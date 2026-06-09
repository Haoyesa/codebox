#!/usr/bin/env python
import asyncio, json, sys, io, requests, re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    # 先获取现有页面
    print('获取现有页面...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=15)
    http_port = conn.json()['data']['http']
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    page_targets = [t for t in targets if t.get('type') == 'page']
    print('页面数量:', len(page_targets))
    for t in page_targets:
        print(' -', t.get('title', '')[:50])

    # 找到或使用第一个小红书页面
    target = None
    for t in page_targets:
        if 'xiaohongshu' in t.get('url', ''):
            target = t
            break
    if not target and page_targets:
        target = page_targets[0]

    if not target:
        print('未找到页面')
        return

    ws_url = target['webSocketDebuggerUrl']
    print('使用页面:', target.get('title'))

    import websockets
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        # 直接在当前页面导航到搜索
        print('导航到搜索页...')
        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(10)

        # 滚动
        for i in range(3):
            await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
            await asyncio.sleep(2)

        # 获取文本
        r = await send('Runtime.evaluate', {'expression': 'document.documentElement.innerText', 'returnByValue': True})
        text = ''
        if isinstance(r, dict):
            text = r.get('value', '')
        elif isinstance(r, str):
            text = r
        print('文本长度:', len(text))
        if text:
            print('文本前200字:', text[:200])

asyncio.run(main())