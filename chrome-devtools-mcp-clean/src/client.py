#!/usr/bin/env python3
"""Chrome DevTools Protocol Client

This module contains the ChromeDevToolsClient class that manages WebSocket connections
to Chrome's remote debugging interface and handles CDP commands and events.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from collections.abc import Callable
from typing import Any

import aiohttp
import websockets

logger = logging.getLogger(__name__)

# WebSocket 连接配置
WEBSOCKET_PING_INTERVAL = 20  # 每20秒发送一次ping
WEBSOCKET_PING_TIMEOUT = 10   # ping超时时间10秒
WEBSOCKET_CLOSE_TIMEOUT = 10  # 关闭超时时间10秒
WEBSOCKET_MAX_SIZE = 10 * 1024 * 1024  # 最大消息大小10MB
WEBSOCKET_OPEN_TIMEOUT = 10.0  # WebSocket连接建立超时10秒

# HTTP请求超时配置
HTTP_TOTAL_TIMEOUT = 30.0     # HTTP请求总超时30秒
HTTP_CONNECT_TIMEOUT = 10.0   # HTTP连接超时10秒
HTTP_READ_TIMEOUT = 10.0      # HTTP读取超时10秒

# 重连配置
MAX_RECONNECT_ATTEMPTS = 3  # 最大重连次数
RECONNECT_BASE_DELAY = 2  # 重连基础延迟（秒）

# 命令超时配置
COMMAND_TIMEOUT = 30.0  # 命令超时时间（秒）

# 目标等待配置
TARGET_WAIT_MAX_TIMEOUT = 10.0  # 等待目标创建最大超时10秒
TARGET_WAIT_INTERVAL = 0.5      # 目标等待轮询间隔0.5秒


class ChromeDevToolsClient:
    """
    Chrome DevTools Protocol client with WebSocket communication capabilities.

    This class manages the connection to Chrome's remote debugging interface,
    handles event processing, and executes CDP commands. It maintains state
    for network requests and console logs, and provides a robust interface
    for web application debugging.

    The client automatically discovers available Chrome targets and establishes
    WebSocket connections for real-time communication with the browser.

    Attributes:
        port: Chrome remote debugging port (default: 9222)
        host: Hostname for Chrome connection (default: localhost)
        ws: WebSocket connection to Chrome DevTools
        connected: Connection status flag
        message_id: Incremental ID for CDP messages
        pending_messages: Awaiting responses for sent commands
        event_handlers: Registered handlers for CDP events
        network_requests: Captured network request data
        console_logs: Captured console log entries
    """

    def __init__(self, port: int = 9222, host: str = "localhost") -> None:
        """
        Initialise the Chrome DevTools Protocol client.

        Args:
            port: Chrome remote debugging port (overridden by CHROME_DEBUG_PORT env var)
            host: Hostname for Chrome connection
        """
        # Check for Bit Browser mode
        self.bit_browser_mode = os.getenv("BIT_BROWSER_MODE", "").lower() == "true"
        self.bit_browser_id = os.getenv("BIT_BROWSER_ID", "")
        self.bit_browser_api_host = os.getenv("BIT_BROWSER_API_HOST", "localhost")
        self.bit_browser_api_port = int(os.getenv("BIT_BROWSER_API_PORT", "54345"))

        # Use environment variable if available for flexible configuration
        env_port = os.getenv("CHROME_DEBUG_PORT")
        if env_port and env_port.isdigit():
            port = int(env_port)

        self.port = port
        self.host = host
        self.ws: websockets.WebSocketServerProtocol | None = None  # type: ignore
        self.connected = False
        self.message_id = 0
        self.pending_messages: dict[int, asyncio.Future] = {}
        self.event_handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}

        # Storage for captured browser data
        self.network_requests: list[dict[str, Any]] = []
        self.console_logs: list[dict[str, Any]] = []

        # Flag to indicate intentional disconnect (prevents auto-reconnect)
        self._intentional_disconnect = False

        # Validate Bit Browser configuration if enabled
        if self.bit_browser_mode and not self.bit_browser_id:
            raise ValueError("BIT_BROWSER_ID environment variable is required when BIT_BROWSER_MODE is enabled")

    async def connect(self) -> bool:
        """
        Establish connection to Chrome DevTools via WebSocket.

        For Bit Browser mode, first calls the Bit Browser Local API to open the browser
        and get connection details, then creates a new page target. For regular Chrome mode,
        discovers available targets and connects to the first available target using WebSocket communication.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If no browser targets are available
        """
        # Reset intentional disconnect flag when connecting
        self._intentional_disconnect = False

        try:
            if self.bit_browser_mode:
                # Use Bit Browser API to get connection details
                connection_info = await self._call_bitbrowser_api()
                if not connection_info:
                    raise ConnectionError("Failed to get Bit Browser connection info")

                # Extract HTTP port from connection info
                http_address = connection_info.get("http", "")
                logger.info(f"Bit Browser HTTP debug address: {http_address}")

                if ":" in http_address:
                    http_port = int(http_address.split(":")[-1])
                else:
                    http_port = 9222  # fallback

                # Try to get existing page targets from the HTTP endpoint
                # This is the correct way to connect to page-level targets
                try:
                    async with aiohttp.ClientSession() as session:
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
                                    self.ws = await websockets.connect(
                                        ws_url,
                                        ping_interval=WEBSOCKET_PING_INTERVAL,
                                        ping_timeout=WEBSOCKET_PING_TIMEOUT,
                                        close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                                        max_size=WEBSOCKET_MAX_SIZE,
                                        open_timeout=WEBSOCKET_OPEN_TIMEOUT
                                    )
                                    self.connected = True
                                    asyncio.create_task(self._handle_incoming_messages())
                                    logger.info(f"✅ Connected to existing page target: {target.get('title', 'Unknown')}")
                                    return True
                except Exception as e:
                    logger.warning(f"Could not get page targets from HTTP endpoint: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())

                # If no page targets found, connect to browser target and create a new page
                logger.info("No existing page targets found, creating a new one...")
                ws_url = connection_info["ws"]
                logger.info(f"Connecting to browser target WebSocket: {ws_url}")
                self.ws = await websockets.connect(
                    ws_url,
                    ping_interval=WEBSOCKET_PING_INTERVAL,
                    ping_timeout=WEBSOCKET_PING_TIMEOUT,
                    close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                    max_size=WEBSOCKET_MAX_SIZE,
                    open_timeout=WEBSOCKET_OPEN_TIMEOUT
                )
                self.connected = True
                asyncio.create_task(self._handle_incoming_messages())

                logger.info(f"Connected to Bit Browser instance: {self.bit_browser_id}")

                # Create a new page target
                try:
                    logger.info("Creating new page target with Target.createTarget...")
                    result = await self.send_command("Target.createTarget", {"url": "about:blank"})
                    logger.debug(f"Target.createTarget result: {result}")

                    if result and "targetId" in result:
                        target_id = result["targetId"]
                        logger.info(f"Created new page target: {target_id}")

                        # Wait for target to be ready using polling instead of fixed delay
                        logger.info(f"Waiting for target {target_id} to be ready...")
                        ready_target = await self.wait_for_target_ready(http_address, target_id)

                        if ready_target:
                            page_ws_url = ready_target.get("webSocketDebuggerUrl")
                            if page_ws_url:
                                logger.info(f"Found new page target, switching connection to: {page_ws_url}")
                                # Close browser connection and connect to page
                                try:
                                    await asyncio.wait_for(self.ws.close(), timeout=WEBSOCKET_CLOSE_TIMEOUT)
                                except asyncio.TimeoutError:
                                    logger.warning("Timeout closing browser WebSocket, forcing disconnect")
                                except Exception as e:
                                    logger.warning(f"Error closing browser WebSocket: {e}")

                                self.ws = await websockets.connect(
                                    page_ws_url,
                                    ping_interval=WEBSOCKET_PING_INTERVAL,
                                    ping_timeout=WEBSOCKET_PING_TIMEOUT,
                                    close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                                    max_size=WEBSOCKET_MAX_SIZE,
                                    open_timeout=WEBSOCKET_OPEN_TIMEOUT
                                )
                                asyncio.create_task(self._handle_incoming_messages())
                                logger.info(f"✅ Connected to new page target: {target_id}")
                                return True
                        else:
                            logger.warning(f"Could not find page target with ID {target_id} after waiting")
                except Exception as e:
                    logger.error(f"Failed to create page target: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())

                # If we're still connected to browser target, log a warning
                logger.warning("⚠️ Connected to browser-level target. Some CDP domains (Page, Runtime, DOM) may not be available.")
                logger.warning("⚠️ Only basic functionality (Network, Console) will work.")
                return True
            else:
                # Regular Chrome connection
                targets = await self._get_available_targets()
                if not targets:
                    raise ConnectionError("No browser targets available")

                target = targets[0]
                ws_url = target["webSocketDebuggerUrl"]

                self.ws = await websockets.connect(
                    ws_url,
                    ping_interval=WEBSOCKET_PING_INTERVAL,
                    ping_timeout=WEBSOCKET_PING_TIMEOUT,
                    close_timeout=WEBSOCKET_CLOSE_TIMEOUT,
                    max_size=WEBSOCKET_MAX_SIZE,
                    open_timeout=WEBSOCKET_OPEN_TIMEOUT
                )
                self.connected = True

                asyncio.create_task(self._handle_incoming_messages())

                logger.info(f"Connected to Chrome target: {target.get('title', 'Unknown')}")
                return True

        except asyncio.TimeoutError:
            logger.error(f"WebSocket connection timed out after {WEBSOCKET_OPEN_TIMEOUT}s")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to browser: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        """Gracefully disconnect from Chrome DevTools."""
        # Set flag to prevent auto-reconnect
        self._intentional_disconnect = True

        if self.ws:
            try:
                # Use asyncio.wait_for to add timeout protection
                await asyncio.wait_for(self.ws.close(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("WebSocket close timed out, forcing disconnect")
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")

        self.connected = False
        self.ws = None
        logger.info("Disconnected from Chrome")

    async def _reconnect(self) -> bool:
        """
        Attempt to reconnect to the browser.

        Returns:
            bool: True if reconnection successful, False otherwise
        """
        try:
            # Close existing connection
            if self.ws:
                try:
                    await self.ws.close()
                except Exception:
                    pass

            self.connected = False
            self.ws = None

            # Attempt to reconnect
            logger.info("Attempting to reconnect...")
            success = await self.connect()

            if success:
                logger.info("✅ Reconnection successful")
            else:
                logger.error("❌ Reconnection failed")

            return success
        except Exception as e:
            logger.error(f"Reconnection error: {e}")
            return False

    async def _call_bitbrowser_api(self) -> dict[str, Any] | None:
        """Call Bit Browser Local API to open browser and get connection details."""
        try:
            url = f"http://{self.bit_browser_api_host}:{self.bit_browser_api_port}/browser/open"
            payload = {"id": self.bit_browser_id}

            # 设置HTTP超时
            timeout = aiohttp.ClientTimeout(
                total=HTTP_TOTAL_TIMEOUT,
                connect=HTTP_CONNECT_TIMEOUT,
                sock_read=HTTP_READ_TIMEOUT
            )

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            data = result.get("data", {})
                            logger.info(f"Bit Browser API response: {data}")
                            return data
                        else:
                            logger.error(f"Bit Browser API returned error: {result}")
                            return None
                    else:
                        logger.error(f"Bit Browser API HTTP error: {response.status}")
                        return None
        except asyncio.TimeoutError:
            logger.error(f"Bit Browser API call timed out after {HTTP_TOTAL_TIMEOUT}s")
            return None
        except Exception as e:
            logger.error(f"Failed to call Bit Browser API: {e}")
            return None

    async def _get_available_targets(self) -> list[dict[str, Any]]:
        """Retrieve list of available Chrome targets."""
        try:
            # 设置HTTP超时
            timeout = aiohttp.ClientTimeout(
                total=HTTP_TOTAL_TIMEOUT,
                connect=HTTP_CONNECT_TIMEOUT,
                sock_read=HTTP_READ_TIMEOUT
            )

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://{self.host}:{self.port}/json") as response:
                    if response.status == 200:
                        targets = await response.json()
                        return [t for t in targets if t.get("type") == "page"]
                    return []
        except asyncio.TimeoutError:
            logger.error(f"Failed to get targets: Request timed out after {HTTP_TOTAL_TIMEOUT}s")
            return []
        except Exception as e:
            logger.error(f"Failed to get targets: {e}")
            return []

    async def wait_for_target_ready(self, http_address: str, target_id: str) -> dict[str, Any] | None:
        """Wait for a specific target to be ready by polling the /json endpoint.

        Args:
            http_address: HTTP debug address (e.g., "127.0.0.1:50106")
            target_id: Target ID to wait for

        Returns:
            Target dict if found, None if timeout
        """
        start_time = asyncio.get_event_loop().time()
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
                            for t in targets:
                                t_id = t.get("id") or t.get("targetId")
                                if t_id == target_id and t.get("type") == "page":
                                    logger.info(f"Target {target_id} is ready")
                                    return t
            except Exception as e:
                logger.debug(f"Error polling for target {target_id}: {e}")

            await asyncio.sleep(TARGET_WAIT_INTERVAL)

        logger.warning(f"Timeout waiting for target {target_id} after {TARGET_WAIT_MAX_TIMEOUT}s")
        return None

    async def get_target_type(self) -> str:
        """Get the type of the currently connected target.

        Returns:
            str: Target type ('page', 'browser', 'service_worker', etc.) or 'unknown'
        """
        try:
            result = await self.send_command("Target.getTargetInfo")
            if result and "targetInfo" in result:
                target_type = result["targetInfo"].get("type", "unknown")
                logger.debug(f"Current target type: {target_type}")
                return target_type
            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to get target type: {e}")
            return "unknown"

    async def send_command(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a command to Chrome DevTools and wait for response."""
        if not self.connected or not self.ws:
            raise ConnectionError("Not connected to Chrome")

        self.message_id += 1
        message = {"id": self.message_id, "method": method, "params": params or {}}

        future: asyncio.Future[dict[str, Any]] = asyncio.Future()
        self.pending_messages[self.message_id] = future

        try:
            await self.ws.send(json.dumps(message))
            result = await asyncio.wait_for(future, timeout=COMMAND_TIMEOUT)
            return result  # type: ignore
        except asyncio.TimeoutError:
            if self.message_id in self.pending_messages:
                del self.pending_messages[self.message_id]
            raise TimeoutError(f"Command {method} timed out after {COMMAND_TIMEOUT}s") from None
        except Exception as e:
            if self.message_id in self.pending_messages:
                del self.pending_messages[self.message_id]
            raise e

    async def _handle_incoming_messages(self) -> None:
        """Handle incoming WebSocket messages from Chrome with automatic reconnection."""
        reconnect_attempts = 0

        while reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
            try:
                if self.ws is not None:
                    async for message in self.ws:
                        try:
                            data = json.loads(message)

                            if "id" in data:
                                message_id = data["id"]
                                if message_id in self.pending_messages:
                                    future = self.pending_messages.pop(message_id)
                                    if "error" in data:
                                        future.set_exception(Exception(data["error"]["message"]))
                                    else:
                                        future.set_result(data.get("result", {}))

                            elif "method" in data:
                                await self._process_event(data)

                        except json.JSONDecodeError:
                            logger.warning("Received invalid JSON from Chrome")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: {e}")
                self.connected = False

                # Check if this was an intentional disconnect - don't reconnect
                if self._intentional_disconnect:
                    logger.info("Intentional disconnect detected, not attempting reconnection")
                    break

                # Attempt to reconnect only for unexpected disconnections
                reconnect_attempts += 1
                if reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
                    # Exponential backoff
                    wait_time = RECONNECT_BASE_DELAY ** reconnect_attempts
                    logger.info(
                        f"Reconnecting in {wait_time}s "
                        f"(attempt {reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})..."
                    )
                    await asyncio.sleep(wait_time)

                    if await self._reconnect():
                        logger.info("✅ Reconnection successful, resuming message handling")
                        reconnect_attempts = 0  # Reset counter on success
                        continue
                    else:
                        logger.error("❌ Reconnection failed")
                else:
                    logger.error(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached")
                    break

            except Exception as e:
                logger.error(f"Fatal error in message handler: {e}")
                self.connected = False
                break

        logger.info("Message handler stopped")

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process CDP event notifications and store relevant data."""
        method = event["method"]
        params = event.get("params", {})

        if method == "Network.requestWillBeSent":
            await self._process_network_request(params)
        elif method == "Network.responseReceived":
            await self._process_network_response(params)
        elif method == "Network.loadingFinished":
            await self._process_network_completion(params)
        elif method == "Network.loadingFailed":
            await self._process_network_failure(params)
        elif method == "Runtime.consoleAPICalled":
            await self._process_console_message(params)
        elif method == "Runtime.exceptionThrown":
            await self._process_console_exception(params)

        if method in self.event_handlers:
            for handler in self.event_handlers[method]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(params)
                    else:
                        handler(params)
                except Exception as e:
                    logger.error(f"Error in event handler for {method}: {e}")

    async def _process_network_request(self, params: dict[str, Any]) -> None:
        """Process network request event."""
        from .tools.utils import safe_timestamp_conversion

        self.network_requests.append(
            {
                "requestId": params["requestId"],
                "url": params["request"]["url"],
                "method": params["request"]["method"],
                "headers": params["request"].get("headers", {}),
                "timestamp": safe_timestamp_conversion(params["timestamp"]),
                "type": "request",
                "status": "pending",
            }
        )

    async def _process_network_response(self, params: dict[str, Any]) -> None:
        """Process network response event."""
        from .tools.utils import safe_timestamp_conversion

        request_id = params["requestId"]
        for req in self.network_requests:
            if req.get("requestId") == request_id and req["type"] == "request":
                req.update(
                    {
                        "response": {
                            "status": params["response"]["status"],
                            "statusText": params["response"]["statusText"],
                            "headers": params["response"]["headers"],
                            "mimeType": params["response"]["mimeType"],
                            "timestamp": safe_timestamp_conversion(params["timestamp"]),
                            "remoteIPAddress": params["response"].get("remoteIPAddress"),
                            "protocol": params["response"].get("protocol"),
                        },
                        "status": "responded",
                    }
                )
                break

    async def _process_network_completion(self, params: dict[str, Any]) -> None:
        """Process network loading completion event."""
        request_id = params["requestId"]
        for req in self.network_requests:
            if req.get("requestId") == request_id:
                req.update(
                    {"status": "completed", "encodedDataLength": params.get("encodedDataLength")}
                )
                break

    async def _process_network_failure(self, params: dict[str, Any]) -> None:
        """Process network loading failure event."""
        request_id = params["requestId"]
        for req in self.network_requests:
            if req.get("requestId") == request_id:
                req.update(
                    {
                        "status": "failed",
                        "errorText": params.get("errorText"),
                        "cancelled": params.get("canceled", False),
                    }
                )
                break

    async def _process_console_message(self, params: dict[str, Any]) -> None:
        """Process console API call event."""
        from .tools.utils import safe_timestamp_conversion

        self.console_logs.append(
            {
                "type": params["type"],
                "args": [arg.get("value", str(arg)) for arg in params["args"]],
                "timestamp": safe_timestamp_conversion(params["timestamp"]),
                "executionContextId": params.get("executionContextId"),
                "stackTrace": params.get("stackTrace"),
            }
        )

    async def _process_console_exception(self, params: dict[str, Any]) -> None:
        """Process console exception event."""
        from .tools.utils import safe_timestamp_conversion

        exception = params["exceptionDetails"]
        self.console_logs.append(
            {
                "type": "error",
                "args": [exception.get("text", "Unknown error")],
                "timestamp": safe_timestamp_conversion(params["timestamp"]),
                "executionContextId": exception.get("executionContextId"),
                "stackTrace": exception.get("stackTrace"),
                "exception": True,
            }
        )

    async def enable_domains(self) -> None:
        """Enable necessary CDP domains for functionality.

        Automatically detects the target type and enables appropriate domains:
        - Browser target: Only Target and Browser domains
        - Page target: All domains including Page, Runtime, DOM, CSS, etc.
        """
        # Check target type first
        target_type = await self.get_target_type()
        logger.info(f"Enabling domains for target type: {target_type}")

        if target_type == "browser":
            # Browser-level target only supports limited domains
            logger.warning("⚠️ Connected to browser-level target. Only basic domains will be enabled.")
            logger.warning("⚠️ Page, Runtime, DOM, CSS domains are NOT available on browser targets.")
            logger.warning("⚠️ To use full CDP functionality, connect to a page-level target.")
            domains = ["Target", "Browser"]
        else:
            # Page-level target supports all domains
            domains = [
                "Network",
                "Runtime",
                "Page",
                "Performance",
                "DOM",
                "CSS",
                "Security",
                "DOMStorage",
            ]

        enabled_count = 0
        failed_count = 0

        for domain in domains:
            try:
                await self.send_command(f"{domain}.enable")
                logger.info(f"✅ {domain} domain enabled")
                enabled_count += 1
            except Exception as e:
                logger.warning(f"❌ Failed to enable {domain} domain: {e}")
                failed_count += 1

        logger.info(f"Domain enablement complete: {enabled_count} enabled, {failed_count} failed")

    async def get_target_info(self) -> dict[str, Any]:
        """Get information about the current target."""
        try:
            return await self.send_command("Target.getTargetInfo")
        except Exception:
            return {"title": "Unknown", "url": "Unknown"}

    def add_event_handler(
        self, event_method: str, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        """Register an event handler for a specific CDP event."""
        if event_method not in self.event_handlers:
            self.event_handlers[event_method] = []
        self.event_handlers[event_method].append(handler)
