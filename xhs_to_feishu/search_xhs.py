#!/usr/bin/env python
import asyncio, json, sys, io, requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'
KEYWORD = '副业'

async def main():
    print('连接 BitBrowser...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=15)
    http_port = conn.json()['data']['http']

    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    target = [t for t in targets if t.get('type') == 'page'][1]
    ws_url = target['webSocketDebuggerUrl']
    print(f'使用页面: {target["title"]}')

    import websockets
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

        # 1. 打开小红书首页
        print('打开小红书首页...')
        await send('Page.navigate', {'url': 'https://www.xiaohongshu.com'})
        await asyncio.sleep(3)

        # 2. 在搜索框输入关键词
        print(f'搜索关键词: {KEYWORD}')
        search_script = '''
        (function() {
            var searchInput = document.querySelector('input[class*="search"] input, input[placeholder*="搜索"]');
            if (!searchInput) {
                searchInput = document.querySelector('header input, .search-input input');
            }
            if (searchInput) {
                searchInput.focus();
                searchInput.value = '副业';
                searchInput.dispatchEvent(new Event('input'));
                return 'found input';
            }
            return 'input not found';
        })
        '''
        result = await send('Runtime.evaluate', {'expression': search_script, 'returnByValue': True})
        print(f'输入框定位: {result}')

        await asyncio.sleep(1)

        # 按回车搜索
        await send('Runtime.evaluate', {'expression': '''
        (function() {
            var searchInput = document.querySelector('input[class*="search"], input[placeholder*="搜索"]');
            if (searchInput) {
                var event = new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13});
                searchInput.dispatchEvent(event);
                return 'pressed Enter';
            }
            return 'not found';
        })
        ''', 'returnByValue': True})
        await asyncio.sleep(5)

        title = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        print(f'页面标题: {title}')

        # 3. 提取搜索结果
        result = await send('Runtime.evaluate', {
            'expression': '''
            (function() {
                var results = [];
                var cards = document.querySelectorAll('.note-item, .search-card, [class*="note-card"], [class*="feeds"] > div');
                cards.forEach(function(card) {
                    var link = card.querySelector('a[href*="/explore/"]');
                    var title = card.querySelector('.title, .note-title, [class*="title"]');
                    var collectEl = card.querySelector('.count, [class*="collect"]');
                    if (link) {
                        var href = link.href || link.getAttribute('href');
                        var id = href.match(/\\/explore\\/([a-f0-9]+)/);
                        if (id) {
                            results.push({
                                id: id[1],
                                title: title ? title.innerText.substring(0, 50) : '（无标题）',
                                collectCount: collectEl ? parseInt(collectEl.innerText.replace(/\\D/g, '')) || 0 : 0
                            });
                        }
                    }
                });
                return JSON.stringify(results.slice(0, 30));
            })()
            ''',
            'returnByValue': True
        })

        try:
            feeds = json.loads(result) if isinstance(result, str) else result
            if isinstance(feeds, dict):
                feeds = feeds.get('value', [])
            if isinstance(feeds, str):
                feeds = json.loads(feeds)
        except:
            feeds = []

        print(f'找到 {len(feeds)} 条结果')

        # 去重并排序
        seen = set()
        unique_feeds = []
        for feed in feeds:
            if feed.get('id') and feed['id'] not in seen:
                seen.add(feed['id'])
                unique_feeds.append(feed)

        unique_feeds.sort(key=lambda x: x.get('collectCount', 0), reverse=True)

        print(f'去重后 {len(unique_feeds)} 条')
        print()
        print('| 序号 | 标题 | 链接 | 收藏数 |')
        print('|------|------|------|--------|')
        for i, feed in enumerate(unique_feeds[:20], 1):
            link = f"https://www.xiaohongshu.com/explore/{feed['id']}"
            title = feed.get('title', '（无标题）')[:40]
            collect = feed.get('collectCount', 0)
            print(f'| {i} | {title} | {link} | {collect} |')

asyncio.run(main())