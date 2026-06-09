"""
飞书多维表格 MCP Server 主入口
"""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import FeishuBitableClient
from .tools import (
    # App tools
    BITABLE_CREATE_APP,
    BITABLE_GET_APP,
    BITABLE_UPDATE_APP,
    BITABLE_COPY_APP,
    bitable_create_app,
    bitable_get_app,
    bitable_update_app,
    bitable_copy_app,
    # Table tools
    BITABLE_CREATE_TABLE,
    BITABLE_BATCH_CREATE_TABLES,
    BITABLE_LIST_TABLES,
    BITABLE_UPDATE_TABLE,
    BITABLE_DELETE_TABLE,
    BITABLE_BATCH_DELETE_TABLES,
    bitable_create_table,
    bitable_batch_create_tables,
    bitable_list_tables,
    bitable_update_table,
    bitable_delete_table,
    bitable_batch_delete_tables,
    # Field tools
    BITABLE_LIST_FIELDS,
    BITABLE_CREATE_FIELD,
    BITABLE_DELETE_FIELD,
    bitable_list_fields,
    bitable_create_field,
    bitable_delete_field,
    # Record tools
    BITABLE_CREATE_RECORD,
    BITABLE_BATCH_CREATE_RECORDS,
    BITABLE_UPDATE_RECORD,
    BITABLE_BATCH_UPDATE_RECORDS,
    BITABLE_SEARCH_RECORDS,
    BITABLE_BATCH_GET_RECORDS,
    BITABLE_DELETE_RECORD,
    BITABLE_BATCH_DELETE_RECORDS,
    bitable_create_record,
    bitable_batch_create_records,
    bitable_update_record,
    bitable_batch_update_records,
    bitable_search_records,
    bitable_batch_get_records,
    bitable_delete_record,
    bitable_batch_delete_records,
)


# 创建MCP服务器实例
app = Server("feishu-bitable-mcp")

# 工具列表
TOOLS = [
    # App tools
    Tool(
        name=BITABLE_CREATE_APP.name,
        description=BITABLE_CREATE_APP.description,
        inputSchema=BITABLE_CREATE_APP.inputSchema,
    ),
    Tool(
        name=BITABLE_GET_APP.name,
        description=BITABLE_GET_APP.description,
        inputSchema=BITABLE_GET_APP.inputSchema,
    ),
    Tool(
        name=BITABLE_UPDATE_APP.name,
        description=BITABLE_UPDATE_APP.description,
        inputSchema=BITABLE_UPDATE_APP.inputSchema,
    ),
    Tool(
        name=BITABLE_COPY_APP.name,
        description=BITABLE_COPY_APP.description,
        inputSchema=BITABLE_COPY_APP.inputSchema,
    ),
    # Table tools
    Tool(
        name=BITABLE_CREATE_TABLE.name,
        description=BITABLE_CREATE_TABLE.description,
        inputSchema=BITABLE_CREATE_TABLE.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_CREATE_TABLES.name,
        description=BITABLE_BATCH_CREATE_TABLES.description,
        inputSchema=BITABLE_BATCH_CREATE_TABLES.inputSchema,
    ),
    Tool(
        name=BITABLE_LIST_TABLES.name,
        description=BITABLE_LIST_TABLES.description,
        inputSchema=BITABLE_LIST_TABLES.inputSchema,
    ),
    Tool(
        name=BITABLE_UPDATE_TABLE.name,
        description=BITABLE_UPDATE_TABLE.description,
        inputSchema=BITABLE_UPDATE_TABLE.inputSchema,
    ),
    Tool(
        name=BITABLE_DELETE_TABLE.name,
        description=BITABLE_DELETE_TABLE.description,
        inputSchema=BITABLE_DELETE_TABLE.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_DELETE_TABLES.name,
        description=BITABLE_BATCH_DELETE_TABLES.description,
        inputSchema=BITABLE_BATCH_DELETE_TABLES.inputSchema,
    ),
    # Field tools
    Tool(
        name=BITABLE_LIST_FIELDS.name,
        description=BITABLE_LIST_FIELDS.description,
        inputSchema=BITABLE_LIST_FIELDS.inputSchema,
    ),
    Tool(
        name=BITABLE_CREATE_FIELD.name,
        description=BITABLE_CREATE_FIELD.description,
        inputSchema=BITABLE_CREATE_FIELD.inputSchema,
    ),
    Tool(
        name=BITABLE_DELETE_FIELD.name,
        description=BITABLE_DELETE_FIELD.description,
        inputSchema=BITABLE_DELETE_FIELD.inputSchema,
    ),
    # Record tools
    Tool(
        name=BITABLE_CREATE_RECORD.name,
        description=BITABLE_CREATE_RECORD.description,
        inputSchema=BITABLE_CREATE_RECORD.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_CREATE_RECORDS.name,
        description=BITABLE_BATCH_CREATE_RECORDS.description,
        inputSchema=BITABLE_BATCH_CREATE_RECORDS.inputSchema,
    ),
    Tool(
        name=BITABLE_UPDATE_RECORD.name,
        description=BITABLE_UPDATE_RECORD.description,
        inputSchema=BITABLE_UPDATE_RECORD.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_UPDATE_RECORDS.name,
        description=BITABLE_BATCH_UPDATE_RECORDS.description,
        inputSchema=BITABLE_BATCH_UPDATE_RECORDS.inputSchema,
    ),
    Tool(
        name=BITABLE_SEARCH_RECORDS.name,
        description=BITABLE_SEARCH_RECORDS.description,
        inputSchema=BITABLE_SEARCH_RECORDS.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_GET_RECORDS.name,
        description=BITABLE_BATCH_GET_RECORDS.description,
        inputSchema=BITABLE_BATCH_GET_RECORDS.inputSchema,
    ),
    Tool(
        name=BITABLE_DELETE_RECORD.name,
        description=BITABLE_DELETE_RECORD.description,
        inputSchema=BITABLE_DELETE_RECORD.inputSchema,
    ),
    Tool(
        name=BITABLE_BATCH_DELETE_RECORDS.name,
        description=BITABLE_BATCH_DELETE_RECORDS.description,
        inputSchema=BITABLE_BATCH_DELETE_RECORDS.inputSchema,
    ),
]


