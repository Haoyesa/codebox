#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书多维表格写入客户端
"""

import requests
import json
from typing import List, Dict, Any


class FeishuClient:
    def __init__(self, app_token: str, table_id: str, access_token: str = None, app_id: str = None, app_secret: str = None):
        self.app_token = app_token
        self.table_id = table_id
        self.base_url = "https://open.feishu.cn/open-apis/bitable/v1"
        self.app_id = app_id
        self.app_secret = app_secret

        if access_token:
            self.access_token = access_token
        elif app_id and app_secret:
            self.access_token = self._get_access_token()
        else:
            raise ValueError("需要提供 access_token 或 app_id/app_secret")

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_access_token(self) -> str:
        """获取 tenant access token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0:
            raise Exception(f"获取飞书 Access Token 失败: {data}")
        return data.get("tenant_access_token")

    def get_fields(self) -> List[Dict[str, Any]]:
        """获取多维表格字段列表"""
        url = f"{self.base_url}/apps/{self.app_token}/tables/{self.table_id}/fields"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("data", {}).get("items", [])

    def _prepare_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """预处理记录，转换超链接字段格式"""
        import re
        prepared = {"fields": {}}
        for key, value in record.get("fields", {}).items():
            if isinstance(value, str) and re.match(r"^https?://", value):
                prepared["fields"][key] = {"link": value, "text": value}
            else:
                prepared["fields"][key] = value
        return prepared

    def batch_create_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量创建记录"""
        url = f"{self.base_url}/apps/{self.app_token}/tables/{self.table_id}/records/batch_create"
        prepared_records = [self._prepare_record(r) for r in records]
        payload = {"records": prepared_records}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def ensure_fields(self, required_fields: List[str]) -> None:
        """确保必要的字段存在，不存在则自动创建"""
        existing_fields = self.get_fields()
        existing_names = {f["field_name"] for f in existing_fields}

        for field_name in required_fields:
            if field_name not in existing_names:
                self._create_field(field_name)

    def _create_field(self, field_name: str, field_type: int = 1) -> None:
        """创建字段 field_type: 1=文本, 2=数字, 5=日期, 15=超链接"""
        url = f"{self.base_url}/apps/{self.app_token}/tables/{self.table_id}/fields"
        payload = {"field_name": field_name, "type": field_type}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code != 200:
                print(f"  警告: 字段 {field_name} 创建失败，可能已存在")
        except Exception as e:
            print(f"  警告: 字段 {field_name} 创建异常: {e}")