"""
MCP 工具实现 - 数据表 (Table) 级别
"""

from typing import Optional, Any
from dataclasses import dataclass

from ..client import get_client


@dataclass
class ToolDef:
    """工具定义"""
    name: str
    description: str
    inputSchema: dict


# ============ 工具定义 ============

BITABLE_CREATE_TABLE = ToolDef(
    name="bitable_create_table",
    description="在指定多维表格中新增一个数据表。新增的数据表仅包含索引列，字段需要单独添加。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "table_name": {
                "type": "string",
                "description": "数据表名称",
            },
            "default_view_name": {
                "type": "string",
                "description": "默认视图名称，默认为'表格视图'",
            },
            "fields": {
                "type": "array",
                "description": "初始字段配置列表",
            },
        },
        "required": ["app_token", "table_name"],
    },
)


BITABLE_BATCH_CREATE_TABLES = ToolDef(
    name="bitable_batch_create_tables",
    description="在指定多维表格中批量新增数据表，单次最多新增10个数据表。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "tables": {
                "type": "array",
                "description": "数据表配置列表，每个包含name和可选的fields",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "default_view_name": {"type": "string"},
                        "fields": {"type": "array"},
                    },
                    "required": ["name"],
                },
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型，open_id/union_id/user_id",
                "default": "open_id",
            },
        },
        "required": ["app_token", "tables"],
    },
)


BITABLE_LIST_TABLES = ToolDef(
    name="bitable_list_tables",
    description="列出指定多维表格中的所有数据表，支持分页。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "page_token": {
                "type": "string",
                "description": "分页标记，首次请求不填",
            },
            "page_size": {
                "type": "integer",
                "description": "分页大小，最大100",
                "default": 20,
            },
        },
        "required": ["app_token"],
    },
)


BITABLE_UPDATE_TABLE = ToolDef(
    name="bitable_update_table",
    description="更新指定数据表的名称。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "table_id": {
                "type": "string",
                "description": "数据表的唯一标识",
            },
            "name": {
                "type": "string",
                "description": "新的数据表名称",
            },
        },
        "required": ["app_token", "table_id", "name"],
    },
)


BITABLE_DELETE_TABLE = ToolDef(
    name="bitable_delete_table",
    description="删除指定多维表格中的一个数据表。删除后可在回收站恢复，30天后彻底删除。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "table_id": {
                "type": "string",
                "description": "数据表的唯一标识",
            },
        },
        "required": ["app_token", "table_id"],
    },
)


BITABLE_BATCH_DELETE_TABLES = ToolDef(
    name="bitable_batch_delete_tables",
    description="批量删除数据表，单次最多删除10个数据表。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "table_ids": {
                "type": "array",
                "description": "要删除的数据表ID列表",
                "items": {"type": "string"},
            },
        },
        "required": ["app_token", "table_ids"],
    },
)


# ============ 工具实现 ============

async def bitable_create_table(
    app_token: str,
    table_name: str,
    default_view_name: Optional[str] = None,
    fields: Optional[list] = None,
) -> dict:
    """新增数据表"""
    client = get_client()
    result = client.create_table(
        app_token=app_token,
        table_name=table_name,
        default_view_name=default_view_name,
        fields=fields,
    )
    return _format_response(result)


async def bitable_batch_create_tables(
    app_token: str,
    tables: list[dict],
    user_id_type: str = "open_id",
) -> dict:
    """批量新增数据表"""
    client = get_client()
    result = client.batch_create_tables(
        app_token=app_token,
        tables=tables,
        user_id_type=user_id_type,
    )
    return _format_response(result)


async def bitable_list_tables(
    app_token: str,
    page_token: Optional[str] = None,
    page_size: int = 20,
) -> dict:
    """列出数据表"""
    client = get_client()
    result = client.list_tables(
        app_token=app_token,
        page_token=page_token,
        page_size=min(page_size, 100),
    )
    return _format_response(result)


async def bitable_update_table(
    app_token: str,
    table_id: str,
    name: str,
) -> dict:
    """更新数据表"""
    client = get_client()
    result = client.update_table(
        app_token=app_token,
        table_id=table_id,
        name=name,
    )
    return _format_response(result)


async def bitable_delete_table(
    app_token: str,
    table_id: str,
) -> dict:
    """删除数据表"""
    client = get_client()
    result = client.delete_table(
        app_token=app_token,
        table_id=table_id,
    )
    return _format_response(result)


async def bitable_batch_delete_tables(
    app_token: str,
    table_ids: list[str],
) -> dict:
    """批量删除数据表"""
    client = get_client()
    result = client.batch_delete_tables(
        app_token=app_token,
        table_ids=table_ids,
    )
    return _format_response(result)


def _format_response(api_response: dict) -> dict:
    """格式化API响应"""
    if api_response.get("code") == 0:
        return {
            "success": True,
            "data": api_response.get("data", {}),
            "error": None,
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": {
                "code": api_response.get("code"),
                "message": api_response.get("msg", "Unknown error"),
            },
        }
