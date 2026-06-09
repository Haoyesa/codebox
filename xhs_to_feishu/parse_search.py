#!/usr/bin/env python
import asyncio, json, sys, io, requests, re

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

        # 获取完整页面文本
        r = await send('Runtime.evaluate', {'expression': 'document.documentElement.innerText', 'returnByValue': True})
        text = r if isinstance(r, str) else (r.get('value', '') if isinstance(r, dict) else '')

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
        hrefs_raw = r2 if isinstance(r2, str) else (r2.get('value', '') if isinstance(r2, dict) else '')
        try:
            hrefs = json.loads(hrefs_raw)
        except:
            hrefs = []

        print('获取到 {} 个hrefs'.format(len(hrefs)))
        print('文本长度: {} 字符'.format(len(text)))

        # 解析文本中的笔记信息
        # 格式: 作者名 + 日期/时间 + 收藏数 + 标题
        lines = text.split('\n')

        notes = []
        current_note = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 检查是否是标题行（包含换行符 n）
            if 'n' in line:
                # 这可能是标题
                clean_title = line.replace('n', '').strip()
                if current_note and current_note.get('title'):
                    # 保存上一个
                    notes.append(current_note)
                current_note = {'title': clean_title}
            # 检查是否是数字（收藏数）
            elif re.match(r'^(\d+\.?\d*万?|\d+)$', line):
                num = line.replace('万', '0000')
                try:
                    val = int(float(num))
                    if val > 10:  # 可能是收藏数
                        if current_note and 'collect' not in current_note:
                            current_note['collect'] = val
                except:
                    pass

        if current_note and current_note.get('title'):
            notes.append(current_note)

        # 另一个策略：直接用正则匹配特定模式
        # 例如: "野路子Robin\n05-22\n4088"
        note_pattern = re.findall(r'([^\n]+)\n(\d{2}-\d{2,4}|昨天|\d+天前|\d+小时前|[今昨前]\w+)\n(\d+\.?\d*万?)\n', text)

        print()
        print('找到 {} 条笔记'.format(len(notes)))
        print()
        print('| 序号 | 标题 | 链接 | 收藏数 |')
        print('|------|------|------|--------|')

        # 尝试将hrefs与笔记关联
        id_idx = 0
        for i, note in enumerate(notes[:20], 1):
            title = note.get('title', '')[:40]
            collect = note.get('collect', 0)
            link = ''
            if id_idx < len(hrefs):
                href = hrefs[id_idx]
                m = re.search(r'/explore/([a-f0-9]+)', href)
                if m:
                    link = 'https://www.xiaohongshu.com/explore/{}'.format(m.group(1))
                id_idx += 1
            print('| {} | {} | {} | {} |'.format(i, title, link, collect))

asyncio.run(main())