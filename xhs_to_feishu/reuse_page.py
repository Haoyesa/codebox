#!/usr/bin/env python
import asyncio, json, sys, io, requests, re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

async def main():
    # 1. 先用 browser/open 导航到搜索页
    print('Step 1: 导航到搜索页...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID, 'url': 'https://www.xiaohongshu.com/search_result?keyword=副业&type=51'}, timeout=15)
    http_port = conn.json()['data']['http']
    print('HTTP port:', http_port)

    # 2. 获取targets
    targets = requests.get(f'http://{http_port}/json', timeout=10).json()
    page_targets = [t for t in targets if t.get('type') == 'page']
    print('页面数量:', len(page_targets))
    for t in page_targets:
        print(' -', t.get('title', '')[:40], ':', t.get('url', '')[:60])

    # 3. 找到搜索结果页
    search_target = None
    for t in page_targets:
        if 'search_result' in t.get('url', ''):
            search_target = t
            break
    if not search_target and page_targets:
        search_target = page_targets[0]

    if not search_target:
        print('未找到搜索结果页')
        return

    ws_url = search_target['webSocketDebuggerUrl']
    print('使用页面:', search_target.get('title'))

    import websockets
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10, max_size=10*1024*1024) as ws:
        async def send(m, p=None):
            id = 1
            await ws.send(json.dumps({'id': id, 'method': m, 'params': p or {}}))
            async for msg in ws:
                return json.loads(msg).get('result', {})

        # 等待页面加载
        await asyncio.sleep(8)

        # 滚动
        for i in range(3):
            await send('Runtime.evaluate', {'expression': 'window.scrollBy(0, 800)', 'returnByValue': True})
            await asyncio.sleep(2)

        # 获取文本
        r = await send('Runtime.evaluate', {'expression': 'document.documentElement.innerText', 'returnByValue': True})
        text = ''
        if isinstance(r, dict):
            text = r.get('value', '')
        elif isinstance(r, str):
            text = r

        print('文本长度:', len(text))

        # 获取hrefs
        r2 = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var anchors = document.querySelectorAll("a");
    var hrefs = [];
    for (var i = 0; i < anchors.length; i++) {
        var href = anchors[i].getAttribute("href") || "";
        if (href && href.indexOf("/explore/") >= 0) {
            hrefs.push(href);
        }
    }
    return JSON.stringify(hrefs.slice(0, 30));
})()
            ''',
            'returnByValue': True
        })
        hrefs = []
        if isinstance(r2, dict):
            try:
                hrefs = json.loads(r2.get('value', '[]'))
            except:
                pass
        elif isinstance(r2, str):
            try:
                hrefs = json.loads(r2)
            except:
                pass

        print('hrefs:', len(hrefs))

        # 解析文本
        lines = text.split('\n')
        notes = []
        current = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if 'n' in line:
                clean = line.replace('n', '').strip()
                if clean:
                    if current.get('title'):
                        notes.append(current)
                    current = {'title': clean}
            elif re.match(r'^(\d+\.?\d*万?|\d+)$', line):
                num = line.replace('万', '0000')
                try:
                    val = int(float(num))
                    if val > 10 and 'collect' not in current:
                        current['collect'] = val
                except:
                    pass

        if current.get('title'):
            notes.append(current)

        print('解析到 {} 条'.format(len(notes)))

        print()
        print('| 序号 | 标题 | 链接 | 收藏数 |')
        print('|------|------|------|--------|')
        for i, note in enumerate(notes[:20], 1):
            title = note.get('title', '')[:40]
            collect = note.get('collect', 0)
            link = ''
            if i-1 < len(hrefs):
                href = hrefs[i-1]
                m = re.search(r'/explore/([a-f0-9]+)', href)
                if m:
                    link = 'https://www.xiaohongshu.com/explore/{}'.format(m.group(1))
            print('| {} | {} | {} | {} |'.format(i, title, link, collect))

asyncio.run(main())