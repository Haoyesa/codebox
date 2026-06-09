#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BitBrowser API 客户端
通过 CDP 协议控制已打开的浏览器
"""

import requests
import json
import time
import websocket
from typing import Optional, Dict, Any, List


class BitBrowserClient:
    """BitBrowser API 封装"""

    def __init__(self, browser_id: str, api_base: str = "http://127.0.0.1:54345"):
        self.browser_id = browser_id
        self.api_base = api_base
        self.ws_url: Optional[str] = None
        self.http_port: Optional[str] = None
        self.seq: Optional[int] = None
        self.driver: Optional[str] = None
        self._ws: Optional[websocket.WebSocket] = None
        self._message_id = 0
        self._callbacks: Dict[int, tuple] = {}

    def open(self, url: str) -> Dict[str, Any]:
        """
        在浏览器中打开URL，返回连接信息
        """
        response = requests.post(
            f"{self.api_base}/browser/open",
            json={"id": self.browser_id, "url": url},
            timeout=30
        )
        data = response.json()
        if not data.get("success"):
            raise Exception(f"打开浏览器失败: {data.get('msg')}")

        info = data["data"]
        self.ws_url = info["ws"]
        self.http_port = info["http"]
        self.seq = info["seq"]
        self.driver = info.get("driver")
        return info

    def close(self) -> None:
        """关闭WebSocket连接"""
        if self._ws:
            try:
                self._ws.close()
            except:
                pass
            self._ws = None

    def _send(self, method: str, params: Dict = None) -> Dict:
        """通过CDP发送命令"""
        if not self._ws:
            self._connect()

        msg_id = self._message_id
        self._message_id += 1

        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params

        self._ws.send(json.dumps(payload))

        # 等待响应
        while True:
            try:
                response = self._ws.recv()
                data = json.loads(response)

                # 处理事件消息（如 Runtime.consoleAPICalled）
                if "method" in data and "id" not in data:
                    continue

                if data.get("id") == msg_id:
                    if data.get("error"):
                        raise Exception(f"CDP错误: {data['error']}")
                    return data
            except websocket.WebSocketTimeoutException:
                raise Exception("CDP命令超时")
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if "CDP" in str(e):
                    raise
                continue

    def _get_page_ws_url(self) -> Optional[str]:
        """从DevTools API获取当前页面的WebSocket URL"""
        try:
            response = requests.get(f"http://{self.http_port}/json", timeout=5)
            pages = response.json()
            # 找到小红书相关的页面
            for page in pages:
                if "xiaohongshu" in page.get("url", "") or "xhs" in page.get("url", "").lower():
                    return page.get("webSocketDebuggerUrl")
            # 返回第一个页面
            if pages:
                return pages[0].get("webSocketDebuggerUrl")
        except:
            pass
        return None

    def _connect(self) -> None:
        """建立WebSocket连接"""
        if not self.ws_url:
            # 尝试获取页面级WebSocket URL
            page_ws_url = self._get_page_ws_url()
            if page_ws_url:
                self.ws_url = page_ws_url
            else:
                raise Exception("未调用open方法或无法获取页面WebSocket URL")

        self._ws = websocket.WebSocket()
        self._ws.settimeout(30)
        # 添加origin头避免403
        self._ws.connect(self.ws_url, origin=f"http://127.0.0.1:{self.http_port}")

    def navigate(self, url: str) -> None:
        """导航到URL"""
        # 先关闭当前页面
        try:
            self.close()
        except:
            pass

        # 重新打开并导航
        self.open(url)

    def get_cookies(self, urls: List[str] = None) -> List[Dict]:
        """获取cookies"""
        if urls is None:
            urls = ["https://www.xiaohongshu.com"]
        return self._send("Network.getAllCookies", {}) \
            .get("result", {}).get("cookies", [])

    def evaluate(self, script: str) -> Any:
        """在页面中执行JavaScript"""
        result = self._send("Page.evaluate", {
            "expression": script,
            "returnByValue": True
        })
        return result.get("result", {}).get("result", {}).get("value")

    def get_page_content(self) -> str:
        """获取页面HTML"""
        return self.evaluate("document.documentElement.outerHTML")

    def get_page_text(self) -> str:
        """获取页面文本内容"""
        return self.evaluate("document.body.innerText")

    def scroll_down(self, pixels: int = 800) -> None:
        """向下滚动"""
        self.evaluate(f"window.scrollBy(0, {pixels})")

    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """等待元素出现"""
        start = time.time()
        while time.time() - start < timeout / 1000:
            found = self.evaluate(
                f"document.querySelector('{selector}') !== null"
            )
            if found:
                return True
            time.sleep(0.5)
        return False

    def query_selector_all(self, selector: str) -> List:
        """查询所有匹配元素"""
        script = f'''
        Array.from(document.querySelectorAll('{selector}')).map(el => {{
            return {{
                tag: el.tagName,
                text: el.innerText?.substring(0, 200),
                href: el.href || el.src || '',
                rect: el.getBoundingClientRect() ? {{
                    x: el.getBoundingClientRect().x,
                    y: el.getBoundingClientRect().y,
                    width: el.getBoundingClientRect().width,
                    height: el.getBoundingClientRect().height
                }} : null
            }};
        }})
        '''
        return self.evaluate(script)

    def get_window_size(self) -> Dict:
        """获取视口大小"""
        return self.evaluate("""
            ({width: window.innerWidth, height: window.innerHeight})
        """)


def collect_xhs_notes(keyword: str, browser_id: str, limit: int = 20) -> List[Dict]:
    """
    从小红书搜索页面采集笔记数据
    """
    from urllib.parse import quote

    search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&type=51"

    client = BitBrowserClient(browser_id)
    client.open(search_url)

    # 等待页面加载
    time.sleep(5)

    # 滚动加载更多内容
    for _ in range(5):
        client.scroll_down(1000)
        time.sleep(1.5)

    # 提取页面数据
    notes = client.evaluate("""
    () => {
        // 尝试从页面提取笔记数据
        // XHS搜索结果页的数据可能在多个位置

        // 方法1: 从 __INITIAL_SSR_STATE__
        // 方法2: 从 script 标签中的 JSON
        // 方法3: 从 DOM 结构

        // 这里返回页面中所有链接的文本，用于调试
        const results = [];
        const cards = document.querySelectorAll('.note-item, .search-card, [class*="note"], [class*="card"]');

        cards.forEach((card, i) => {
            const titleEl = card.querySelector('.title, [class*="title"], h2, h3, a');
            const metaEl = card.querySelector('.meta, [class*="meta"], [class*="info"]');
            const linkEl = card.querySelector('a[href*="/discovery/item/"]');

            if (titleEl) {
                results.push({
                    index: i,
                    title: titleEl.innerText?.substring(0, 100),
                    meta: metaEl?.innerText?.substring(0, 100),
                    link: linkEl?.href || ''
                });
            }
        });

        // 如果没找到卡片，返回页面中包含"小红书"或链接的文本片段
        if (results.length === 0) {
            const scripts = document.querySelectorAll('script[type="application/json"]');
            const data = [];
            scripts.forEach(s => {
                try {
                    const json = JSON.parse(s.textContent);
                    data.push(json);
                } catch(e) {}
            });
            return {method: 'script', count: scripts.length, dataPreview: JSON.stringify(data).substring(0, 500)};
        }

        return {method: 'card', count: results.length, results: results.slice(0, 20)};
    }
    """)

    client.close()
    return notes


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python bitbrowser_client.py <browser_id> <keyword>")
        sys.exit(1)

    browser_id = sys.argv[1]
    keyword = sys.argv[2]

    print(f"正在采集「{keyword}」...")
    result = collect_xhs_notes(keyword, browser_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))