#!/usr/bin/env python
"""从飞书表格读取第1行笔记链接，访问并采集详细信息"""
import asyncio, json, sys, io, os, tempfile, requests, re
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

FEISHU_APP_ID = 'cli_a961da72e8b9dbb4'
FEISHU_APP_SECRET = 'E8dJJTCEO54602xLnTXUsfHxobPpHIFR'
FEISHU_APP_TOKEN = 'UIjVb1N5raGjrKs6TZYcF9XHn0R'
FEISHU_TABLE_ID = 'tblTnAzXDnF7jhRu'
BIT_BROWSER_ID = '68b8252b06454718b2c65b7dd1639341'

def get_token():
    r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}, timeout=10)
    return r.json().get('tenant_access_token', '')

def upload_to_feishu(file_path):
    """上传媒体到飞书"""
    if not os.path.exists(file_path):
        return None
    token = get_token()
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f, 'image/jpeg')}
        data = {'file_name': file_name, 'parent_type': 'bitable_image', 'size': str(file_size), 'parent_node': FEISHU_APP_TOKEN}
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.post('https://open.feishu.cn/open-apis/drive/v1/medias/upload_all', files=files, data=data, headers=headers, timeout=30)
        result = r.json()
        if result.get('code') == 0:
            return result['data']['file_token']
    return None

