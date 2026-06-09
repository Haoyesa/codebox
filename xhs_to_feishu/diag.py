#!/usr/bin/env python
import asyncio, json, sys, io, requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=15)
    http_port = conn.json()['data']['http']
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    print('所有页面:', [(t.get('title'), t.get('url')[:50]) for t in targets if t.get('type') == 'page'])

    target = None
    for t in targets:
        if t.get('type') == 'page' and 'xiaohongshu' in t.get('url', ''):
            target = t
            break
    if not target:
        for t in targets:
            if t.get('type') == 'page':
                target = t
                break

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

        print('导航...')
        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(8)

        r1 = await send('Runtime.evaluate', {
            'expression': 'document.querySelectorAll(".note-item").length',
            'returnByValue': True
        })
        print('note-item:', r1)

        r2 = await send('Runtime.evaluate', {
            'expression': 'document.querySelectorAll("[class*=note]").length',
            'returnByValue': True
        })
        print('class含note:', r2)

        r3 = await send('Runtime.evaluate', {
            'expression': 'document.body.innerText.substring(0, 500)',
            'returnByValue': True
        })
        print('文本:', r3)

        r4 = await send('Runtime.evaluate', {
            'expression': 'document.querySelectorAll("a[href*=explore]").length',
            'returnByValue': True
        })
        print('explore链接:', r4)

asyncio.run(main())