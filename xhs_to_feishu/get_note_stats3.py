#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

XHS_NOTE_URL = 'http://xhslink.com/o/8VvNNO8kxcl'
BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    print('连接 BitBrowser...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID, 'url': XHS_NOTE_URL}, timeout=15)
    conn_info = conn.json().get('data', {})
    http_port = conn_info.get('http')
    print(f'HTTP: {http_port}')

    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    page_targets = [t for t in targets if t.get('type') == 'page']

    target = None
    for t in page_targets:
        url = t.get('url', '')
        if 'xiaohongshu' in url and 'explore' in url:
            target = t
            break

    if not target and page_targets:
        target = page_targets[0]

    ws_url = target['webSocketDebuggerUrl']
    print(f'使用页面: {target["title"]}')

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
        title = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        print(f'标题: {title}')

        url_now = await send('Runtime.evaluate', {'expression': 'window.location.href', 'returnByValue': True})
        print(f'当前URL: {url_now}')

        # 提取点赞/收藏/评论
        result1 = await send('Runtime.evaluate', {
            'expression': '''
            (function() {
                var sel = "#noteContainer > div.interaction-container > div.interactions.engage-bar > div > div > div.input-box > div.interact-container > div > div.left";
                var el = document.querySelector(sel);
                if (el) {
                    return el.innerText;
                }
                return "未找到";
            })
            ''',
            'returnByValue': True
        })
        print(f'互动栏: {result1}')

        # 找评论
        result2 = await send('Runtime.evaluate', {
            'expression': '''
            (function() {
                var sel = "#noteContainer > div.interaction-container > div.note-scroller > div.comments-el";
                var el = document.querySelector(sel);
                if (el) {
                    return el.innerText.substring(0, 500);
                }
                return "未找到";
            })
            ''',
            'returnByValue': True
        })
        print(f'评论区: {result2}')

        # 如果上面的选择器找不到，尝试通用方法
        if result1 == "未找到" or result1 == "function () {[native code]}":
            print('\n尝试备用方法...')
            result3 = await send('Runtime.evaluate', {
                'expression': '''
                (function() {
                    var text = document.body.innerText;
                    var match = text.match(/(\\d+)\\s*赞/) || text.match(/(\\d+\\.?\\d*\\w*)\\s*赞/);
                    var match2 = text.match(/(\\d+)\\s*收藏/) || text.match(/(\\d+\\.?\\d*\\w*)\\s*收藏/);
                    var match3 = text.match(/(\\d+)\\s*评论/) || text.match(/(\\d+\\.?\\d*\\w*)\\s*评论/);
                    return {
                        like: match ? match[0] : "未找到",
                        collect: match2 ? match2[0] : "未找到",
                        comment: match3 ? match3[0] : "未找到"
                    };
                })
                ''',
                'returnByValue': True
            })
            print(f'备用数据: {result3}')

asyncio.run(main())