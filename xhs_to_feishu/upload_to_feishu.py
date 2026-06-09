#!/usr/bin/env python
"""上传小红书笔记图片到飞书多维表格"""
import asyncio
import json
import sys
import io
import os
import tempfile
import requests
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

FEISHU_APP_ID = "cli_a961da72e8b9dbb4"
FEISHU_APP_SECRET = "E8dJJTCEO54602xLnTXUsfHxobPpHIFR"
FEISHU_APP_TOKEN = "WC0Kbwl6oa7UGWsemczcO7WMnwg"
FEISHU_TABLE_ID = "tbli2HXECsBi6jhp"

async def get_tenant_access_token():
    """获取 tenant access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    resp = requests.post(url, json=data, timeout=10)
    result = resp.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    return None

def upload_media_to_feishu(file_path, file_token=None):
    """上传媒体文件到飞书"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    token = get_tenant_access_token()
    if not token:
        raise Exception("无法获取 access token")

    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, "image/jpeg")}
        data = {
            "file_name": file_name,
            "parent_type": "bitable_image",
            "size": str(file_size),
        }
        if file_token:
            data["parent_node"] = file_token

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        result = resp.json()
        print(f"    上传结果: code={result.get('code')}, msg={result.get('msg')}")
        if result.get("code") == 0:
            return result.get("data", {}).get("file_token")
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
            temp_file = os.path.join(temp_dir, f"xhs_upload_{os.getpid()}{ext}")
            with open(temp_file, "wb") as f:
                f.write(resp.content)
            return temp_file
    except Exception as e:
        print(f"    下载失败: {e}")
    return None

async def main():
    print("=" * 60)
    print("上传小红书笔记到飞书多维表格")
    print("=" * 60)

    # 读取采集的数据
    with open('D:/project/xhs_to_feishu/collected_note.json', 'r', encoding='utf-8') as f:
        note_data = json.load(f)

    title = note_data.get('title', '')
    note_content = note_data.get('note_content', '')
    cover_image = note_data.get('cover_image', '')
    images = note_data.get('images', [])
    videos = note_data.get('videos', [])
    note_url = note_data.get('url', '')

    print(f"\n笔记标题: {title}")
    print(f"正文长度: {len(note_content)} 字符")
    print(f"图片数量: {len(images)}")
    print(f"视频数量: {len(videos)}")

    # 过滤出笔记图片（非头像）
    note_images = [img for img in images if 'avatar' not in img]
    print(f"笔记图片（排除头像）: {len(note_images)}")

    uploaded_tokens = []

    # 1. 上传封面图片
    print(f"\n[1] 上传封面图片...")
    if cover_image:
        temp_file = download_image(cover_image)
        if temp_file:
            print(f"    临时文件: {temp_file}")
            token = upload_media_to_feishu(temp_file, FEISHU_TABLE_ID)
            if token:
                print(f"    ✅ file_token: {token}")
                uploaded_tokens.append({'type': 'cover', 'token': token})
            os.unlink(temp_file)
        else:
            print("    ❌ 下载失败")

    # 2. 上传笔记图片
    print(f"\n[2] 上传笔记图片 ({len(note_images)} 张)...")
    image_tokens = []
    for i, img_url in enumerate(note_images[:10]):  # 限制10张
        print(f"    [{i+1}/{min(len(note_images), 10)}] {img_url[:60]}...")
        temp_file = download_image(img_url)
        if temp_file:
            token = upload_media_to_feishu(temp_file, FEISHU_TABLE_ID)
            if token:
                print(f"    ✅ {token}")
                image_tokens.append(token)
            else:
                print("    ❌ 上传失败")
            try:
                os.unlink(temp_file)
            except:
                pass
        else:
            print("    ❌ 下载失败")
        await asyncio.sleep(0.5)  # 避免请求过快

    # 3. 视频分析（如果未来有视频）
    print(f"\n[3] 视频URL分析...")
    if videos:
        for v in videos:
            print(f"    视频: {v.get('src', '')[:80]}")
    else:
        print("    本笔记无视频")

    # 保存上传结果
    result = {
        'title': title,
        'note_content': note_content,
        'cover_token': uploaded_tokens[0]['token'] if uploaded_tokens else None,
        'image_tokens': image_tokens,
        'video_tokens': [],
        'url': note_url
    }

    output_file = 'D:/project/xhs_to_feishu/upload_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[4] 上传结果已保存: {output_file}")
    print(f"    封面 token: {result['cover_token']}")
    print(f"    图片 tokens: {len(result['image_tokens'])} 个")

    print("\n" + "=" * 60)
    print("下一步：将数据写入飞书多维表格")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())