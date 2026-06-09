#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小红书爆款笔记采集 → 飞书多维表格
手动触发版：输入关键词，采集前20篇笔记
"""

import json
import re
import sys
import time
from typing import List, Dict, Optional

import requests

# 尝试导入本地配置
try:
    from config import FEISHU_APP_TOKEN, FEISHU_TABLE_ID, FEISHU_ACCESS_TOKEN
except ImportError:
    print("错误: 请先复制 config.example.py 为 config.py 并填入飞书配置")
    sys.exit(1)

from feishu_client import FeishuClient


def search_xhs(keyword: str, limit: int = 20) -> List[Dict]:
    """
    通过 BitBrowser 或直接 HTTP 访问小红书搜索
    返回笔记列表
    """
    print(f"正在搜索小红书...")

    # 方式1: 使用 BitBrowser API (如果可用)
    try:
        return fetch_via_bitbrowser(keyword, limit)
    except Exception as e:
        print(f"  BitBrowser 方式失败: {e}")

    # 方式2: 直接请求小红书搜索 API
    try:
        return fetch_via_api(keyword, limit)
    except Exception as e:
        print(f"  API 方式失败: {e}")

    print("错误: 无法连接小红书数据源，请确认 BitBrowser 已启动")
    return []


def fetch_via_api(keyword: str, limit: int) -> List[Dict]:
    """
    直接调用小红书搜索 API
    小红书移动端 API 比较稳定
    """
    import urllib.parse

    # 小红书搜索 API
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.xiaohongshu.com/",
        "X-Requested-With": "XMLHttpRequest",
    }

    params = {
        "keyword": keyword,
        "page": 1,
        "page_size": limit,
        "search_note_source": "normal_search",
        "sort": "general",
        "note_type": 0,
    }

    session = requests.Session()
    session.headers.update(headers)

    response = session.get(url, params=params, timeout=15)
    print(f"  API 响应状态: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"API 返回非 200 状态: {response.status_code}")

    data = response.json()

    if data.get("code") != 0:
        raise Exception(f"API 返回错误: {data.get("msg", data)}")

    items = data.get("data", {}).get("items", [])
    notes = []

    for item in items:
        note_card = item.get("note_card", {})
        note_id = note_card.get("note_id", "")
        interact_info = note_card.get("interact_info", {})

        def parse_num(val):
            if isinstance(val, (int, float)):
                return int(val)
            if isinstance(val, str):
                val = val.strip()
                if not val:
                    return 0
                if "万" in val:
                    return int(float(val.replace("万", "")) * 10000)
                try:
                    return int(float(val))
                except:
                    return 0
            return 0

        notes.append({
            "id": note_id,
            "title": note_card.get("display_title", ""),
            "link": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
            "likes": parse_num(interact_info.get("liked_count")),
            "collects": parse_num(interact_info.get("collected_count")),
            "comments": parse_num(interact_info.get("comment_count")),
            "time": note_card.get("time", ""),
        })

    return notes


def fetch_via_bitbrowser(keyword: str, limit: int) -> List[Dict]:
    """
    通过 BitBrowser 自动化浏览器访问小红书
    需要 BitBrowser 运行并开启 API
    """
    import time

    # 创建浏览器上下文
    browser_id = create_browser()
    if not browser_id:
        raise Exception("无法创建浏览器实例")

    try:
        # 打开小红书搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={requests.utils.quote(keyword)}&source=web_search_result_notes"
        open_result = open_browser_tab(browser_id, search_url)
        if not open_result:
            raise Exception("无法打开页面")

        # 等待页面加载
        time.sleep(3)

        # 滚动页面触发懒加载，收集笔记数据
        notes = []
        scroll_count = 0
        max_scrolls = 10

        while len(notes) < limit and scroll_count < max_scrolls:
            # 提取页面上的笔记数据
            script = """
            () => {
                const notes = window.__INITIAL_SSR_STATE__?.note?.noteListMap?.default;
                if (notes) {
                    return Object.values(notes).map(n => ({
                        id: n.id,
                        title: n.title,
                        likes: n.interactInfo?.likedCount || 0,
                        collects: n.interactInfo?.collectedCount || 0,
                        comments: n.interactInfo?.commentCount || 0,
                        time: n.time || '',
                        link: 'https://www.xiaohongshu.com/discovery/item/' + n.id
                    }));
                }
                return [];
            }
            """
            # 这个脚本提取逻辑可能需要根据实际页面调整

            scroll_down(browser_id)
            time.sleep(1.5)
            scroll_count += 1

        # 返回收集到的笔记
        return notes[:limit]

    finally:
        close_browser(browser_id)


# BitBrowser API 封装
def create_browser() -> Optional[str]:
    """创建浏览器实例"""
    try:
        response = requests.post(
            "http://127.0.0.1:54345/api/browser/create",
            json={"type": "chrome"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("data", {}).get("browserId")
    except:
        pass
    return None


def open_browser_tab(browser_id: str, url: str) -> bool:
    """在浏览器中打开标签页"""
    try:
        response = requests.get(
            f"http://127.0.0.1:54345/api/browser/open",
            params={"browserId": browser_id, "url": url},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False


def scroll_down(browser_id: str) -> None:
    """滚动浏览器页面"""
    try:
        requests.post(
            f"http://127.0.0.1:54345/api/browser/scroll",
            json={"browserId": browser_id, "direction": "down"},
            timeout=5
        )
    except:
        pass


def close_browser(browser_id: str) -> None:
    """关闭浏览器"""
    try:
        requests.delete(f"http://127.0.0.1:54345/api/browser/close/{browser_id}", timeout=5)
    except:
        pass


def normalize_note(note: Dict) -> Dict:
    """标准化笔记数据"""
    # 提取数字（可能带 "万" 或 "点赞" 等文字）
    def parse_count(val):
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            val = val.strip()
            if "万" in val:
                return int(float(val.replace("万", "")) * 10000)
            match = re.search(r"[\d.]+", val)
            if match:
                return int(float(match.group()))
        return 0

    return {
        "title": note.get("title", ""),
        "link": note.get("link", ""),
        "likes": parse_count(note.get("likes", 0)),
        "collects": parse_count(note.get("collects", 0)),
        "comments": parse_count(note.get("comments", 0)),
        "time": note.get("time", ""),
    }


def write_to_feishu(notes: List[Dict], keyword: str) -> int:
    """写入飞书多维表格"""
    client = FeishuClient(FEISHU_APP_TOKEN, FEISHU_TABLE_ID,
                          app_id=FEISHU_APP_ID, app_secret=FEISHU_APP_SECRET)

    # 确保必要字段存在
    required_fields = ["标题", "链接", "点赞", "收藏", "评论", "发布时间", "关键词"]
    client.ensure_fields(required_fields)

    # 构造记录
    records = []
    for note in notes:
        normalized = normalize_note(note)
        records.append({
            "fields": {
                "标题": normalized["title"],
                "链接": normalized["link"],
                "点赞": normalized["likes"],
                "收藏": normalized["collects"],
                "评论": normalized["comments"],
                "发布时间": normalized["time"],
                "关键词": keyword,
            }
        })

    # 批量写入
    if records:
        result = client.batch_create_records(records)
        created = len(result.get("data", {}).get("records", []))
        return created
    return 0


def main():
    print("=" * 50)
    print("小红书爆款笔记采集器")
    print("=" * 50)

    # 输入关键词
    keyword = input("\n请输入搜索关键词: ").strip()
    if not keyword:
        print("关键词不能为空")
        sys.exit(1)

    print(f"\n开始采集关键词「{keyword}」的笔记...")

    # 采集笔记
    notes = search_xhs(keyword, limit=20)

    if not notes:
        print("未采集到任何笔记")
        sys.exit(1)

    print(f"采集到 {len(notes)} 篇笔记")

    # 写入飞书
    print("\n正在写入飞书多维表格...")
    try:
        created = write_to_feishu(notes, keyword)
        print(f"成功写入 {created} 条记录到飞书")
    except Exception as e:
        print(f"写入飞书失败: {e}")
        sys.exit(1)

    print("\n完成!")


if __name__ == "__main__":
    main()