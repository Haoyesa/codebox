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

        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(8)
        for i in range(3):
            await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
            await asyncio.sleep(2)

        result = await send('Runtime.evaluate', {
            'expression': 'document.body.innerHTML',
            'returnByValue': True
        })

        print('result type:', type(result))
        print('result:', str(result)[:200])

        if isinstance(result, dict):
            val = result.get('value', '')
            print('value type:', type(val))
            print('value len:', len(val) if val else 0)
            # 查找explore链接
            ids = re.findall(r'/explore/([a-f0-9]{10,})', val)
            print('ids:', ids[:10])

asyncio.run(main())