"""
飞书多维表格 MCP Server
"""

__version__ = "0.1.0"

from .client import FeishuBitableClient, get_client, reset_client

__all__ = [
    "__version__",
    "FeishuBitableClient",
    "get_client",
    "reset_client",
]
