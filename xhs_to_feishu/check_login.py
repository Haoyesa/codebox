#!/usr/bin/env python
import asyncio, json, sys, io, requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID, 'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'}, timeout=15)
    http_port = conn.json()['data']['http']
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    target = None
    for t in targets:
        if t.get('type') == 'page' and 'xiaohongshu' in t.get('url', ''):
            target = t
            break
    if not target:
        target = [t for t in targets if t.get('type') == 'page'][1]

    ws_url = target['webSocketDebuggerUrl']
    print(f'页面: {target["title"]}')

    import websockets
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        await asyncio.sleep(5)

        url_now = await send('Runtime.evaluate', {'expression': 'window.location.href', 'returnByValue': True})
        print(f'当前URL: {url_now}')

        title = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        print(f'标题: {title}')

        body = await send('Runtime.evaluate', {
            'expression': 'document.body.innerText.substring(0, 300)',
            'returnByValue': True
        })
        print(f'页面内容: {body}')

asyncio.run(main())