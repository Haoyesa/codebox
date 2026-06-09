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
    target = [t for t in targets if t.get('type') == 'page'][1]
    ws_url = target['webSocketDebuggerUrl']

    import websockets
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(6)

        # 滚动页面
        await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
        await asyncio.sleep(2)

        # 检查页面元素
        result = await send('Runtime.evaluate', {
            'expression': '''
            (function() {
                var body = document.body.innerText;
                return body.substring(0, 500);
            })
            ''',
            'returnByValue': True
        })
        print('页面文本片段:', str(result)[:300])

        # 获取搜索结果数量
        result2 = await send('Runtime.evaluate', {
            'expression': '''
            (function() {
                var all = document.querySelectorAll("a[href*='/explore/']");
                return all.length;
            })
            ''',
            'returnByValue': True
        })
        print('explore链接数量:', result2)

asyncio.run(main())