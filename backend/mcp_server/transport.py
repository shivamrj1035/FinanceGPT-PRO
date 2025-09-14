"""
MCP Transport Layer
Handles WebSocket and HTTP communication for real-time financial data
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime
import uuid
from aiohttp import web
import aiohttp_cors

logger = logging.getLogger(__name__)

class MCPTransport:
    """
    Transport layer for MCP Server
    Supports both WebSocket (real-time) and HTTP (REST) communication
    """

    def __init__(self, server):
        self.server = server
        self.websocket_connections: Dict[str, Any] = {}
        self.http_app = None
        self.websocket_server = None
        self.runner = None

    async def start(self):
        """Start both WebSocket and HTTP servers"""
        # Start WebSocket server
        asyncio.create_task(self.start_websocket_server())

        # Start HTTP server
        await self.start_http_server()

        logger.info("✅ MCP Transport layer started successfully")

    async def start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        try:
            port = self.server.config.get("websocket_port", 9001)

            async def handle_websocket(websocket):
                connection_id = str(uuid.uuid4())
                self.websocket_connections[connection_id] = {
                    "websocket": websocket,
                    "connected_at": datetime.now(),
                    "path": "/"
                }

                # Register connection with server
                self.server.register_connection(connection_id, {
                    "type": "websocket",
                    "remote_address": websocket.remote_address
                })

                logger.info(f"🔌 WebSocket connection established: {connection_id[:8]}")

                try:
                    # Send welcome message
                    await websocket.send(json.dumps({
                        "type": "welcome",
                        "connection_id": connection_id,
                        "server_version": self.server.config["version"],
                        "timestamp": datetime.now().isoformat()
                    }))

                    # Handle messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)

                            # Process request through MCP server
                            response = await self.server.handle_request(data, connection_id)

                            # Send response
                            await websocket.send(json.dumps(response))

                            # Log for demo
                            if data.get("method", "").startswith("tools.execute"):
                                tool_name = data.get("params", {}).get("tool", "unknown")
                                logger.info(f"🔧 Executed tool: {tool_name}")

                        except json.JSONDecodeError:
                            error_response = {
                                "jsonrpc": "2.0",
                                "error": {
                                    "code": -32700,
                                    "message": "Parse error"
                                }
                            }
                            await websocket.send(json.dumps(error_response))

                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"🔌 WebSocket connection closed: {connection_id[:8]}")

                finally:
                    # Clean up connection
                    del self.websocket_connections[connection_id]
                    self.server.unregister_connection(connection_id)

            self.websocket_server = await websockets.serve(
                handle_websocket,
                "localhost",
                port
            )

            logger.info(f"🌐 WebSocket server listening on ws://localhost:{port}")

        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")

    async def start_http_server(self):
        """Start HTTP server for REST API"""
        self.http_app = web.Application()

        # Setup CORS
        cors = aiohttp_cors.setup(self.http_app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        # Define routes
        self.http_app.router.add_post('/mcp/request', self.handle_http_request)
        self.http_app.router.add_get('/mcp/info', self.handle_info_request)
        self.http_app.router.add_get('/mcp/health', self.handle_health_check)
        self.http_app.router.add_post('/mcp/demo/fraud', self.trigger_fraud_demo)

        # Apply CORS to all routes
        for route in list(self.http_app.router.routes()):
            cors.add(route)

        # Start server
        port = self.server.config.get("port", 9000)
        self.runner = web.AppRunner(self.http_app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', port)
        await site.start()

        logger.info(f"📡 HTTP server listening on http://localhost:{port}")

    async def handle_http_request(self, request):
        """Handle HTTP POST requests"""
        try:
            data = await request.json()
            connection_id = f"http-{uuid.uuid4()}"

            # Register temporary connection
            self.server.register_connection(connection_id, {
                "type": "http",
                "remote_address": request.remote
            })

            # Process request
            response = await self.server.handle_request(data, connection_id)

            # Unregister connection
            self.server.unregister_connection(connection_id)

            return web.json_response(response)

        except Exception as e:
            logger.error(f"❌ HTTP request error: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }, status=500)

    async def handle_info_request(self, request):
        """Handle server info request"""
        info = {
            "server_name": self.server.config["server_name"],
            "version": self.server.config["version"],
            "uptime": (datetime.now() - self.server.start_time).total_seconds(),
            "active_connections": len(self.server.active_connections),
            "websocket_connections": len(self.websocket_connections),
            "request_count": self.server.request_count,
            "capabilities": {
                "websocket": True,
                "http": True,
                "real_time": True,
                "encryption": self.server.config.get("enable_encryption", True),
                "compression": self.server.config.get("enable_compression", True)
            }
        }
        return web.json_response(info)

    async def handle_health_check(self, request):
        """Health check endpoint"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mcp_server": "operational",
                "websocket": "operational" if self.websocket_server else "down",
                "http": "operational",
                "data_store": "operational"
            }
        }
        return web.json_response(health)

    async def trigger_fraud_demo(self, request):
        """Trigger fraud alert for demo - THIS IS OUR WOW MOMENT!"""
        try:
            # Trigger the fraud simulation
            fraud_data = await self.server.simulate_fraud_alert()

            # Broadcast to all WebSocket connections
            alert_message = {
                "type": "fraud_alert",
                "data": fraud_data,
                "timestamp": datetime.now().isoformat(),
                "severity": "HIGH"
            }

            await self.broadcast_to_websockets(alert_message)

            return web.json_response({
                "success": True,
                "message": "Fraud alert triggered successfully",
                "alert_data": fraud_data
            })

        except Exception as e:
            logger.error(f"❌ Failed to trigger fraud demo: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if connection_id in self.websocket_connections:
            websocket = self.websocket_connections[connection_id]["websocket"]
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"❌ Failed to send to {connection_id[:8]}: {e}")
                # Remove dead connection
                del self.websocket_connections[connection_id]
                self.server.unregister_connection(connection_id)

    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket connections"""
        message_str = json.dumps(message)
        dead_connections = []

        for conn_id, conn_data in self.websocket_connections.items():
            try:
                await conn_data["websocket"].send(message_str)
            except Exception as e:
                logger.error(f"❌ Failed to broadcast to {conn_id[:8]}: {e}")
                dead_connections.append(conn_id)

        # Clean up dead connections
        for conn_id in dead_connections:
            del self.websocket_connections[conn_id]
            self.server.unregister_connection(conn_id)

        logger.info(f"📢 Broadcasted to {len(self.websocket_connections) - len(dead_connections)} connections")

    async def close_connection(self, connection_id: str):
        """Close a specific connection"""
        if connection_id in self.websocket_connections:
            try:
                await self.websocket_connections[connection_id]["websocket"].close()
            except:
                pass
            finally:
                del self.websocket_connections[connection_id]

    async def stop(self):
        """Stop all transport servers"""
        # Close all WebSocket connections
        for conn_id in list(self.websocket_connections.keys()):
            await self.close_connection(conn_id)

        # Stop WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()

        # Stop HTTP server
        if self.runner:
            await self.runner.cleanup()

        logger.info("🛑 Transport layer stopped")

# Additional WebSocket message types for demo
class MessageTypes:
    """WebSocket message types for real-time updates"""

    # Client to Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    REQUEST = "request"
    PING = "ping"

    # Server to Client
    UPDATE = "update"
    ALERT = "alert"
    NOTIFICATION = "notification"
    PONG = "pong"
    ERROR = "error"

    # Special demo messages
    FRAUD_ALERT = "fraud_alert"
    GOAL_UPDATE = "goal_update"
    TRANSACTION_UPDATE = "transaction_update"
    INSIGHT_UPDATE = "insight_update"