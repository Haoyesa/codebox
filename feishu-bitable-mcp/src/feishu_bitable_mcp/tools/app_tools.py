"""
MCP 工具实现 - 多维表格 (App) 级别
"""

from typing import Optional
from dataclasses import dataclass

from ..client import get_client


@dataclass
class ToolDef:
    """工具定义"""
    name: str
    description: str
    inputSchema: dict


# ============ 工具定义 ============

BITABLE_CREATE_APP = ToolDef(
    name="bitable_create_app",
    description="创建新的多维表格。需要在云空间文件夹中有创建权限。",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "多维表格名称，最长255个字符",
            },
            "folder_token": {
                "type": "string",
                "description": "多维表格归属文件夹的token，默认为云空间根目录",
            },
            "time_zone": {
                "type": "string",
                "description": "文档时区，如 'Asia/Shanghai'",
            },
        },
        "required": [],
    },
)


BITABLE_GET_APP = ToolDef(
    name="bitable_get_app",
    description="获取指定多维表格的元数据信息，包括名称、版本号、是否开启高级权限等。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识，从URL中获取或通过API获取",
            },
        },
        "required": ["app_token"],
    },
)


BITABLE_UPDATE_APP = ToolDef(
    name="bitable_update_app",
    description="更新多维表格的名称或高级权限设置。此操作仅支持存储在云空间文件夹中的多维表格。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "多维表格的唯一标识",
            },
            "name": {
                "type": "string",
                "description": "新的多维表格名称，不传则不更新",
            },
            "is_advanced": {
                "type": "boolean",
                "description": "是否开启高级权限，不传则不更新",
            },
        },
        "required": ["app_token"],
    },
)


BITABLE_COPY_APP = ToolDef(
    name="bitable_copy_app",
    description="复制一个多维表格到指定文件夹。当记录数超过50,000条时，仅可复制结构。",
    inputSchema={
        "type": "object",
        "properties": {
            "app_token": {
                "type": "string",
                "description": "要复制的多维表格app_token",
            },
            "name": {
                "type": "string",
                "description": "新多维表格的名称",
            },
            "folder_token": {
                "type": "string",
                "description": "目标文件夹的token",
            },
            "without_content": {
                "type": "boolean",
                "description": "是否只复制结构不复制内容，默认false",
            },
            "time_zone": {
                "type": "string",
                "description": "文档时区",
            },
        },
        "required": ["app_token"],
    },
)


# ============ 工具实现 ============

async def bitable_create_app(
    name: Optional[str] = None,
    folder_token: Optional[str] = None,
    time_zone: Optional[str] = None,
) -> dict:
    """创建新的多维表格"""
    client = get_client()
    result = client.create_app(
        name=name,
        folder_token=folder_token,
        time_zone=time_zone,
    )
    return _format_response(result)


async def bitable_get_app(app_token: str) -> dict:
    """获取多维表格元数据"""
    client = get_client()
    result = client.get_app(app_token)
    return _format_response(result)


async def bitable_update_app(
    app_token: str,
    name: Optional[str] = None,
    is_advanced: Optional[bool] = None,
) -> dict:
    """更新多维表格"""
    client = get_client()
    result = client.update_app(
        app_token=app_token,
        name=name,
        is_advanced=is_advanced,
    )
    return _format_response(result)


async def bitable_copy_app(
    app_token: str,
    name: Optional[str] = None,
    folder_token: Optional[str] = None,
    without_content: bool = False,
    time_zone: Optional[str] = None,
) -> dict:
    """复制多维表格"""
    client = get_client()
    result = client.copy_app(
        app_token=app_token,
        name=name,
        folder_token=folder_token,
        without_content=without_content,
        time_zone=time_zone,
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
