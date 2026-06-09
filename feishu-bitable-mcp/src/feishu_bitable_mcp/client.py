"""
飞书多维表格 API 客户端
"""

import os
import time
import json
from typing import Any, Optional
from dotenv import load_dotenv
import httpx

load_dotenv()


class FeishuBitableClient:
    """飞书多维表格 API 客户端"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        user_access_token: Optional[str] = None,
        api_base_url: Optional[str] = None,
        user_id_type: str = "open_id",
    ):
        """
        初始化飞书客户端

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            user_access_token: 用户访问令牌 (直接使用)
            api_base_url: API基础URL
            user_id_type: 用户ID类型 (open_id/union_id/user_id)
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        self.user_access_token = user_access_token or os.getenv("FEISHU_USER_ACCESS_TOKEN")
        self.api_base_url = api_base_url or os.getenv(
            "FEISHU_API_BASE_URL", "https://open.feishu.cn/open-apis"
        )
        self.user_id_type = user_id_type or os.getenv("FEISHU_USER_ID_TYPE", "open_id")

        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_tenant_access_token(self) -> str:
        """获取或刷新 tenant_access_token"""
        if self._tenant_access_token and time.time() < self._token_expires_at:
            return self._tenant_access_token

        if not self.app_id or not self.app_secret:
            raise ValueError(
                "请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量, "
                "或直接设置 FEISHU_USER_ACCESS_TOKEN"
            )

        url = f"{self.api_base_url}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                raise RuntimeError(f"获取tenant_access_token失败: {data.get('msg')}")

            self._tenant_access_token = data["tenant_access_token"]
            # 提前5分钟刷新
            self._token_expires_at = time.time() + data.get("expire", 7200) - 300

        return self._tenant_access_token

    def _get_headers(self) -> dict:
        """获取请求头"""
        if self.user_access_token:
            return {
                "Authorization": f"Bearer {self.user_access_token}",
                "Content-Type": "application/json; charset=utf-8",
            }
        else:
            token = self._get_tenant_access_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        """发送API请求"""
        url = f"{self.api_base_url}{endpoint}"
        headers = self._get_headers()

        with httpx.Client(timeout=60.0) as client:
            if method.upper() == "GET":
                response = client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, params=params, json=json_data, headers=headers)
            elif method.upper() == "PUT":
                response = client.put(url, params=params, json=json_data, headers=headers)
            elif method.upper() == "PATCH":
                response = client.patch(url, params=params, json=json_data, headers=headers)
            elif method.upper() == "DELETE":
                response = client.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response.raise_for_status()
            return response.json()

    # ============ 多维表格 (App) 操作 ============

    def create_app(
        self,
        name: Optional[str] = None,
        folder_token: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> dict:
        """创建多维表格"""
        payload = {}
        if name:
            payload["name"] = name
        if folder_token:
            payload["folder_token"] = folder_token
        if time_zone:
            payload["time_zone"] = time_zone

        return self._request("POST", "/bitable/v1/apps", json_data=payload)

    def get_app(self, app_token: str) -> dict:
        """获取多维表格元数据"""
        return self._request("GET", f"/bitable/v1/apps/{app_token}")

    def update_app(
        self,
        app_token: str,
        name: Optional[str] = None,
        is_advanced: Optional[bool] = None,
    ) -> dict:
        """更新多维表格"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if is_advanced is not None:
            payload["is_advanced"] = is_advanced

        return self._request("PUT", f"/bitable/v1/apps/{app_token}", json_data=payload)

    def copy_app(
        self,
        app_token: str,
        name: Optional[str] = None,
        folder_token: Optional[str] = None,
        without_content: bool = False,
        time_zone: Optional[str] = None,
    ) -> dict:
        """复制多维表格"""
        payload = {
            "without_content": without_content,
        }
        if name:
            payload["name"] = name
        if folder_token:
            payload["folder_token"] = folder_token
        if time_zone:
            payload["time_zone"] = time_zone

        return self._request("POST", f"/bitable/v1/apps/{app_token}/copy", json_data=payload)

    # ============ 数据表 (Table) 操作 ============

    def create_table(
        self,
        app_token: str,
        table_name: str,
        default_view_name: Optional[str] = None,
        fields: Optional[list] = None,
    ) -> dict:
        """新增数据表"""
        payload = {"table": {"name": table_name}}
        if default_view_name:
            payload["table"]["default_view_name"] = default_view_name
        if fields:
            payload["table"]["fields"] = fields

        return self._request("POST", f"/bitable/v1/apps/{app_token}/tables", json_data=payload)

    def batch_create_tables(
        self, app_token: str, tables: list[dict], user_id_type: str = "open_id"
    ) -> dict:
        """批量新增数据表"""
        payload = {"tables": tables}
        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/batch_create",
            params={"user_id_type": user_id_type},
            json_data=payload,
        )

    def list_tables(
        self,
        app_token: str,
        page_token: Optional[str] = None,
        page_size: int = 20,
    ) -> dict:
        """列出数据表"""
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token

        return self._request("GET", f"/bitable/v1/apps/{app_token}/tables", params=params)

    def update_table(self, app_token: str, table_id: str, name: str) -> dict:
        """更新数据表"""
        return self._request(
            "PATCH",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}",
            json_data={"name": name},
        )

    def delete_table(self, app_token: str, table_id: str) -> dict:
        """删除数据表"""
        return self._request("DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}")

    def batch_delete_tables(self, app_token: str, table_ids: list[str]) -> dict:
        """批量删除数据表"""
        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/batch_delete",
            json_data={"table_ids": table_ids},
        )

    # ============ 字段 (Field) 操作 ============

    def list_fields(
        self,
        app_token: str,
        table_id: str,
        view_id: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 20,
        text_field_as_array: bool = False,
    ) -> dict:
        """列出字段"""
        params = {
            "page_size": page_size,
            "text_field_as_array": text_field_as_array,
        }
        if view_id:
            params["view_id"] = view_id
        if page_token:
            params["page_token"] = page_token

        return self._request(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            params=params,
        )

    def create_field(
        self,
        app_token: str,
        table_id: str,
        field_name: str,
        field_type: int,
        property: Optional[dict] = None,
        client_token: Optional[str] = None,
    ) -> dict:
        """新增字段"""
        payload = {
            "field_name": field_name,
            "type": field_type,
        }
        if property:
            payload["property"] = property
        if client_token:
            payload["client_token"] = client_token

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            json_data=payload,
        )

    def delete_field(self, app_token: str, table_id: str, field_id: str) -> dict:
        """删除字段"""
        return self._request(
            "DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
        )

    # ============ 附件上传下载 (新增功能) ============

    def upload_media(
        self,
        file_path: str,
        file_name: Optional[str] = None,
        parent_type: str = "bitable_image",
        parent_node: Optional[str] = None,
    ) -> dict:
        """
        上传媒体文件/附件到飞书

        Args:
            file_path: 本地文件路径
            file_name: 文件名（可选，默认使用原文件名）
            parent_type: 父节点类型，默认为 "bitable_image"
            parent_node: 父节点token（可选，用于指定多维表格）

        Returns:
            包含 file_token 等信息的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_name:
            file_name = os.path.basename(file_path)

        file_size = os.path.getsize(file_path)

        # 获取认证token
        token = self.user_access_token or self._get_tenant_access_token()

        url = f"{self.api_base_url}/drive/v1/medias/upload_all"

        # 构建multipart表单数据
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, self._get_content_type(file_path))}
            data = {
                "file_name": file_name,
                "parent_type": parent_type,
                "size": str(file_size),
            }
            if parent_node:
                data["parent_node"] = parent_node

            headers = {
                "Authorization": f"Bearer {token}"
                # 注意：httpx会自动设置Content-Type为multipart/form-data
            }

            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, headers=headers, data=data, files=files)
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    raise RuntimeError(f"上传文件失败: {result.get('msg')}")

                return result.get("data", {})

    def download_media(
        self,
        file_token: str,
        save_path: str,
        file_name: Optional[str] = None,
    ) -> str:
        """
        从飞书下载媒体文件/附件

        Args:
            file_token: 文件token
            save_path: 保存目录路径
            file_name: 保存的文件名（可选，默认使用原文件名）

        Returns:
            保存的完整文件路径
        """
        # 获取认证token
        token = self.user_access_token or self._get_tenant_access_token()

        url = f"{self.api_base_url}/drive/v1/medias/{file_token}/download"

        headers = {"Authorization": f"Bearer {token}"}

        with httpx.Client(timeout=120.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

            # 从Content-Disposition获取文件名
            content_disposition = response.headers.get("Content-Disposition", "")
            if not file_name and "filename=" in content_disposition:
                file_name = content_disposition.split("filename=")[1].strip("\"'")

            if not file_name:
                file_name = f"{file_token}.bin"

            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)
            full_path = os.path.join(save_path, file_name)

            # 保存文件
            with open(full_path, "wb") as f:
                f.write(response.content)

            return full_path

    def _get_content_type(self, file_path: str) -> str:
        """根据文件扩展名获取Content-Type"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".mp4": "video/mp4",
            ".mp3": "audio/mpeg",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".txt": "text/plain",
        }
        return content_types.get(ext, "application/octet-stream")

    # ============ 记录 (Record) 操作 ============

    def create_record(
        self,
        app_token: str,
        table_id: str,
        fields: dict,
        user_id_type: str = "open_id",
        client_token: Optional[str] = None,
        ignore_consistency_check: bool = False,
    ) -> dict:
        """新增单条记录"""
        payload = {"fields": fields}
        params = {"user_id_type": user_id_type}
        if client_token:
            params["client_token"] = client_token
        if ignore_consistency_check:
            params["ignore_consistency_check"] = "true"

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            params=params,
            json_data=payload,
        )

    def batch_create_records(
        self,
        app_token: str,
        table_id: str,
        records: list[dict],
        user_id_type: str = "open_id",
        client_token: Optional[str] = None,
        ignore_consistency_check: bool = False,
    ) -> dict:
        """批量新增记录 (最多1000条)"""
        payload = {"records": records}
        params = {"user_id_type": user_id_type}
        if client_token:
            params["client_token"] = client_token
        if ignore_consistency_check:
            params["ignore_consistency_check"] = "true"

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            params=params,
            json_data=payload,
        )

    def update_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        fields: dict,
        user_id_type: str = "open_id",
        ignore_consistency_check: bool = False,
    ) -> dict:
        """更新单条记录"""
        payload = {"fields": fields}
        params = {"user_id_type": user_id_type}
        if ignore_consistency_check:
            params["ignore_consistency_check"] = "true"

        return self._request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            params=params,
            json_data=payload,
        )

    def batch_update_records(
        self,
        app_token: str,
        table_id: str,
        records: list[dict],
        user_id_type: str = "open_id",
        ignore_consistency_check: bool = False,
    ) -> dict:
        """批量更新记录 (最多1000条)"""
        payload = {"records": records}
        params = {"user_id_type": user_id_type}
        if ignore_consistency_check:
            params["ignore_consistency_check"] = "true"

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
            params=params,
            json_data=payload,
        )

    def search_records(
        self,
        app_token: str,
        table_id: str,
        view_id: Optional[str] = None,
        field_names: Optional[list] = None,
        sort: Optional[list] = None,
        filter: Optional[dict] = None,
        page_token: Optional[str] = None,
        page_size: int = 20,
        user_id_type: str = "open_id",
        automatic_fields: bool = False,
    ) -> dict:
        """查询/搜索记录"""
        payload = {}
        if view_id:
            payload["view_id"] = view_id
        if field_names:
            payload["field_names"] = field_names
        if sort:
            payload["sort"] = sort
        if filter:
            payload["filter"] = filter
        if automatic_fields:
            payload["automatic_fields"] = automatic_fields

        params = {
            "page_size": min(page_size, 500),  # 最大500
            "user_id_type": user_id_type,
        }
        if page_token:
            params["page_token"] = page_token

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
            params=params,
            json_data=payload,
        )

    def batch_get_records(
        self,
        app_token: str,
        table_id: str,
        record_ids: list[str],
        user_id_type: str = "open_id",
        with_shared_url: bool = False,
        automatic_fields: bool = False,
    ) -> dict:
        """批量获取记录 (按record_id, 最多100条)"""
        payload = {
            "record_ids": record_ids,
            "user_id_type": user_id_type,
            "with_shared_url": with_shared_url,
            "automatic_fields": automatic_fields,
        }

        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_get",
            json_data=payload,
        )

    def delete_record(self, app_token: str, table_id: str, record_id: str) -> dict:
        """删除单条记录"""
        return self._request(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
        )

    def batch_delete_records(self, app_token: str, table_id: str, record_ids: list[str]) -> dict:
        """批量删除记录 (最多500条)"""
        return self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete",
            json_data={"records": record_ids},
        )


# 全局客户端实例
_client: Optional[FeishuBitableClient] = None


def get_client() -> FeishuBitableClient:
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = FeishuBitableClient()
    return _client


def reset_client():
    """重置客户端实例 (用于测试)"""
    global _client
    _client = None
