#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

XHS_NOTE_URL = 'https://www.xiaohongshu.com/explore/6a12a56400000000380352d8'
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

        print(f'导航到: {XHS_NOTE_URL}')
        await send('Page.navigate', {'url': XHS_NOTE_URL})
        await asyncio.sleep(5)

        title = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        print(f'标题: {title}')

        # 1. 点赞/收藏/评论数
        print('\n[1] 点赞/收藏/评论数')
        result1 = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const selector = '#noteContainer > div.interaction-container > div.interactions.engage-bar > div > div > div.input-box > div.interact-container > div > div.left';
                const el = document.querySelector(selector);
                if (!el) return '未找到';
                return {
                    html: el.innerHTML.substring(0, 500),
                    text: el.innerText,
                    children: el.children.length
                };
            })()
            ''',
            'returnByValue': True
        })
        print(f'结果: {result1}')

        # 2. 评论列表
        print('\n[2] 评论列表')
        result2 = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const selector = '#noteContainer > div.interaction-container > div.note-scroller > div.comments-el';
                const el = document.querySelector(selector);
                if (!el) return '未找到元素';

                const comments = [];
                const items = el.querySelectorAll('.comment-item, .user-comment, [class*="comment"]');
                for (const item of items) {
                    const user = item.querySelector('.user-name, .nickname, [class*="name"]');
                    const content = item.querySelector('.content, .comment-content, [class*="content"]');
                    const time = item.querySelector('.time, [class*="time"]');
                    if (content) {
                        comments.push({
                            user: user ? user.innerText : '',
                            content: content.innerText.substring(0, 100),
                            time: time ? time.innerText : ''
                        });
                    }
                }

                if (comments.length === 0) {
                    // 尝试其他方式找评论
                    const allDivs = el.querySelectorAll('div');
                    return {
                        totalDivs: allDivs.length,
                        text: el.innerText.substring(0, 300)
                    };
                }
                return comments.slice(0, 20);
            })()
            ''',
            'returnByValue': True
        })
        print(f'评论: {result2}')

        # 备用 - 直接获取页面文本中的数字
        result3 = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const text = document.body.innerText;
                const likeMatch = text.match(/(\\d+\\.?\\d*\\w*)\\s*赞/);
                const collectMatch = text.match(/(\\d+\\.?\\d*\\w*)\\s*收藏/);
                const commentMatch = text.match(/(\\d+\\.?\\d*\\w*)\\s*评论/);
                return {
                    like: likeMatch ? likeMatch[0] : '未找到',
                    collect: collectMatch ? collectMatch[0] : '未找到',
                    comment: commentMatch ? commentMatch[0] : '未找到'
                };
            })()
            ''',
            'returnByValue': True
        })
        print(f'关键词匹配: {result3}')

asyncio.run(main())