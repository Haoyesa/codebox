#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

XHS_PROFILE_URL = 'https://www.xiaohongshu.com/user/profile/68ed8d9f000000003702f0db'
BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    print('连接 BitBrowser...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=10)
    conn_info = conn.json()['data']
    http_port = conn_info['http']

    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    page_targets = [t for t in targets if t.get('type') == 'page']

    target = None
    for t in page_targets:
        if 'xiaohongshu' in t.get('url', ''):
            target = t
            break
    if not target:
        target = page_targets[0]

    ws_url = target['webSocketDebuggerUrl']
    print(f'目标: {target["title"]}')

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

        print(f'导航到: {XHS_PROFILE_URL}')
        await send('Page.navigate', {'url': XHS_PROFILE_URL})
        await asyncio.sleep(5)

        title = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        print(f'标题: {title}')

        # 提取数据
        result = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const selector = '#userPageContainer > div.user > div > div.info-part > div.info > div.data-info > div';
                const el = document.querySelector(selector);
                if (!el) return '未找到元素';
                return {
                    html: el.innerHTML.substring(0, 500),
                    text: el.innerText,
                    children: el.children.length
                };
            })()
            ''',
            'returnByValue': True
        })
        print(f'主选择器结果: {result}')

        # 备用
        result2 = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const els = document.querySelectorAll('div[class*="data-info"]');
                return Array.from(els).map(el => el.innerText.substring(0, 100));
            })()
            ''',
            'returnByValue': True
        })
        print(f'备用(data-info): {result2}')

        # 找数字
        result3 = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                // 找关注、粉丝、赞藏相关的数字
                const allText = document.body.innerText;
                const matches = allText.match(/关注[\\s\\S]{0,20}\\d+/g) || [];
                const matches2 = allText.match(/粉丝[\\s\\S]{0,20}\\d+/g) || [];
                const matches3 = allText.match(/赞藏[\\s\\S]{0,20}\\d+/g) || [];
                return {
                    follow: matches.slice(0, 3),
                    fans: matches2.slice(0, 3),
                    like: matches3.slice(0, 3)
                };
            })()
            ''',
            'returnByValue': True
        })
        print(f'关键词匹配: {result3}')

asyncio.run(main())