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
    page_targets = [t for t in targets if t.get('type') == 'page']
    target = page_targets[1]
    ws_url = target['webSocketDebuggerUrl']

    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        msg_id = [0]
        async def send(method, params=None):
            msg_id[0] += 1
            mid = msg_id[0]
            await ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
            async for msg in ws:
                data = json.loads(msg)
                if data.get('id') == mid:
                    return data.get('result', {})

        await asyncio.sleep(5)

        result = await send('Runtime.evaluate', {
            'expression': 'document.getElementById("noteContainer") ? document.getElementById("noteContainer").innerHTML.substring(0, 300) : "not found"',
            'returnByValue': True
        })
        print('noteContainer:', result)

        result2 = await send('Runtime.evaluate', {
            'expression': 'document.querySelector(".interaction-container") ? document.querySelector(".interaction-container").innerText.substring(0, 200) : "not found"',
            'returnByValue': True
        })
        print('interaction-container:', result2)

        result3 = await send('Runtime.evaluate', {
            'expression': 'document.body.innerText.match(/\\d+\\s*(赞|收藏|评论)/g) ? document.body.innerText.match(/\\d+\\s*(赞|收藏|评论)/g).slice(0, 5) : "no match"',
            'returnByValue': True
        })
        print('匹配:', result3)

asyncio.run(main())