def download_file(url, timeout=20):
    """下载文件到临时路径"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, timeout=timeout, headers=headers)
        if r.status_code == 200:
            ext = os.path.splitext(url.split('?')[0])[-1] or '.mp4'
            if len(ext) > 5: ext = '.mp4'
            temp_file = os.path.join(tempfile.gettempdir(), f'xhs_dl_{os.getpid()}{ext}')
            with open(temp_file, 'wb') as f:
                f.write(r.content)
            return temp_file
    except Exception as e:
        print(f'    下载失败: {e}')
    return None

async def collect_note_detail(http_port, note_url):
    """采集笔记详情"""
    import websockets
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

        print(f'    导航到: {note_url}')
        await send('Page.navigate', {'url': note_url})
        await asyncio.sleep(6)

        title_r = await send('Runtime.evaluate', {'expression': "document.title", 'returnByValue': True})
        print(f'    标题: {title_r}')

        # 提取笔记数据
        result = await send('Runtime.evaluate', {
            'expression': '''
(function() {
    var data = {};
    var text = document.body.innerText;

    // 标题
    var titleEl = document.querySelector('.note-content .title, .note-content h1, #detail-title, [class*="title"]');
    data.title = titleEl ? titleEl.innerText : text.split('\\n')[0];

    // 作者名
    var authorEl = document.querySelector('.author-info .name, .author-name, [class*="author"] .name, .user-name');
    data.author_name = authorEl ? authorEl.innerText : '';

    // 标签/话题
    var tags = [];
    var tagEls = document.querySelectorAll('.tag, .topic, [class*="tag"]');
    tagEls.forEach(function(el) { tags.push(el.innerText); });
    data.tags = tags.slice(0, 20).join(', ');

    // 正文
    var contentEl = document.querySelector('#detail-desc, .detail-desc, .note-content, [class*="content"]');
    data.content = contentEl ? contentEl.innerText : '';

    // 点赞/收藏/评论数
    var likeEl = document.querySelector('.like-wrapper .count, .like .count, [class*="like"] .count');
    var collectEl = document.querySelector('.collect-wrapper .count, .collect .count, [class*="collect"] .count');
    var commentEl = document.querySelector('.comment-wrapper .count, .comment .count, [class*="comment"] .count');
    data.like_count = likeEl ? likeEl.innerText : '';
    data.collect_count = collectEl ? collectEl.innerText : '';
    data.comment_count = commentEl ? commentEl.innerText : '';

    // 分享数
    var shareEl = document.querySelector('.share-wrapper .count, .share .count, [class*="share"] .count');
    data.share_count = shareEl ? shareEl.innerText : '';

    // 视频URL
    var videoEl = document.querySelector('video source, video');
    data.video_url = videoEl ? (videoEl.src || videoEl.currentSrc) : '';

    // 封面URL
    var coverEl = document.querySelector('video[poster], .cover-img img, [class*="cover"] img');
    data.cover_url = coverEl ? coverEl.src || coverEl.poster || '' : '';

    // 发布时间
    var timeEl = document.querySelector('.time, .date, [class*="time"], [class*="date"]');
    data.publish_time = timeEl ? timeEl.innerText : '';

    // 作者粉丝量 - 从页面提取
    var followerMatch = text.match(/(\\d+\\.?\\d*\\w*)\\s*粉丝/);
    data.follower_count = followerMatch ? followerMatch[0] : '';

    return data;
})
            ''',
            'returnByValue': True
        })
        return result

async def main():
    print('=' * 60)
    print('小红书笔记详细采集')
    print('=' * 60)

    # 1. 从飞书表格读取第1行
    print('\n[1] 从飞书表格读取第1行...')
    token = get_token()
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records?page_size=1'
    r = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=15)
    result = r.json()
    if result.get('code') != 0:
        print(f'    读取失败: {result}')
        return

    items = result.get('data', {}).get('items', [])
    if not items:
        print('    无记录')
        return

    fields = items[0]['fields']
    note_link = fields.get('小红书链接', '')
    author_name = fields.get('作者名', '')
    print(f'    笔记链接: {note_link}')
    print(f'    作者名: {author_name}')

    # 2. 用BitBrowser打开笔记
    print('\n[2] 连接BitBrowser...')
    conn = requests.post('http://127.0.0.1:54345/browser/open', json={'id': BIT_BROWSER_ID, 'url': note_link}, timeout=15)
    conn_info = conn.json().get('data', {})
    http_port = conn_info.get('http')
    print(f'    HTTP端口: {http_port}')

    # 3. 采集数据
    print('\n[3] 采集笔记数据...')
    note_data = await collect_note_detail(http_port, note_link)
    data = note_data.get('result', {}).get('value', note_data) if isinstance(note_data, dict) else note_data
    if isinstance(data, dict):
        print(f'    标题: {data.get("title", "")[:50]}')
        print(f'    作者: {data.get("author_name", "")}')
        print(f'    标签: {data.get("tags", "")[:50]}')
        print(f'    点赞: {data.get("like_count", "")}')
        print(f'    收藏: {data.get("collect_count", "")}')
        print(f'    评论: {data.get("comment_count", "")}')
        print(f'    分享: {data.get("share_count", "")}')
        print(f'    视频URL: {data.get("video_url", "")[:80]}')
        print(f'    封面URL: {data.get("cover_url", "")[:80]}')

    # 4. 如果有视频，下载并上传
    video_token = None
    cover_token = None

    video_url = data.get('video_url', '') if isinstance(data, dict) else ''
    cover_url = data.get('cover_url', '') if isinstance(data, dict) else ''

    if video_url and 'mp4' in video_url.lower():
        print('\n[4] 处理视频...')
        print(f'    下载视频: {video_url[:60]}...')
        temp_video = download_file(video_url)
        if temp_video:
            print(f'    上传视频到飞书...')
            video_token = upload_to_feishu(temp_video)
            if video_token:
                print(f'    ✅ video_token: {video_token}')
            os.unlink(temp_video)

    # 5. 处理封面
    if cover_url:
        print('\n[5] 处理封面...')
        print(f'    下载封面: {cover_url[:60]}...')
        temp_cover = download_file(cover_url)
        if temp_cover:
            print(f'    上传封面到飞书...')
            cover_token = upload_to_feishu(temp_cover)
            if cover_token:
                print(f'    ✅ cover_token: {cover_token}')
            os.unlink(temp_cover)

    # 6. 保存结果
    print('\n[6] 保存结果...')
    output = {
        'note_url': note_link,
        'title': data.get('title', '') if isinstance(data, dict) else '',
        'author_name': data.get('author_name', '') if isinstance(data, dict) else author_name,
        'tags': data.get('tags', '') if isinstance(data, dict) else '',
        'content': data.get('content', '') if isinstance(data, dict) else '',
        'like_count': data.get('like_count', '') if isinstance(data, dict) else '',
        'collect_count': data.get('collect_count', '') if isinstance(data, dict) else '',
        'comment_count': data.get('comment_count', '') if isinstance(data, dict) else '',
        'share_count': data.get('share_count', '') if isinstance(data, dict) else '',
        'video_url': video_url,
        'cover_url': cover_url,
        'video_token': video_token,
        'cover_token': cover_token,
        'publish_time': data.get('publish_time', '') if isinstance(data, dict) else '',
        'follower_count': data.get('follower_count', '') if isinstance(data, dict) else '',
    }

    with open('D:/project/xhs_to_feishu/note_detail.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'    已保存到 note_detail.json')

    print('\n' + '=' * 60)
    print('采集完成')
    print('=' * 60)

if __name__ == '__main__':
    asyncio.run(main())