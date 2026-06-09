#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = "68b8252b06454718b2c65b7dd1639341"
XHS_SHORT_URL = "http://xhslink.com/o/8VvNNO8kxcl"

async def main():
    print("连接 BitBrowser...")
    conn_resp = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=10)
    conn_info = conn_resp.json()['data']
    http_port = conn_info['http']
    print(f"HTTP Port: {http_port}")

    targets_resp = requests.get(f'http://{http_port}/json', timeout=10)
    targets = targets_resp.json()
    page_targets = [t for t in targets if t.get('type') == 'page']

    # 选择小红书创作服务平台
    target = None
    for t in page_targets:
        if 'creator.xiaohongshu' in t.get('url', ''):
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

        # 导航到笔记
        print(f'导航到: {XHS_SHORT_URL}')
        await send('Page.navigate', {'url': XHS_SHORT_URL})
        await asyncio.sleep(5)

        title = await send('Runtime.evaluate', {
            'expression': 'document.title',
            'returnByValue': True
        })
        print(f'标题: {title}')

        # 提取所有内容
        result = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                const imgs = Array.from(document.querySelectorAll('img'))
                    .map(img => img.src)
                    .filter(src => src && (src.includes('xiaohongshu') || src.includes('rednote') || src.includes('sns')));
                const videos = Array.from(document.querySelectorAll('video'))
                    .map(v => ({src: v.src || v.currentSrc, poster: v.poster}));
                const content = document.querySelector('#detail-desc, .detail-desc, [class*="desc"], .note-content');
                const links = Array.from(document.querySelectorAll('a[href*="xhslink"]')).map(a => a.href);
                return {
                    imgCount: imgs.length,
                    videoCount: videos.length,
                    links: links.slice(0, 5),
                    sampleImgs: imgs.slice(0, 5),
                    sampleVideos: videos.slice(0, 3),
                    contentText: content ? content.innerText : '未找到',
                    htmlLength: document.body.innerHTML.length
                };
            })()
            ''',
            'returnByValue': True
        })

        data = result.get('result', {}).get('value', {})
        print(f'\n图片数量: {data.get("imgCount", 0)}')
        print(f'视频数量: {data.get("videoCount", 0)}')
        print(f'正文: {data.get("contentText", "未找到")}')
        print(f'HTML长度: {data.get("htmlLength", 0)}')

        print('\n图片:')
        for img in data.get('sampleImgs', []):
            print(f'  {img[:100]}')

        print('\n视频:')
        for v in data.get('sampleVideos', []):
            print(f'  src: {v.get("src", "")[:100]}')
            print(f'  poster: {v.get("poster", "")[:100]}')

if __name__ == "__main__":
    asyncio.run(main())