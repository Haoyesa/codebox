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

        print('导航到搜索页...')
        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'})
        await asyncio.sleep(8)

        for i in range(3):
            await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
            await asyncio.sleep(2)

        result = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var results = [];
    var items = document.querySelectorAll(".note-item");
    items.forEach(function(item) {
        var titleEl = item.querySelector(".title, .note-title");
        var title = titleEl ? titleEl.innerText : "";
        var collect = 0;
        var spans = item.querySelectorAll("span");
        for (var i = 0; i < spans.length; i++) {
            if (spans[i].innerText.indexOf("收藏") >= 0) {
                var prev = spans[i - 1];
                if (prev) {
                    var txt = prev.innerText.replace(/[^0-9]/g, "");
                    collect = parseInt(txt) || 0;
                }
                break;
            }
        }
        var anchors = item.querySelectorAll("a");
        for (var i = 0; i < anchors.length; i++) {
            var href = anchors[i].getAttribute("href") || "";
            if (href.indexOf("/explore/") >= 0) {
                var m = href.match(/\/explore\/([a-f0-9]+)/);
                if (m) {
                    results.push({
                        id: m[1],
                        title: title || "（无标题）",
                        collect: collect
                    });
                    break;
                }
            }
        }
    });
    return JSON.stringify(results);
})()
            ''',
            'returnByValue': True
        })

        try:
            feeds = json.loads(result) if isinstance(result, str) else []
            if isinstance(feeds, dict): feeds = feeds.get('value', [])
        except: feeds = []
        print('找到 {} 条'.format(len(feeds)))

        seen = set()
        unique = []
        for f in feeds:
            if f.get('id') and f['id'] not in seen:
                seen.add(f['id'])
                unique.append(f)
        unique.sort(key=lambda x: x.get('collect', 0), reverse=True)

        print()
        print('| 序号 | 标题 | 链接 | 收藏数 |')
        print('|------|------|------|--------|')
        for i, f in enumerate(unique[:20], 1):
            title = f.get('title', '')[:40]
            link = 'https://www.xiaohongshu.com/explore/{}'.format(f['id'])
            collect = f.get('collect', 0)
            print('| {} | {} | {} | {} |'.format(i, title, link, collect))

asyncio.run(main())