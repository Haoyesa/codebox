#!/usr/bin/env python3
"""Bit Browser Management Tools

This module provides Bit Browser connection and management through the DevTools Protocol.
It handles browser connection, navigation, and session management specifically optimized
for Bit Browser (比特浏览器) integration.

The tools support Bit Browser Local API integration with automatic page target detection
and connection. All operations include error handling and status reporting.

Key Features:
    - Bit Browser Local API integration
    - Automatic page target detection and connection
    - Connection management with status monitoring
    - URL navigation and session control
    - Multi-instance support

Example:
    Connecting to Bit Browser:

    ```python
    # Connect to Bit Browser instance
    result = await connect_to_browser()

    # Navigate to a specific URL
    if result['success']:
        await navigate_to_url('https://example.com')
    ```
"""

from __future__ import annotations

import asyncio
import os
import platform
import subprocess
from typing import Any

import aiohttp
import logging
from mcp.server.fastmcp import FastMCP

from ..cdp_context import require_cdp_client
from .utils import create_error_response, create_success_response

logger = logging.getLogger(__name__)

# HTTP请求超时配置
HTTP_TOTAL_TIMEOUT = 30.0
HTTP_CONNECT_TIMEOUT = 10.0
HTTP_READ_TIMEOUT = 10.0

# WebSocket连接超时配置
WEBSOCKET_OPEN_TIMEOUT = 10.0
WEBSOCKET_CLOSE_TIMEOUT = 10.0
WEBSOCKET_PING_INTERVAL = 20
WEBSOCKET_PING_TIMEOUT = 10
WEBSOCKET_MAX_SIZE = 10 * 1024 * 1024

# 目标等待配置
TARGET_WAIT_MAX_TIMEOUT = 10.0
TARGET_WAIT_INTERVAL = 0.5


# Removed Chrome executable detection and startup functions
# This server is now dedicated to Bit Browser integration only


