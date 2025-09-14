"""
Main MCP Server Implementation
This is the core of our MCP architecture - handles all financial data requests
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from pathlib import Path

from .protocol import MCPProtocol
from .transport import MCPTransport
from .resources import ResourceManager
from .tools import ToolsManager
from .security import SecurityManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """
    Main MCP Server that handles all financial data operations
    This is what makes us different from every other hackathon project!
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the MCP Server with configuration"""
        self.config = config or self._default_config()
        self.server_id = str(uuid.uuid4())
        self.start_time = datetime.now()

        # Initialize core components
        self.protocol = MCPProtocol()
        self.transport = MCPTransport(self)
        self.resource_manager = ResourceManager(self)
        self.tool_manager = ToolsManager(self)
        self.security_manager = SecurityManager(self)

        # Connection tracking
        self.active_connections = {}
        self.request_count = 0

        # Load mock data
        self.data_path = Path("data/mock")
        self._load_mock_data()

        logger.info(f"🚀 MCP Server initialized with ID: {self.server_id}")

    def _default_config(self) -> Dict[str, Any]:
        """Default server configuration"""
        return {
            "server_name": "FinanceGPT-MCP-Server",
            "version": "1.0.0",
            "host": "localhost",
            "port": 9000,
            "websocket_port": 9001,
            "max_connections": 100,
            "timeout": 30,
            "enable_encryption": True,
            "enable_compression": True,
            "rate_limit": {
                "requests_per_minute": 100,
                "burst_size": 20
            }
        }

    def _load_mock_data(self):
        """Load mock financial data from JSON files"""
        self.mock_data = {}
        # Streamlined to 4 core financial data sources for hackathon demo
        data_files = ["users", "accounts", "transactions", "investments"]

        for file_name in data_files:
            file_path = self.data_path / f"{file_name}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.mock_data[file_name] = json.load(f)
                logger.info(f"✅ Loaded {file_name}.json")
            else:
                self.mock_data[file_name] = []
                logger.warning(f"⚠️ {file_name}.json not found")

    async def start(self):
        """Start the MCP server"""
        logger.info(f"🎯 Starting MCP Server on port {self.config['port']}")

        # Start transport layer (WebSocket + HTTP)
        await self.transport.start()

        # Initialize security
        await self.security_manager.initialize()

        # Start heartbeat
        asyncio.create_task(self._heartbeat())

        logger.info("✨ MCP Server is ready for connections!")
        logger.info(f"📡 WebSocket: ws://localhost:{self.config['websocket_port']}")
        logger.info(f"🌐 HTTP: http://localhost:{self.config['port']}")

    async def handle_request(self, request: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """
        Main request handler - routes to appropriate component
        This is where the magic happens!
        """
        self.request_count += 1

        try:
            # Validate request format
            if not self.protocol.validate_request(request):
                return self.protocol.error_response("Invalid request format", -32600)

            # Check authentication
            if not await self.security_manager.authenticate(request, connection_id):
                return self.protocol.error_response("Authentication failed", -32001)

            # Check permissions
            if not await self.security_manager.check_permission(request, connection_id):
                return self.protocol.error_response("Permission denied", -32002)

            # Route request based on method
            method = request.get("method", "")
            params = request.get("params", {})

            # Log request for demo
            logger.info(f"📥 Request: {method} from {connection_id[:8]}")

            # Handle different method types
            if method.startswith("resources."):
                response = await self.resource_manager.handle(method, params)
            elif method.startswith("tools."):
                response = await self.tool_manager.handle(method, params)
            elif method.startswith("system."):
                response = await self._handle_system_method(method, params)
            else:
                response = self.protocol.error_response(f"Unknown method: {method}", -32601)

            # Add request ID to response
            response["id"] = request.get("id", None)

            return response

        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
            return self.protocol.error_response(str(e), -32603)

    async def _handle_system_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system-level methods"""

        if method == "system.info":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "server_id": self.server_id,
                    "version": self.config["version"],
                    "uptime": (datetime.now() - self.start_time).total_seconds(),
                    "request_count": self.request_count,
                    "active_connections": len(self.active_connections),
                    "capabilities": {
                        "resources": self.resource_manager.list_resources(),
                        "tools": self.tool_manager.list_tools(),
                        "features": [
                            "real-time-updates",
                            "encryption",
                            "compression",
                            "permissions",
                            "multi-tenancy"
                        ]
                    }
                }
            }

        elif method == "system.ping":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "pong": True,
                    "timestamp": datetime.now().isoformat()
                }
            }

        elif method == "system.permissions":
            user_id = params.get("user_id", "USR001")
            permissions = self.mock_data.get("permissions", [])
            user_permissions = [p for p in permissions if p["user_id"] == user_id]

            return {
                "jsonrpc": "2.0",
                "result": {
                    "permissions": user_permissions
                }
            }

        return self.protocol.error_response(f"Unknown system method: {method}", -32601)

    async def broadcast_update(self, resource: str, data: Any):
        """
        Broadcast real-time updates to all connected clients
        This is what makes our demo look amazing - real-time data!
        """
        update = {
            "jsonrpc": "2.0",
            "method": "update",
            "params": {
                "resource": resource,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Send to all active connections
        for conn_id in self.active_connections:
            await self.transport.send_to_connection(conn_id, update)

        logger.info(f"📢 Broadcasted update for {resource} to {len(self.active_connections)} clients")

    async def _heartbeat(self):
        """Keep-alive heartbeat for WebSocket connections"""
        while True:
            await asyncio.sleep(30)

            heartbeat = {
                "jsonrpc": "2.0",
                "method": "heartbeat",
                "params": {
                    "timestamp": datetime.now().isoformat(),
                    "server_health": "healthy"
                }
            }

            # Send heartbeat to all connections
            for conn_id in list(self.active_connections.keys()):
                try:
                    await self.transport.send_to_connection(conn_id, heartbeat)
                except:
                    # Remove dead connections
                    self.active_connections.pop(conn_id, None)

    def register_connection(self, connection_id: str, connection_info: Dict[str, Any]):
        """Register a new client connection"""
        self.active_connections[connection_id] = {
            "connected_at": datetime.now().isoformat(),
            "info": connection_info,
            "request_count": 0
        }
        logger.info(f"✅ New connection registered: {connection_id[:8]}")

    def unregister_connection(self, connection_id: str):
        """Remove a client connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"👋 Connection closed: {connection_id[:8]}")

    async def simulate_fraud_alert(self):
        """
        Simulate a fraud alert for demo purposes
        This is our WOW moment in the presentation!
        """
        fraud_transaction = {
            "id": "TXN999999",
            "account_id": "ACC001",
            "amount": -35000,
            "merchant": "SUSPICIOUS-MERCHANT-INTL",
            "category": "Suspicious",
            "date": datetime.now().isoformat(),
            "type": "DEBIT",
            "status": "BLOCKED",
            "fraud_score": 0.92,
            "alert": {
                "type": "FRAUD_ALERT",
                "severity": "HIGH",
                "message": "Suspicious transaction detected and blocked",
                "action_required": True
            }
        }

        # Broadcast to all clients
        await self.broadcast_update("fraud_alert", fraud_transaction)

        logger.info("🚨 FRAUD ALERT TRIGGERED FOR DEMO!")
        return fraud_transaction

    async def shutdown(self):
        """Gracefully shutdown the server"""
        logger.info("🛑 Shutting down MCP Server...")

        # Close all connections
        for conn_id in list(self.active_connections.keys()):
            await self.transport.close_connection(conn_id)

        # Stop transport
        await self.transport.stop()

        logger.info("👋 MCP Server shutdown complete")

# Quick test
if __name__ == "__main__":
    async def test_server():
        server = MCPServer()
        await server.start()

        # Test request
        test_request = {
            "jsonrpc": "2.0",
            "method": "system.info",
            "id": 1
        }

        response = await server.handle_request(test_request, "test-connection")
        print(f"Response: {json.dumps(response, indent=2)}")

        # Keep server running
        await asyncio.sleep(3600)

    asyncio.run(test_server())