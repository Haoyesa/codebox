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

        # 获取互动数据
        result = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var el = document.querySelector(".interaction-container");
    if (!el) return "not found";
    var text = el.innerText;
    var lines = text.split("\n");
    var result = {};
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (line === "赞" && i > 0) result.like = lines[i-1];
        if (line === "收藏" && i > 0) result.collect = lines[i-1];
        if (line === "评论" && i > 0) result.comment = lines[i-1];
    }
    return result;
})
            ''',
            'returnByValue': True
        })
        print('互动数据:', result)

        # 获取评论列表
        result2 = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var el = document.querySelector(".note-scroller");
    if (!el) return "not found";
    var items = el.querySelectorAll("div[class*='comment']");
    var comments = [];
    for (var i = 0; i < items.length; i++) {
        var text = items[i].innerText || "";
        if (text.length > 5) {
            comments.push(text.replace(/\n+/g, " | ").substring(0, 100));
        }
    }
    return comments.slice(0, 15);
})
            ''',
            'returnByValue': True
        })
        print('\n评论列表:')
        if isinstance(result2, list):
            for i, c in enumerate(result2):
                print(f'  [{i+1}] {c}')
        else:
            print(result2)

asyncio.run(main())