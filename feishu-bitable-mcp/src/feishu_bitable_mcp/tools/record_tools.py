"""
MCP 工具实现 - 记录 (Record) 级别
"""

from typing import Optional, Any, Union
from dataclasses import dataclass

from ..client import get_client


@dataclass
class ToolDef:
    """工具定义"""
    name: str
    description: str
    inputSchema: dict


# ============ 工具定义 ============

BITABLE_CREATE_RECORD = ToolDef(
    name="bitable_create_record",
    description="在指定数据表中新增一条记录。需要在多维表格有编辑权限。",
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
            "fields": {
                "type": "object",
                "description": "记录字段数据，key为字段名，value为字段值",
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型，open_id/union_id/user_id",
                "default": "open_id",
            },
            "client_token": {
                "type": "string",
                "description": "幂等操作标识，uuidv4格式",
            },
            "ignore_consistency_check": {
                "type": "boolean",
                "description": "是否忽略读写一致性检查",
                "default": False,
            },
        },
        "required": ["app_token", "table_id", "fields"],
    },
)


BITABLE_BATCH_CREATE_RECORDS = ToolDef(
    name="bitable_batch_create_records",
    description="批量新增记录，单次最多新增1000条记录。性能更好，推荐用于批量导入。",
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
            "records": {
                "type": "array",
                "description": "记录列表，每条记录包含fields字段",
                "items": {
                    "type": "object",
                    "properties": {
                        "fields": {
                            "type": "object",
                            "description": "记录字段数据",
                        },
                    },
                    "required": ["fields"],
                },
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型，open_id/union_id/user_id",
                "default": "open_id",
            },
            "client_token": {
                "type": "string",
                "description": "幂等操作标识，uuidv4格式",
            },
            "ignore_consistency_check": {
                "type": "boolean",
                "description": "是否忽略读写一致性检查",
                "default": False,
            },
        },
        "required": ["app_token", "table_id", "records"],
    },
)


BITABLE_UPDATE_RECORD = ToolDef(
    name="bitable_update_record",
    description="更新指定数据表中的单条记录。",
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
            "record_id": {
                "type": "string",
                "description": "要更新的记录ID",
            },
            "fields": {
                "type": "object",
                "description": "要更新的字段数据",
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型",
                "default": "open_id",
            },
            "ignore_consistency_check": {
                "type": "boolean",
                "description": "是否忽略读写一致性检查",
                "default": False,
            },
        },
        "required": ["app_token", "table_id", "record_id", "fields"],
    },
)


BITABLE_BATCH_UPDATE_RECORDS = ToolDef(
    name="bitable_batch_update_records",
    description="批量更新记录，单次最多更新1000条记录。",
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
            "records": {
                "type": "array",
                "description": "要更新的记录列表，每条包含record_id和fields",
                "items": {
                    "type": "object",
                    "properties": {
                        "record_id": {"type": "string"},
                        "fields": {"type": "object"},
                    },
                    "required": ["record_id", "fields"],
                },
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型",
                "default": "open_id",
            },
            "ignore_consistency_check": {
                "type": "boolean",
                "description": "是否忽略读写一致性检查",
                "default": False,
            },
        },
        "required": ["app_token", "table_id", "records"],
    },
)


BITABLE_SEARCH_RECORDS = ToolDef(
    name="bitable_search_records",
    description="搜索/查询记录。支持条件筛选、排序、分页获取数据表中的记录。",
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
            "view_id": {
                "type": "string",
                "description": "视图ID，使用视图的筛选和排序条件",
            },
            "field_names": {
                "type": "array",
                "description": "要返回的字段名称列表，不传则返回所有字段",
                "items": {"type": "string"},
            },
            "filter": {
                "type": "object",
                "description": "筛选条件",
            },
            "sort": {
                "type": "array",
                "description": "排序规则",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_name": {"type": "string"},
                        "desc": {"type": "boolean"},
                    },
                },
            },
            "page_token": {
                "type": "string",
                "description": "分页标记",
            },
            "page_size": {
                "type": "integer",
                "description": "分页大小，最大500",
                "default": 20,
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型",
                "default": "open_id",
            },
            "automatic_fields": {
                "type": "boolean",
                "description": "是否返回自动计算字段",
                "default": False,
            },
        },
        "required": ["app_token", "table_id"],
    },
)


BITABLE_BATCH_GET_RECORDS = ToolDef(
    name="bitable_batch_get_records",
    description="通过记录ID批量获取记录信息，最多获取100条记录。",
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
            "record_ids": {
                "type": "array",
                "description": "要获取的记录ID列表",
                "items": {"type": "string"},
            },
            "user_id_type": {
                "type": "string",
                "description": "用户ID类型",
                "default": "open_id",
            },
            "with_shared_url": {
                "type": "boolean",
                "description": "是否返回记录分享链接",
                "default": False,
            },
            "automatic_fields": {
                "type": "boolean",
                "description": "是否返回自动计算字段",
                "default": False,
            },
        },
        "required": ["app_token", "table_id", "record_ids"],
    },
)


