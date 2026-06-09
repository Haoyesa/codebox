"""
MCP 工具实现 - 字段 (Field) 级别
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

BITABLE_LIST_FIELDS = ToolDef(
    name="bitable_list_fields",
    description="获取指定数据表中的所有字段信息，包括字段ID、名称、类型和属性。支持分页获取大量字段。",
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
                "description": "视图ID，用于获取该视图可见的字段",
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
            "text_field_as_array": {
                "type": "boolean",
                "description": "字段描述是否以数组形式返回",
                "default": False,
            },
        },
        "required": ["app_token", "table_id"],
    },
)


BITABLE_CREATE_FIELD = ToolDef(
    name="bitable_create_field",
    description="在指定数据表中新增一个字段。需要先了解数据表结构再添加合适的字段类型。",
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
            "field_name": {
                "type": "string",
                "description": "字段名称",
            },
            "field_type": {
                "type": "integer",
                "description": "字段类型: 1-文本, 2-数字, 3-单选, 4-多选, 5-日期, 7-复选框, 11-人员, 13-电话, 15-超链接, 17-附件, 18-关联, 20-公式, 21-双向关联, 22-地理位置, 23-群组, 1001-创建时间, 1002-最后更新时间, 1003-创建人, 1004-修改人, 1005-自动编号",
            },
            "property": {
                "type": "object",
                "description": "字段属性配置",
            },
            "client_token": {
                "type": "string",
                "description": "幂等操作的唯一标识，uuidv4格式",
            },
        },
        "required": ["app_token", "table_id", "field_name", "field_type"],
    },
)


BITABLE_DELETE_FIELD = ToolDef(
    name="bitable_delete_field",
    description="删除指定数据表中的一个字段。索引列无法删除。",
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
            "field_id": {
                "type": "string",
                "description": "要删除的字段ID",
            },
        },
        "required": ["app_token", "table_id", "field_id"],
    },
)


# ============ 工具实现 ============

async def bitable_list_fields(
    app_token: str,
    table_id: str,
    view_id: Optional[str] = None,
    page_token: Optional[str] = None,
    page_size: int = 20,
    text_field_as_array: bool = False,
) -> dict:
    """列出字段"""
    client = get_client()
    result = client.list_fields(
        app_token=app_token,
        table_id=table_id,
        view_id=view_id,
        page_token=page_token,
        page_size=min(page_size, 100),
        text_field_as_array=text_field_as_array,
    )
    return _format_response(result)


async def bitable_create_field(
    app_token: str,
    table_id: str,
    field_name: str,
    field_type: int,
    property: Optional[dict] = None,
    client_token: Optional[str] = None,
) -> dict:
    """新增字段"""
    client = get_client()
    result = client.create_field(
        app_token=app_token,
        table_id=table_id,
        field_name=field_name,
        field_type=field_type,
        property=property,
        client_token=client_token,
    )
    return _format_response(result)


async def bitable_delete_field(
    app_token: str,
    table_id: str,
    field_id: str,
) -> dict:
    """删除字段"""
    client = get_client()
    result = client.delete_field(
        app_token=app_token,
        table_id=table_id,
        field_id=field_id,
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
