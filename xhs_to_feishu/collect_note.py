#!/usr/bin/env python
import asyncio, json, sys, io
import requests
import websockets
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = "68b8252b06454718b2c65b7dd1639341"
XHS_SHORT_URL = "http://xhslink.com/o/8VvNNO8kxcl"

async def main():
    print("=" * 60)
    print("小红书笔记采集")
    print("=" * 60)

    print("\n[1] 连接 BitBrowser...")
    conn_resp = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID}, timeout=10)
    conn_info = conn_resp.json()['data']
    http_port = conn_info['http']

    targets_resp = requests.get(f'http://{http_port}/json', timeout=10)
    targets = targets_resp.json()
    page_targets = [t for t in targets if t.get('type') == 'page']

    target = page_targets[1]  # 小红书创作服务平台
    ws_url = target['webSocketDebuggerUrl']
    print(f'    目标: {target["title"]}')

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

        print(f'\n[2] 导航到笔记...')
        print(f'    URL: {XHS_SHORT_URL}')
        await send('Page.navigate', {'url': XHS_SHORT_URL})
        await asyncio.sleep(6)

        title_result = await send('Runtime.evaluate', {'expression': 'document.title', 'returnByValue': True})
        title = title_result.get('result', {}).get('value', '')
        print(f'    标题: {title}')

        print(f'\n[3] 提取笔记数据...')

        result = await send('Runtime.evaluate', {
            'expression': '''
            (() => {
                // 获取正文 - 尝试多个选择器
                const descSelectors = [
                    '#detail-desc', '.detail-desc', '.note-content',
                    '[class*="desc"]', '#noteDesc', '.desc'
                ];
                let noteContent = '';
                for (const sel of descSelectors) {
                    const el = document.querySelector(sel);
                    if (el) { noteContent = el.innerText || ''; break; }
                }

                // 获取封面图片
                const coverImg = document.querySelector('.cover-img img, .cover img, [class*="cover"] img');
                const coverSrc = coverImg ? coverImg.src : '';

                // 获取所有图片（排除头像和图标）
                const allImgs = Array.from(document.querySelectorAll('img'));
                const noteImgs = allImgs
                    .filter(img => {
                        const src = img.src || '';
                        return src.includes('sns-webpic') || src.includes('rednotecdn') ||
                               src.includes('xiaohongshu.com/explore') || src.includes('xhscdn');
                    })
                    .map(img => ({
                        src: img.src,
                        alt: img.alt || '',
                        className: img.className || ''
                    }));

                // 获取视频信息
                const videos = Array.from(document.querySelectorAll('video'));
                const videoInfo = videos.map(v => ({
                    src: v.src || v.currentSrc || '',
                    poster: v.poster || '',
                    duration: v.duration || 0
                })).filter(v => v.src || v.currentSrc);

                // 查找页面初始数据（可能包含完整笔记数据）
                const scripts = Array.from(document.querySelectorAll('script'))
                    .map(s => s.textContent)
                    .filter(t => t.includes('note') && t.includes('url'));

                return {
                    noteContent: noteContent.substring(0, 500) || '未找到正文',
                    coverSrc: coverSrc,
                    imgCount: noteImgs.length,
                    images: noteImgs.slice(0, 20),
                    videoCount: videoInfo.length,
                    videos: videoInfo,
                    scriptsCount: scripts.length
                };
            })()
            ''',
            'returnByValue': True
        })

        data = result.get('result', {}).get('value', {})
        print(f'    正文: {data.get("noteContent", "未找到")}')
        print(f'    封面: {data.get("coverSrc", "")[:80]}')
        print(f'    图片: {data.get("imgCount", 0)} 张')
        print(f'    视频: {data.get("videoCount", 0)} 个')

        print(f'\n[4] 图片列表:')
        for i, img in enumerate(data.get('images', [])):
            print(f'    [{i+1}] {img["src"][:100]}')

        print(f'\n[5] 视频列表:')
        for i, v in enumerate(data.get('videos', [])):
            print(f'    [{i+1}] src: {v["src"][:100]}')
            print(f'        poster: {v["poster"][:100]}')

        # 分析图片URL结构
        print(f'\n[6] 图片URL分析...')
        sample_imgs = data.get('images', [])
        if sample_imgs:
            sample = sample_imgs[0]['src']
            print(f'    示例: {sample}')

            # 分析URL结构
            # 格式: https://sns-webpic-qc.xhscdn.com/时间戳/hash/用途/图片ID
            parts = sample.split('/')
            print(f'    路径段数: {len(parts)}')
            for j, p in enumerate(parts):
                print(f'      [{j}] {p[:40]}')

            # 提取关键模式
            m = re.search(r'/(\d{14})/([a-f0-9]+)/([^/]+)/(\w+)', sample)
            if m:
                print(f'    模式: 时间戳={m.group(1)}, hash={m.group(2)}, 用途={m.group(3)}, ID={m.group(4)}')

        # 保存数据
        output = {
            'title': title,
            'note_content': data.get('noteContent', ''),
            'cover_image': data.get('coverSrc', ''),
            'images': [img['src'] for img in data.get('images', [])],
            'videos': data.get('videos', []),
            'url': XHS_SHORT_URL
        }

        with open('D:/project/xhs_to_feishu/collected_note.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f'\n[7] 数据已保存到 collected_note.json')
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())