@app.list_tools()
async def list_tools():
    """列出所有可用工具"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    try:
        # App tools
        if name == "bitable_create_app":
            result = await bitable_create_app(
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token"),
                time_zone=arguments.get("time_zone"),
            )
        elif name == "bitable_get_app":
            result = await bitable_get_app(app_token=arguments["app_token"])
        elif name == "bitable_update_app":
            result = await bitable_update_app(
                app_token=arguments["app_token"],
                name=arguments.get("name"),
                is_advanced=arguments.get("is_advanced"),
            )
        elif name == "bitable_copy_app":
            result = await bitable_copy_app(
                app_token=arguments["app_token"],
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token"),
                without_content=arguments.get("without_content", False),
                time_zone=arguments.get("time_zone"),
            )
        # Table tools
        elif name == "bitable_create_table":
            result = await bitable_create_table(
                app_token=arguments["app_token"],
                table_name=arguments["table_name"],
                default_view_name=arguments.get("default_view_name"),
                fields=arguments.get("fields"),
            )
        elif name == "bitable_batch_create_tables":
            result = await bitable_batch_create_tables(
                app_token=arguments["app_token"],
                tables=arguments["tables"],
                user_id_type=arguments.get("user_id_type", "open_id"),
            )
        elif name == "bitable_list_tables":
            result = await bitable_list_tables(
                app_token=arguments["app_token"],
                page_token=arguments.get("page_token"),
                page_size=arguments.get("page_size", 20),
            )
        elif name == "bitable_update_table":
            result = await bitable_update_table(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                name=arguments["name"],
            )
        elif name == "bitable_delete_table":
            result = await bitable_delete_table(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
            )
        elif name == "bitable_batch_delete_tables":
            result = await bitable_batch_delete_tables(
                app_token=arguments["app_token"],
                table_ids=arguments["table_ids"],
            )
        # Field tools
        elif name == "bitable_list_fields":
            result = await bitable_list_fields(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                view_id=arguments.get("view_id"),
                page_token=arguments.get("page_token"),
                page_size=arguments.get("page_size", 20),
                text_field_as_array=arguments.get("text_field_as_array", False),
            )
        elif name == "bitable_create_field":
            result = await bitable_create_field(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                field_name=arguments["field_name"],
                field_type=arguments["field_type"],
                property=arguments.get("property"),
                client_token=arguments.get("client_token"),
            )
        elif name == "bitable_delete_field":
            result = await bitable_delete_field(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                field_id=arguments["field_id"],
            )
        # Record tools
        elif name == "bitable_create_record":
            result = await bitable_create_record(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                fields=arguments["fields"],
                user_id_type=arguments.get("user_id_type", "open_id"),
                client_token=arguments.get("client_token"),
                ignore_consistency_check=arguments.get("ignore_consistency_check", False),
            )
        elif name == "bitable_batch_create_records":
            result = await bitable_batch_create_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                records=arguments["records"],
                user_id_type=arguments.get("user_id_type", "open_id"),
                client_token=arguments.get("client_token"),
                ignore_consistency_check=arguments.get("ignore_consistency_check", False),
            )
        elif name == "bitable_update_record":
            result = await bitable_update_record(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                record_id=arguments["record_id"],
                fields=arguments["fields"],
                user_id_type=arguments.get("user_id_type", "open_id"),
                ignore_consistency_check=arguments.get("ignore_consistency_check", False),
            )
        elif name == "bitable_batch_update_records":
            result = await bitable_batch_update_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                records=arguments["records"],
                user_id_type=arguments.get("user_id_type", "open_id"),
                ignore_consistency_check=arguments.get("ignore_consistency_check", False),
            )
        elif name == "bitable_search_records":
            result = await bitable_search_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                view_id=arguments.get("view_id"),
                field_names=arguments.get("field_names"),
                filter=arguments.get("filter"),
                sort=arguments.get("sort"),
                page_token=arguments.get("page_token"),
                page_size=arguments.get("page_size", 20),
                user_id_type=arguments.get("user_id_type", "open_id"),
                automatic_fields=arguments.get("automatic_fields", False),
            )
        elif name == "bitable_batch_get_records":
            result = await bitable_batch_get_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                record_ids=arguments["record_ids"],
                user_id_type=arguments.get("user_id_type", "open_id"),
                with_shared_url=arguments.get("with_shared_url", False),
                automatic_fields=arguments.get("automatic_fields", False),
            )
        elif name == "bitable_delete_record":
            result = await bitable_delete_record(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                record_id=arguments["record_id"],
            )
        elif name == "bitable_batch_delete_records":
            result = await bitable_batch_delete_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                record_ids=arguments["record_ids"],
            )
        else:
            return [TextContent(type="text", text=f"错误: 未知工具 '{name}'")]

        # 返回结果
        if result.get("success"):
            content = result.get("data", {})
        else:
            error = result.get("error", {})
            content = {"error": f"[{error.get('code')}] {error.get('message')}"}

        return [TextContent(type="text", text=str(content))]

    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]


async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def run():
    """运行服务器"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
