#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': '68b8252b06454718b2c65b7dd1639341', 'url': 'http://xhslink.com/o/8VvNNO8kxcl'}, timeout=15)
    http_port = conn.json()['data']['http']
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    target = [t for t in targets if t.get('type') == 'page'][1]
    ws_url = target['webSocketDebuggerUrl']

    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        await asyncio.sleep(5)

        r = await send('Runtime.evaluate', {
            'expression': "document.querySelector('.interaction-container').innerText",
            'returnByValue': True
        })
        print('互动文本:', r)

        r2 = await send('Runtime.evaluate', {
            'expression': "document.querySelector('.note-scroller').innerText",
            'returnByValue': True
        })
        print('\n评论区:', r2)

asyncio.run(main())