def register_chrome_tools(mcp: FastMCP) -> None:
    """Register Bit Browser management tools with the MCP server.

    Adds Bit Browser connection and management functions as MCP tools, including
    connection management, navigation, and status monitoring. Each tool provides
    detailed error handling and standardised response formatting.

    The registered tools support Bit Browser automation workflow:
    - Connection to Bit Browser instances via Local API
    - URL navigation and page control
    - Status monitoring and disconnection handling

    Args:
        mcp: FastMCP server instance to register tools with. Must be properly
             initialised before calling this function.

    Registered Tools:
        - connect_to_browser: Connect to Bit Browser instance
        - connect_to_bitbrowser: Explicitly connect to Bit Browser with instance ID
        - navigate_to_url: Navigate to specific URLs
        - disconnect_from_browser: Clean session termination
        - get_connection_status: Status monitoring and diagnostics

    Note:
        All tools require access to the global CDP client instance for operation.
        Tools will return appropriate error responses if the client is unavailable.

        This server is optimized for Bit Browser integration. Chrome startup
        functionality has been removed to focus on Bit Browser use cases.
    """

    # Removed start_chrome and start_chrome_and_connect functions
    # This server now focuses exclusively on Bit Browser integration

    @mcp.tool()
    async def connect_to_browser(port: int = 9222) -> dict[str, Any]:
        """Connect to Bit Browser with remote debugging enabled.

        Establishes a connection to a Bit Browser instance that's already running.
        Uses the Bit Browser Local API to open the specified browser instance and
        automatically connects to the correct page target.

        This function is the primary way to connect to Bit Browser. It handles all
        the complexity of finding and connecting to the correct page target automatically.

        Args:
            port: TCP port parameter (ignored for Bit Browser, kept for compatibility).
                  The actual port is obtained from the Bit Browser API.

        Returns:
            Connection status dictionary containing:
            - success: Boolean indicating connection success
            - message: Human-readable status description
            - data: Connection details including:
                - connected: Boolean connection status
                - bitBrowserId: Browser instance ID
                - targetInfo: Browser version and capability information

        Environment Variables:
            - BIT_BROWSER_MODE: Must be set to "true" (default for this server)
            - BIT_BROWSER_ID: Browser instance ID (e.g., "63de02b1ebb34145b7b7886294821a72")
            - BIT_BROWSER_API_PORT: Bit Browser Local API port (default: 54345)
            - BIT_BROWSER_API_HOST: Bit Browser Local API host (default: localhost)

        Note:
            The browser instance must exist and be accessible through the Bit Browser
            Local API. Make sure Bit Browser is running and the Local API is enabled.
        """
        from .. import main

        cdp_client = main.cdp_client

        if not cdp_client:
            return create_error_response("CDP client not initialised")

        try:
            # This server only supports Bit Browser mode
            if not cdp_client.bit_browser_mode:
                return create_error_response(
                    "Bit Browser mode not enabled",
                    "Set BIT_BROWSER_MODE=true environment variable"
                )

            if not cdp_client.bit_browser_id:
                return create_error_response(
                    "BIT_BROWSER_ID not set",
                    "Set BIT_BROWSER_ID environment variable to your browser instance ID"
                )

            connected = await cdp_client.connect()
            if not connected:
                return create_error_response(
                    f"Failed to connect to Bit Browser instance {cdp_client.bit_browser_id}",
                    "Check that Bit Browser Local API is running and the browser instance exists"
                )

            await cdp_client.enable_domains()
            target_info = await cdp_client.get_target_info()

            return create_success_response(
                message=f"Connected to Bit Browser instance {cdp_client.bit_browser_id}",
                data={
                    "connected": True,
                    "bitBrowserId": cdp_client.bit_browser_id,
                    "targetInfo": target_info
                },
            )

        except Exception as e:
            return create_error_response(f"Connection error: {e}")

    @mcp.tool()
    async def connect_to_bitbrowser(browser_id: str | None = None) -> dict[str, Any]:
        """Connect specifically to a Bit Browser instance using the Local API.

        This tool provides a direct way to connect to a specific Bit Browser instance
        by calling the Bit Browser Local API. It's useful when you want to override
        the environment variable configuration or connect to a different browser instance.

        Args:
            browser_id: Bit Browser instance ID. If not provided, uses BIT_BROWSER_ID
                       environment variable. Example: "63de02b1ebb34145b7b7886294821a72"

        Returns:
            Connection status dictionary containing:
            - success: Boolean indicating connection success
            - message: Human-readable status description
            - data: Connection details including:
                - connected: Boolean connection status
                - bitBrowserId: The browser instance ID used
                - connectionInfo: Raw response from Bit Browser API
                - targetInfo: Browser version and capability information

        Environment Variables:
            - BIT_BROWSER_API_PORT: Bit Browser Local API port (default: 54345)
            - BIT_BROWSER_API_HOST: Bit Browser Local API host (default: localhost)
            - BIT_BROWSER_ID: Default browser instance ID (used if browser_id not provided)

        Note:
            This tool temporarily enables Bit Browser mode for the connection, regardless
            of the BIT_BROWSER_MODE environment variable setting. The browser instance
            must exist and be accessible through the Bit Browser Local API.
        """
        import asyncio
        import websockets
        from .. import main

        cdp_client = main.cdp_client

        if not cdp_client:
            return create_error_response("CDP client not initialised")

        # Use provided browser_id or fall back to environment variable
        target_browser_id = browser_id or os.getenv("BIT_BROWSER_ID", "")
        if not target_browser_id:
            return create_error_response(
                "Browser ID required",
                "Provide browser_id parameter or set BIT_BROWSER_ID environment variable"
            )

        # Store original settings before trying to connect
        original_mode = cdp_client.bit_browser_mode
        original_id = cdp_client.bit_browser_id

        try:
            # Temporarily enable Bit Browser mode and set the browser ID
            cdp_client.bit_browser_mode = True
            cdp_client.bit_browser_id = target_browser_id

            # Get connection info from Bit Browser API
            connection_info = await cdp_client._call_bitbrowser_api()
            if not connection_info:
                return create_error_response(
                    f"Failed to get connection info for Bit Browser instance {target_browser_id}",
                    "Check that Bit Browser Local API is running and the browser instance exists"
                )

            # Extract HTTP address from connection info
            http_address = connection_info.get("http", "")
            logger.info(f"Bit Browser HTTP debug address: {http_address}")

            # Try to get existing page targets
            # This is the correct way to connect to page-level targets in Bit Browser
            import aiohttp
            try:
                timeout = aiohttp.ClientTimeout(
                    total=HTTP_TOTAL_TIMEOUT,
                    connect=HTTP_CONNECT_TIMEOUT,
                    sock_read=HTTP_READ_TIMEOUT
                )
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(f"http://{http_address}/json") as response:
                        if response.status == 200:
                            targets = await response.json()
                            logger.info(f"Found {len(targets)} targets from HTTP endpoint")

                            # Log all targets for debugging
                            for t in targets:
                                logger.debug(f"Target: type={t.get('type')}, title={t.get('title', 'N/A')}, url={t.get('url', 'N/A')}")

                            page_targets = [t for t in targets if t.get("type") == "page"]
                            logger.info(f"Found {len(page_targets)} page targets")

                            if page_targets:
                                # Connect to the first page target
                                target = page_targets[0]
                                ws_url = target["webSocketDebuggerUrl"]
                                logger.info(f"Connecting to page target WebSocket: {ws_url}")
                                cdp_client.ws = await websockets.connect(
                                    ws_url,
                                    ping_interval=WEBSOCKET_PING_INTERVAL,
                                    ping_timeout=WEBSOCKET_PING_TIMEOUT,
                                    close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                                    max_size=WEBSOCKET_MAX_SIZE,
                                    open_timeout=WEBSOCKET_OPEN_TIMEOUT
                                )
                                cdp_client.connected = True
                                asyncio.create_task(cdp_client._handle_incoming_messages())
                                await cdp_client.enable_domains()
                                target_info = await cdp_client.get_target_info()
                                target_type = await cdp_client.get_target_type()

                                logger.info(f"✅ Connected to existing page target: {target.get('title', 'Unknown')}")
                                return create_success_response(
                                    message=f"Connected to Bit Browser instance {target_browser_id} (page target)",
                                    data={
                                        "connected": True,
                                        "bitBrowserId": target_browser_id,
                                        "connectionInfo": connection_info,
                                        "targetInfo": target_info,
                                        "targetType": target_type
                                    },
                                )
            except Exception as e:
                logger.warning(f"Could not get page targets from HTTP endpoint: {e}")
                import traceback
                logger.debug(traceback.format_exc())

            # If no page targets found, connect to browser target and create a new page
            logger.info("No existing page targets found, creating a new one...")
            ws_url = connection_info["ws"]
            logger.info(f"Connecting to browser target WebSocket: {ws_url}")
            cdp_client.ws = await websockets.connect(
                ws_url,
                ping_interval=WEBSOCKET_PING_INTERVAL,
                ping_timeout=WEBSOCKET_PING_TIMEOUT,
                close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                max_size=WEBSOCKET_MAX_SIZE,
                open_timeout=WEBSOCKET_OPEN_TIMEOUT
            )
            cdp_client.connected = True
            asyncio.create_task(cdp_client._handle_incoming_messages())

            # Create a new page target
            try:
                logger.info("Creating new page target with Target.createTarget...")
                result = await cdp_client.send_command("Target.createTarget", {"url": "about:blank"})
                logger.debug(f"Target.createTarget result: {result}")

                if result and "targetId" in result:
                    target_id = result["targetId"]
                    logger.info(f"Created new page target: {target_id}")

                    # Wait for target to be ready using polling
                    logger.info(f"Waiting for target {target_id} to be ready...")
                    start_time = asyncio.get_event_loop().time()
                    ready_target = None

                    timeout = aiohttp.ClientTimeout(
                        total=HTTP_TOTAL_TIMEOUT,
                        connect=HTTP_CONNECT_TIMEOUT,
                        sock_read=HTTP_READ_TIMEOUT
                    )

                    while asyncio.get_event_loop().time() - start_time < TARGET_WAIT_MAX_TIMEOUT:
                        try:
                            async with aiohttp.ClientSession(timeout=timeout) as session:
                                async with session.get(f"http://{http_address}/json") as response:
                                    if response.status == 200:
                                        targets = await response.json()
                                        logger.debug(f"Polling: Found {len(targets)} targets")

                                        for t in targets:
                                            # Try both 'id' and 'targetId' fields
                                            t_id = t.get("id") or t.get("targetId")
                                            if t_id == target_id and t.get("type") == "page":
                                                ready_target = t
                                                break

                                        if ready_target:
                                            break
                        except Exception as e:
                            logger.debug(f"Error polling for target: {e}")

                        await asyncio.sleep(TARGET_WAIT_INTERVAL)

                    if ready_target:
                        page_ws_url = ready_target.get("webSocketDebuggerUrl")
                        if page_ws_url:
                            logger.info(f"Found new page target, switching connection to: {page_ws_url}")
                            # Close browser connection with timeout protection
                            try:
                                await asyncio.wait_for(cdp_client.ws.close(), timeout=WEBSOCKET_CLOSE_TIMEOUT)
                            except asyncio.TimeoutError:
                                logger.warning("Timeout closing browser WebSocket")
                            except Exception as e:
                                logger.warning(f"Error closing browser WebSocket: {e}")

                            cdp_client.ws = await websockets.connect(
                                page_ws_url,
                                ping_interval=WEBSOCKET_PING_INTERVAL,
                                ping_timeout=WEBSOCKET_PING_TIMEOUT,
                                close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                                max_size=WEBSOCKET_MAX_SIZE,
                                open_timeout=WEBSOCKET_OPEN_TIMEOUT
                            )
                            asyncio.create_task(cdp_client._handle_incoming_messages())
                            logger.info(f"✅ Connected to new page target: {target_id}")
                    else:
                        logger.warning(f"Could not find page target with ID {target_id} after waiting")
            except Exception as e:
                logger.error(f"Failed to create page target: {e}")
                import traceback
                logger.debug(traceback.format_exc())

            await cdp_client.enable_domains()
            target_info = await cdp_client.get_target_info()
            target_type = await cdp_client.get_target_type()

            if target_type == "browser":
                logger.warning("⚠️ Connected to browser-level target. Some CDP domains may not be available.")

            # Success - keep the current state and return
            return create_success_response(
                message=f"Connected to Bit Browser instance {target_browser_id} ({target_type} target)",
                data={
                    "connected": True,
                    "bitBrowserId": target_browser_id,
                    "connectionInfo": connection_info,
                    "targetInfo": target_info,
                    "targetType": target_type
                },
            )

        except Exception as e:
            logger.error(f"Bit Browser connection error: {e}")
            return create_error_response(f"Bit Browser connection error: {e}")
        finally:
            # Only restore original settings if connection failed or we're returning with error
            # If connection succeeded, we keep the new state
            if not cdp_client.connected:
                logger.debug("Connection failed, restoring original settings")
                cdp_client.bit_browser_mode = original_mode
                cdp_client.bit_browser_id = original_id

    @mcp.tool()
    @require_cdp_client
    async def navigate_to_url(url: str, **kwargs: Any) -> dict[str, Any]:
        """Navigate the connected browser to a specific URL.

        Instructs the currently connected Chrome instance to navigate to the specified
        URL. The function waits briefly for the navigation to begin before returning.
        Requires an active connection to Chrome established via connect_to_browser
        or start_chrome with auto_connect.

        Args:
            url: Target URL to navigate to. Must be a valid URL that Chrome can load,
                 including HTTP/HTTPS websites, local file paths, or data URIs.

        Returns:
            Navigation status dictionary containing:
            - success: Boolean indicating navigation success
            - message: Human-readable status description
            - data: Navigation details including:
                - url: The URL navigated to
                - navigated: Boolean navigation status

        Note:
            The function returns immediately after initiating navigation and doesn't
            wait for the page to fully load. Use additional tools to monitor page
            load completion if needed.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            await cdp_client.send_command("Page.navigate", {"url": url})
            await asyncio.sleep(1)

            return create_success_response(
                message=f"Navigated to {url}", data={"url": url, "navigated": True}
            )

        except Exception as e:
            return create_error_response(f"Navigation error: {e}")

    @mcp.tool()
    @require_cdp_client
    async def disconnect_from_browser(**kwargs: Any) -> dict[str, Any]:
        """Disconnect from the current browser session.

        Cleanly terminates the connection to the Chrome browser instance while
        leaving the browser running. This is useful for releasing resources or
        preparing to connect to a different browser instance.

        The browser will continue running after disconnection, but will no longer
        be controllable through this client until a new connection is established.

        Returns:
            Disconnection status dictionary containing:
            - success: Boolean indicating disconnection success
            - message: Human-readable status description
            - data: Disconnection details including:
                - connected: Boolean status (should be False after disconnect)

        Note:
            This function only disconnects the client from Chrome; it doesn't
            close or terminate the browser process itself.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            await cdp_client.disconnect()
            return create_success_response(
                message="Disconnected from browser", data={"connected": False}
            )

        except Exception as e:
            return create_error_response(f"Disconnection error: {e}")

    @mcp.tool()
    @require_cdp_client
    async def get_connection_status(**kwargs: Any) -> dict[str, Any]:
        """Get the current connection status to the browser.

        Retrieves comprehensive information about the current connection state,
        including browser details if connected. This is useful for diagnostics
        and determining whether other operations can be performed.

        The function provides different information depending on connection state:
        - If connected: Browser version, target info, and connection details
        - If not connected: Basic status information
        - If not initialised: Client setup status

        Returns:
            Status dictionary containing:
            - success: Boolean indicating status check success
            - message: Human-readable status description
            - data: Status details including:
                - connected: Boolean connection status
                - status: Text status (connected/disconnected/not_initialised)
                - targetInfo: Browser information (if connected)
                - host: Chrome host address (if connected)
                - port: Chrome port number (if connected)

        Note:
            This function is safe to call at any time and will not modify the
            connection state, only report it.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            if cdp_client.connected:
                target_info = await cdp_client.get_target_info()
                return create_success_response(
                    message="Connected to browser",
                    data={
                        "connected": True,
                        "status": "connected",
                        "targetInfo": target_info,
                        "host": cdp_client.host,
                        "port": cdp_client.port,
                    },
                )
            else:
                return create_success_response(
                    message="Not connected to browser",
                    data={"connected": False, "status": "disconnected"},
                )

        except Exception as e:
            return create_error_response(f"Status check error: {e}")
