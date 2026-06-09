#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小红书笔记采集 -> 飞书多维表格
使用 BitBrowser + Chrome DevTools Protocol
"""

import asyncio
import json
import sys
import io
import time
import re
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = "68b8252b06454718b2c65b7dd1639341"
BIT_BROWSER_API_HOST = "127.0.0.1"
BIT_BROWSER_API_PORT = 54345
XHS_SHORT_URL = "http://xhslink.com/o/8VvNNO8kxcl"
CSS_SELECTOR = "#noteContainer > div.video-player-media.media-container > div > div > xg-poster"

import aiohttp
import websockets

WEBSOCKET_PING_INTERVAL = 20
WEBSOCKET_PING_TIMEOUT = 10
WEBSOCKET_CLOSE_TIMEOUT = 10
WEBSOCKET_MAX_SIZE = 10 * 1024 * 1024
COMMAND_TIMEOUT = 30.0

class ChromeDevToolsClient:
    def __init__(self, ws_url=None, http_port=None):
        self.ws_url = ws_url
        self.http_port = http_port
        self.ws = None
        self.connected = False
        self.message_id = 0
        self.pending_messages = {}

    async def connect(self):
        if not self.ws_url:
            raise Exception("WebSocket URL is required")
        self.ws = await websockets.connect(
            self.ws_url,
            ping_interval=WEBSOCKET_PING_INTERVAL,
            ping_timeout=WEBSOCKET_PING_TIMEOUT,
            close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
            max_size=WEBSOCKET_MAX_SIZE
        )
        self.connected = True
        asyncio.create_task(self._handle_incoming_messages())
        return True

    async def _handle_incoming_messages(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                if "id" in data and data["id"] in self.pending_messages:
                    self.pending_messages[data["id"]].set_result(data)
        except Exception as e:
            pass

    async def send_command(self, method, params=None):
        if not self.ws:
            raise Exception("Not connected")
        msg_id = self.message_id
        self.message_id += 1
        future = asyncio.Future()
        self.pending_messages[msg_id] = future
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        try:
            result = await asyncio.wait_for(future, timeout=COMMAND_TIMEOUT)
            del self.pending_messages[msg_id]
            if "error" in result:
                raise Exception(f"CDP Error: {result['error']}")
            return result.get("result", {})
        except asyncio.TimeoutError:
            del self.pending_messages[msg_id]
            raise Exception(f"Command {method} timed out")

    async def navigate(self, url):
        return await self.send_command("Page.navigate", {"url": url})

    async def evaluate(self, script, return_by_value=True):
        result = await self.send_command("Runtime.evaluate", {
            "expression": script,
            "returnByValue": return_by_value
        })
        return result.get("result", {}).get("value")

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            self.connected = False

async def get_bitbrowser_connection(browser_id, api_host, api_port):
    url = f"http://{api_host}:{api_port}/browser/open"
    payload = {"id": browser_id}
    timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success"):
                    return result.get("data", {})
    return None

async def get_page_targets(http_port):
    timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f"http://{http_port}/json") as response:
            if response.status == 200:
                targets = await response.json()
                return [t for t in targets if t.get("type") == "page"]
    return []

async def main():
    print("=" * 60)
    print("小红书笔记采集 -> 飞书多维表格")
    print("=" * 60)

    print("\n[Step 1] 连接 BitBrowser...")
    conn_info = await get_bitbrowser_connection(BIT_BROWSER_ID, BIT_BROWSER_API_HOST, BIT_BROWSER_API_PORT)
    if not conn_info:
        print("❌ 无法获取 BitBrowser 连接信息")
        return

    ws_url = conn_info.get("ws")
    http_port = conn_info.get("http")
    print(f"✅ BitBrowser 连接成功")
    print(f"   HTTP Port: {http_port}")

    print(f"\n[Step 2] 查找可用页面目标...")
    page_targets = await get_page_targets(http_port)
    print(f"   发现 {len(page_targets)} 个页面目标")

    target = None
    for pt in page_targets:
        url = pt.get("url", "")
        title = pt.get("title", "")
        print(f"   - {title}: {url[:60]}...")
        if "xiaohongshu" in url.lower() or "xhs" in url.lower():
            target = pt

    if not target and page_targets:
        target = page_targets[0]

    if not target:
        print("❌ 未找到可用页面目标")
        return

    page_ws_url = target.get("webSocketDebuggerUrl")
    page_title = target.get("title", "未知")
    print(f"   选择: {page_title}")

    print(f"\n[Step 3] 连接到页面...")
    client = ChromeDevToolsClient(ws_url=page_ws_url, http_port=http_port)
    await client.connect()
    print("✅ 已连接 CDP")

    print(f"\n[Step 4] 导航到笔记: {XHS_SHORT_URL}")
    await client.navigate(XHS_SHORT_URL)
    await asyncio.sleep(6)

    title = await client.evaluate("document.title")
    print(f"   页面标题: {title}")

    print("\n[Step 5] 提取页面内容...")

    selectors = [
        "#noteContainer > div.video-player-media.media-container > div > div > xg-poster",
        "#noteContainer .video-player-media xg-poster",
        "#noteContainer > div.video-player-media",
        ".video-poster",
        "xg-poster",
        "[class*='video-player']",
        "#noteContainer",
    ]

    extracted_data = {}
    found_selector = None

    for selector in selectors:
        print(f"   尝试: {selector}")
        script = f"""
        () => {{
            const el = document.querySelector('{selector}');
            if (!el) return null;
            const style = window.getComputedStyle(el);
            return {{
                tagName: el.tagName,
                className: el.className,
                id: el.id,
                outerHTML: el.outerHTML.substring(0, 300),
                bgImage: style.backgroundImage,
                poster: el.getAttribute('poster') || '',
                src: el.src || '',
                html: el.innerHTML.substring(0, 300)
            }};
        }}
        """
        try:
            result = await client.evaluate(script)
            if result:
                print(f"   ✅ 找到元素 ({result.get('tagName')})")
                print(f"   bgImage: {result.get('bgImage', '')[:80]}")
                print(f"   poster: {result.get('poster', '')[:80]}")
                extracted_data[selector] = result
                found_selector = selector
                break
        except Exception as e:
            print(f"   ❌ {e}")

    if not found_selector:
        print("   ❌ 所有选择器都失败")

    print("\n   获取笔记正文...")
    content_script = """
    () => {
        const el = document.querySelector('.note-content, #noteContent, .content, [class*="content"], #detail-desc');
        return el ? el.innerText?.substring(0, 300) : '未找到';
    }
    """
    content = await client.evaluate(content_script)
    print(f"   正文: {content[:100] if content else '未找到'}...")

    print("\n   获取图片...")
    img_script = """
    () => {
        const imgs = document.querySelectorAll('img');
        return Array.from(imgs)
            .filter(img => img.src && (img.src.includes('xiaohongshu') || img.src.includes('rednotecdn')))
            .slice(0, 10)
            .map(img => img.src);
    }
    """
    images = await client.evaluate(img_script)
    print(f"   找到 {len(images) if images else 0} 张图片")
    if images:
        for i, img in enumerate(images[:3]):
            print(f"   [{i}] {img[:80]}...")

    print("\n   获取视频...")
    video_script = """
    () => {
        const videos = document.querySelectorAll('video');
        return Array.from(videos).map(v => ({
            src: v.src || v.currentSrc || '',
            poster: v.poster || '',
            currentSrc: v.currentSrc || ''
        })).filter(v => v.src || v.currentSrc);
    }
    """
    videos = await client.evaluate(video_script)
    print(f"   找到 {len(videos) if videos else 0} 个视频")

    print("\n[Step 6] 视频URL分析...")
    sample_video = None
    if videos:
        for v in videos:
            if v.get('src'):
                sample_video = v['src']
                break
        if not sample_video:
            for v in videos:
                if v.get('currentSrc'):
                    sample_video = v['currentSrc']
                    break

    if sample_video:
        print(f"   URL: {sample_video}")
        parsed = urlparse(sample_video)
        print(f"   协议: {parsed.scheme}")
        print(f"   域名: {parsed.netloc}")
        print(f"   路径: {parsed.path}")
        path_parts = parsed.path.split('/')
        print(f"   路径段: {path_parts}")
        m = re.search(r'/(\d+)/(\d+)/([^/]+)_(\d+)\.mp4', sample_video)
        if m:
            print(f"   模式: stream_id={m.group(1)}, sub_id={m.group(2)}, hash={m.group(3)}, seq={m.group(4)}")

    await client.disconnect()
    print("\n" + "=" * 60)
    print("采集完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())