#!/usr/bin/env python
"""上传小红书笔记图片到飞书多维表格"""
import asyncio
import json
import sys
import io
import os
import tempfile
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

FEISHU_APP_ID = "cli_a961da72e8b9dbb4"
FEISHU_APP_SECRET = "E8dJJTCEO54602xLnTXUsfHxobPpHIFR"
FEISHU_APP_TOKEN = "WC0Kbwl6oa7UGWsemczcO7WMnwg"  # 多维表格的 app_token
FEISHU_TABLE_ID = "tbli2HXECsBi6jhp"

def get_token():
    resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}, timeout=10)
    return resp.json().get('tenant_access_token', '')

def upload_image(file_path, token):
    """上传单个图片"""
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f, 'image/jpeg')}
        data = {
            'file_name': file_name,
            'parent_type': 'bitable_image',
            'size': str(file_size),
            'parent_node': FEISHU_APP_TOKEN  # 这里是 app_token
        }
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.post('https://open.feishu.cn/open-apis/drive/v1/medias/upload_all',
            files=files, data=data, headers=headers, timeout=30)
        result = resp.json()
        if result.get('code') == 0:
            return result['data']['file_token']
    return None

def download_image(url, timeout=15):
    """下载图片到临时文件"""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if resp.status_code == 200:
            ext = os.path.splitext(url.split('?')[0])[-1] or '.jpg'
            if not ext or len(ext) > 5:
                ext = '.jpg'
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"xhs_{os.getpid()}{ext}")
            with open(temp_file, "wb") as f:
                f.write(resp.content)
            return temp_file
    except Exception as e:
        print(f"    下载失败: {e}")
    return None

def create_bitablerecord(values, token):
    """创建多维表格记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {"fields": values}
    resp = requests.post(url, json=data, headers=headers, timeout=30)
    return resp.json()

async def main():
    print("=" * 60)
    print("上传小红书笔记到飞书多维表格")
    print("=" * 60)

    token = get_token()
    if not token:
        print("❌ 无法获取 token")
        return
    print(f"Token: {token[:30]}...")

    # 读取采集数据
    with open('D:/project/xhs_to_feishu/collected_note.json', 'r', encoding='utf-8') as f:
        note = json.load(f)

    title = note.get('title', '').replace(' - 小红书', '')
    content = note.get('note_content', '')
    cover_url = note.get('cover_image', '')
    images = note.get('images', [])
    note_url = note.get('url', '')
    note_images = [img for img in images if 'avatar' not in img]

    print(f"\n笔记: {title}")
    print(f"正文: {content[:50]}...")
    print(f"封面: {cover_url[:60]}...")
    print(f"图片: {len(note_images)} 张")

    # 1. 上传封面
    cover_token = None
    print("\n[1] 上传封面图片...")
    if cover_url:
        temp = download_image(cover_url)
        if temp:
            cover_token = upload_image(temp, token)
            if cover_token:
                print(f"    ✅ {cover_token}")
            os.unlink(temp)

    # 2. 上传正文图
    print(f"\n[2] 上传 {len(note_images)} 张正文图...")
    image_tokens = []
    for i, url in enumerate(note_images[:10]):
        print(f"    [{i+1}/{min(len(note_images), 10)}] {url[:50]}...", end=" ")
        temp = download_image(url)
        if temp:
            tok = upload_image(temp, token)
            if tok:
                print(f"✅ {tok}")
                image_tokens.append(tok)
            else:
                print("❌")
            os.unlink(temp)
        else:
            print("❌")
        await asyncio.sleep(0.2)

    # 3. 写入记录
    print("\n[3] 写入飞书多维表格...")
    fields = {
        "标题": title,
        "正文": content,
        "来源链接": note_url,
    }

    if cover_token:
        fields["封面图片"] = [{"token": cover_token}]

    if image_tokens:
        fields["正文图/笔记视频"] = [{"token": t} for t in image_tokens[:9]]

    result = create_bitablerecord(fields, token)
    print(f"    结果: code={result.get('code')}, msg={result.get('msg')}")

    if result.get('code') == 0:
        record = result.get('data', {}).get('record', {})
        print(f"    ✅ 记录已创建: {record.get('record_id', 'unknown')}")
    else:
        print(f"    ❌ 失败: {result}")

    # 保存结果
    output = {
        'title': title,
        'cover_token': cover_token,
        'image_tokens': image_tokens,
        'feishu_result': result
    }
    with open('D:/project/xhs_to_feishu/upload_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())