BITABLE_DELETE_RECORD = ToolDef(
    name="bitable_delete_record",
    description="删除指定数据表中的单条记录。",
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
            "record_id": {
                "type": "string",
                "description": "要删除的记录ID",
            },
        },
        "required": ["app_token", "table_id", "record_id"],
    },
)


BITABLE_BATCH_DELETE_RECORDS = ToolDef(
    name="bitable_batch_delete_records",
    description="批量删除记录，单次最多删除500条记录。",
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
            "record_ids": {
                "type": "array",
                "description": "要删除的记录ID列表",
                "items": {"type": "string"},
            },
        },
        "required": ["app_token", "table_id", "record_ids"],
    },
)


# ============ 工具实现 ============

async def bitable_create_record(
    app_token: str,
    table_id: str,
    fields: dict,
    user_id_type: str = "open_id",
    client_token: Optional[str] = None,
    ignore_consistency_check: bool = False,
) -> dict:
    """新增单条记录"""
    client = get_client()
    result = client.create_record(
        app_token=app_token,
        table_id=table_id,
        fields=fields,
        user_id_type=user_id_type,
        client_token=client_token,
        ignore_consistency_check=ignore_consistency_check,
    )
    return _format_response(result)


async def bitable_batch_create_records(
    app_token: str,
    table_id: str,
    records: list[dict],
    user_id_type: str = "open_id",
    client_token: Optional[str] = None,
    ignore_consistency_check: bool = False,
) -> dict:
    """批量新增记录"""
    client = get_client()
    result = client.batch_create_records(
        app_token=app_token,
        table_id=table_id,
        records=records,
        user_id_type=user_id_type,
        client_token=client_token,
        ignore_consistency_check=ignore_consistency_check,
    )
    return _format_response(result)


async def bitable_update_record(
    app_token: str,
    table_id: str,
    record_id: str,
    fields: dict,
    user_id_type: str = "open_id",
    ignore_consistency_check: bool = False,
) -> dict:
    """更新单条记录"""
    client = get_client()
    result = client.update_record(
        app_token=app_token,
        table_id=table_id,
        record_id=record_id,
        fields=fields,
        user_id_type=user_id_type,
        ignore_consistency_check=ignore_consistency_check,
    )
    return _format_response(result)


async def bitable_batch_update_records(
    app_token: str,
    table_id: str,
    records: list[dict],
    user_id_type: str = "open_id",
    ignore_consistency_check: bool = False,
) -> dict:
    """批量更新记录"""
    client = get_client()
    result = client.batch_update_records(
        app_token=app_token,
        table_id=table_id,
        records=records,
        user_id_type=user_id_type,
        ignore_consistency_check=ignore_consistency_check,
    )
    return _format_response(result)


async def bitable_search_records(
    app_token: str,
    table_id: str,
    view_id: Optional[str] = None,
    field_names: Optional[list] = None,
    filter: Optional[dict] = None,
    sort: Optional[list] = None,
    page_token: Optional[str] = None,
    page_size: int = 20,
    user_id_type: str = "open_id",
    automatic_fields: bool = False,
) -> dict:
    """搜索记录"""
    client = get_client()
    result = client.search_records(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        field_names=field_names,
        sort=sort,
        filter=filter,
        page_token=page_token,
        page_size=min(page_size, 500),
        user_id_type=user_id_type,
        automatic_fields=automatic_fields,
    )
    return _format_response(result)


async def bitable_batch_get_records(
    app_token: str,
    table_id: str,
    record_ids: list[str],
    user_id_type: str = "open_id",
    with_shared_url: bool = False,
    automatic_fields: bool = False,
) -> dict:
    """批量获取记录"""
    client = get_client()
    result = client.batch_get_records(
        app_token=app_token,
        table_id=table_id,
        record_ids=record_ids,
        user_id_type=user_id_type,
        with_shared_url=with_shared_url,
        automatic_fields=automatic_fields,
    )
    return _format_response(result)


async def bitable_delete_record(
    app_token: str,
    table_id: str,
    record_id: str,
) -> dict:
    """删除单条记录"""
    client = get_client()
    result = client.delete_record(
        app_token=app_token,
        table_id=table_id,
        record_id=record_id,
    )
    return _format_response(result)


async def bitable_batch_delete_records(
    app_token: str,
    table_id: str,
    record_ids: list[str],
) -> dict:
    """批量删除记录"""
    client = get_client()
    result = client.batch_delete_records(
        app_token=app_token,
        table_id=table_id,
        record_ids=record_ids,
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
