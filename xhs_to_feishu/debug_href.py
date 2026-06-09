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
    target = [t for t in targets if t.get('type') == 'page'][0]
    ws_url = target['webSocketDebuggerUrl']

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
        await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
        await asyncio.sleep(2)

        result = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var anchors = document.querySelectorAll("a");
    var hrefs = [];
    for (var i = 0; i < anchors.length; i++) {
        var href = anchors[i].getAttribute("href") || "";
        if (href && href.indexOf("explore") >= 0) {
            hrefs.push(href);
        }
    }
    return JSON.stringify(hrefs.slice(0, 20));
})()
            ''',
            'returnByValue': True
        })
        print('hrefs:', result)

        # 也看看第一个note-item的title元素
        result2 = await send('Runtime.evaluate', {
            'expression': 'var item = document.querySelector(".note-item"); var title = item ? item.querySelector(".title") : null; return title ? title.innerText : "no title"',
            'returnByValue': True
        })
        print('title:', result2)

asyncio.run(main())