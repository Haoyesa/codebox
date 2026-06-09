#!/usr/bin/env python
"""使用飞书 MCP 客户端上传图片"""
import asyncio
import json
import sys
import io
import os
import tempfile
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加飞书 MCP 到路径
sys.path.insert(0, 'D:/project/feishu-bitable-mcp/src')

from feishu_bitable_mcp.client import FeishuBitableClient
import requests

FEISHU_APP_ID = "cli_a961da72e8b9dbb4"
FEISHU_APP_SECRET = "E8dJJTCEO54602xLnTXUsfHxobPpHIFR"
FEISHU_TABLE_ID = "tbli2HXECsBi6jhp"

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
    print("上传小红书笔记到飞书多维表格 (使用 MCP 客户端)")
    print("=" * 60)

    # 读取采集的数据
    with open('D:/project/xhs_to_feishu/collected_note.json', 'r', encoding='utf-8') as f:
        note_data = json.load(f)

    title = note_data.get('title', '')
    note_content = note_data.get('note_content', '')
    cover_image = note_data.get('cover_image', '')
    images = note_data.get('images', [])
    note_url = note_data.get('url', '')

    print(f"\n笔记标题: {title}")
    print(f"正文: {note_content[:50]}...")

    # 过滤出笔记图片（非头像）
    note_images = [img for img in images if 'avatar' not in img]
    print(f"笔记图片: {len(note_images)} 张")

    # 使用飞书客户端
    print("\n[1] 初始化飞书客户端...")
    client = FeishuBitableClient(
        app_id=FEISHU_APP_ID,
        app_secret=FEISHU_APP_SECRET
    )
    print("    ✅ 客户端初始化成功")

    # 2. 上传封面图片
    print("\n[2] 上传封面图片...")
    cover_token = None
    if cover_image:
        temp_file = download_image(cover_image)
        if temp_file:
            print(f"    临时文件: {temp_file} ({os.path.getsize(temp_file)} bytes)")
            try:
                result = client.upload_media(temp_file, parent_node=FEISHU_TABLE_ID)
                print(f"    上传结果: {result}")
                if result and result.get('file_token'):
                    cover_token = result['file_token']
                    print(f"    ✅ file_token: {cover_token}")
            except Exception as e:
                print(f"    ❌ 上传失败: {e}")
            try:
                os.unlink(temp_file)
            except:
                pass
        else:
            print("    ❌ 下载失败")

    # 3. 上传笔记图片
    print(f"\n[3] 上传笔记图片 ({len(note_images)} 张)...")
    image_tokens = []
    for i, img_url in enumerate(note_images[:10]):
        print(f"    [{i+1}/{min(len(note_images), 10)}] {img_url[:60]}...")
        temp_file = download_image(img_url)
        if temp_file:
            try:
                result = client.upload_media(temp_file, parent_node=FEISHU_TABLE_ID)
                if result and result.get('file_token'):
                    print(f"    ✅ {result['file_token']}")
                    image_tokens.append(result['file_token'])
                else:
                    print(f"    结果: {result}")
            except Exception as e:
                print(f"    ❌ {e}")
            try:
                os.unlink(temp_file)
            except:
                pass
        else:
            print("    ❌ 下载失败")
        await asyncio.sleep(0.3)

    # 4. 保存结果
    result_data = {
        'title': title,
        'note_content': note_content,
        'cover_token': cover_token,
        'image_tokens': image_tokens,
        'url': note_url
    }

    output_file = 'D:/project/xhs_to_feishu/upload_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n[4] 结果已保存: {output_file}")
    print(f"    封面 token: {cover_token}")
    print(f"    图片 tokens: {len(image_tokens)} 个")

    # 5. 写入多维表格
    print("\n[5] 写入飞书多维表格...")
    try:
        # 先列出字段
        fields = client.list_fields(FEISHU_TABLE_ID, "Default View")
        print(f"    字段数量: {len(fields) if fields else 0}")

        # 创建记录
        record = {
            "fields": {
                "标题": title.replace(" - 小红书", ""),
                "正文": note_content,
                "来源链接": note_url,
            }
        }

        # 如果有封面token，添加到记录
        if cover_token:
            record["fields"]["封面图片"] = [{"token": cover_token}]

        # 如果有图片tokens，添加到记录
        if image_tokens:
            record["fields"]["正文图"] = [{"token": t} for t in image_tokens[:9]]

        result = client.create_record(FEISHU_TABLE_ID, record)
        print(f"    创建记录结果: {result}")
    except Exception as e:
        print(f"    ❌ 写入失败: {e}")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())