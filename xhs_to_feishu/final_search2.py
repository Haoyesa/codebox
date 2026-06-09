#!/usr/bin/env python
import asyncio, json, sys, io, requests, re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=15)
    http_port = conn.json()['data']['http']
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    target = [t for t in targets if t.get('type') == 'page'][0]
    ws_url = target['webSocketDebuggerUrl']

    import websockets
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        print('导航到搜索页...')
        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(8)

        for i in range(3):
            await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
            await asyncio.sleep(2)

        # 从innerHTML提取
        result = await send('Runtime.evaluate', {
            'expression': 'document.body.innerHTML',
            'returnByValue': True
        })

        html = result if isinstance(result, str) else (result.get('value', '') if isinstance(result, dict) else '')
        if isinstance(html, dict): html = html.get('value', '')

        # 提取explore id
        ids = re.findall(r'/explore/([a-f0-9]+)', html)
        # 去重保持顺序
        seen = set()
        unique_ids = []
        for id in ids:
            if id not in seen and len(id) > 10:  # 小红书ID长度通常>10
                seen.add(id)
                unique_ids.append(id)

        print('提取到 {} 个笔记ID'.format(len(unique_ids)))

        # 尝试提取收藏数 - 从页面innerText
        text_result = await send('Runtime.evaluate', {
            'expression': 'document.body.innerText',
            'returnByValue': True
        })
        body_text = text_result if isinstance(text_result, str) else (text_result.get('value', '') if isinstance(text_result, dict) else '')

        print()
        print('| 序号 | 标题 | 链接 | 收藏数 |')
        print('|------|------|------|--------|')
        for i, id in enumerate(unique_ids[:20], 1):
            link = 'https://www.xiaohongshu.com/explore/{}'.format(id)
            print('| {} | （需点击获取） | {} | - |'.format(i, link))

asyncio.run(main())