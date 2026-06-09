#!/usr/bin/env python
"""写入小红书笔记到飞书多维表格（使用现有字段）"""
import json
import sys
import io
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FEISHU_APP_ID = "cli_a961da72e8b9dbb4"
FEISHU_APP_SECRET = "E8dJJTCEO54602xLnTXUsfHxobPpHIFR"
FEISHU_APP_TOKEN = "WC0Kbwl6oa7UGWsemczcO7WMnwg"
FEISHU_TABLE_ID = "tbli2HXECsBi6jhp"

def get_token():
    resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}, timeout=10)
    return resp.json().get('tenant_access_token', '')

def create_record(fields, token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.post(url, json={"fields": fields}, headers=headers, timeout=30)
    return resp.json()

def add_field(field_name, field_type, token):
    """添加新字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/fields"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    # type 13 = 多媒体（图片/文件）
    resp = requests.post(url, json={
        "field_name": field_name,
        "type": field_type
    }, headers=headers, timeout=30)
    return resp.json()

# 读取上传结果
with open('D:/project/xhs_to_feishu/upload_result.json', 'r', encoding='utf-8') as f:
    upload_result = json.load(f)

with open('D:/project/xhs_to_feishu/collected_note.json', 'r', encoding='utf-8') as f:
    note = json.load(f)

token = get_token()
print(f"Token: {token[:30]}...")

# 提取话题标签作为关键词
content = note.get('note_content', '')
hashtags = [word for word in content.split() if word.startswith('#')]
print(f"关键词: {hashtags}")

# 1. 先尝试添加新字段
print("\n[1] 检查并添加必要字段...")

# 添加封面图片字段 (type 13 = 图片)
result = add_field("封面图片", 13, token)
print(f"  封面图片: code={result.get('code')}")

# 添加正文图/笔记视频字段 (type 13 = 多媒体)
result = add_field("正文图/笔记视频", 13, token)
print(f"  正文图/笔记视频: code={result.get('code')}")

# 2. 写入记录
print("\n[2] 写入记录...")
fields = {
    "标题": note.get('title', '').replace(' - 小红书', ''),
    "链接": note.get('url', ''),
    "关键词": ' '.join(hashtags),
}

cover_token = upload_result.get('cover_token')
if cover_token:
    fields["封面图片"] = [{"token": cover_token}]

image_tokens = upload_result.get('image_tokens', [])
if image_tokens:
    fields["正文图/笔记视频"] = [{"token": t} for t in image_tokens[:9]]

result = create_record(fields, token)
print(f"    结果: code={result.get('code')}, msg={result.get('msg')}")

if result.get('code') == 0:
    record = result.get('data', {}).get('record', {})
    print(f"    ✅ 记录已创建: {record.get('record_id', 'unknown')}")
else:
    print(f"    错误详情: {json.dumps(result, ensure_ascii=False)}")

print("\n完成")