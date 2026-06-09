#!/usr/bin/env python
"""写入小红书笔记到飞书多维表格"""
import json, sys, io, requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FEISHU_APP_ID = "cli_a961da72e8b9dbb4"
FEISHU_APP_SECRET = "E8dJJTCEO54602xLnTXUsfHxobPpHIFR"
FEISHU_APP_TOKEN = "WC0Kbwl6oa7UGWsemczcO7WMnwg"
FEISHU_TABLE_ID = "tbli2HXECsBi6jhp"

def get_token():
    r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': FEISHU_APP_ID, 'app_secret': FEISHU_APP_SECRET}, timeout=10)
    return r.json().get('tenant_access_token', '')

def create_record(fields, token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    r = requests.post(url, json={"fields": fields}, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, timeout=30)
    return r.json()

# 读取数据
with open('D:/project/xhs_to_feishu/upload_result.json', 'r') as f:
    upload = json.load(f)
with open('D:/project/xhs_to_feishu/collected_note.json', 'r') as f:
    note = json.load(f)

token = get_token()
print(f"Token: {token[:30]}...")

title = note.get('title', '').replace(' - 小红书', '')
content = note.get('note_content', '')
note_url = note.get('url', '')
hashtags = ' '.join([w for w in content.split() if w.startswith('#')])

print(f"标题: {title}")

# 构建字段
fields = {
    "标题": title,
    "链接": {"link": note_url, "text": title[:50]},
    "关键词": hashtags,
}

cover_token = upload.get('cover_token')
if cover_token:
    fields["封面图"] = [{"token": cover_token}]

image_tokens = upload.get('image_tokens', [])
if image_tokens:
    fields["正文图片"] = [{"token": t} for t in image_tokens[:9]]

print(f"字段: {list(fields.keys())}")

result = create_record(fields, token)
print(f"结果: code={result.get('code')}, msg={result.get('msg')}")

if result.get('code') == 0:
    rec = result.get('data', {}).get('record', {})
    print(f"✅ 记录已创建: {rec.get('record_id', 'unknown')}")
else:
    print(f"❌ 失败: {json.dumps(result, ensure_ascii=False)}")