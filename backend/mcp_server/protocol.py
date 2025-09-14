"""
MCP Protocol Implementation
Handles JSON-RPC 2.0 protocol for MCP communication
"""

import json
from typing import Dict, Any, Optional, Union
import uuid

class MCPProtocol:
    """
    Implements the MCP protocol based on JSON-RPC 2.0
    This ensures standardized communication with AI clients
    """

    VERSION = "2.0"

    def __init__(self):
        self.supported_methods = [
            # Resource methods
            "resources.list",
            "resources.get",
            "resources.search",
            "resources.subscribe",
            "resources.unsubscribe",

            # Tool methods
            "tools.list",
            "tools.execute",
            "tools.validate",

            # System methods
            "system.info",
            "system.ping",
            "system.permissions",
            "system.grant",
            "system.revoke",

            # Financial specific
            "finance.accounts",
            "finance.transactions",
            "finance.analyze",
            "finance.predict"
        ]

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate if request follows JSON-RPC 2.0 format"""

        # Check required fields
        if not isinstance(request, dict):
            return False

        if "jsonrpc" not in request or request["jsonrpc"] != self.VERSION:
            return False

        if "method" not in request:
            return False

        # Method must be a string
        if not isinstance(request["method"], str):
            return False

        # If params exist, they must be dict or list
        if "params" in request:
            if not isinstance(request["params"], (dict, list)):
                return False

        return True

    def create_request(self, method: str, params: Optional[Union[Dict, list]] = None,
                      request_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """Create a properly formatted JSON-RPC request"""

        request = {
            "jsonrpc": self.VERSION,
            "method": method
        }

        if params is not None:
            request["params"] = params

        if request_id is not None:
            request["id"] = request_id
        else:
            request["id"] = str(uuid.uuid4())

        return request

    def create_response(self, result: Any, request_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """Create a successful response"""

        response = {
            "jsonrpc": self.VERSION,
            "result": result
        }

        if request_id is not None:
            response["id"] = request_id

        return response

    def error_response(self, message: str, code: int,
                      data: Optional[Any] = None,
                      request_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """Create an error response"""

        error = {
            "code": code,
            "message": message
        }

        if data is not None:
            error["data"] = data

        response = {
            "jsonrpc": self.VERSION,
            "error": error
        }

        if request_id is not None:
            response["id"] = request_id

        return response

    def create_notification(self, method: str, params: Optional[Union[Dict, list]] = None) -> Dict[str, Any]:
        """Create a notification (no response expected)"""

        notification = {
            "jsonrpc": self.VERSION,
            "method": method
        }

        if params is not None:
            notification["params"] = params

        # Notifications don't have an ID
        return notification

    def parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse incoming message"""

        try:
            data = json.loads(message)
            if self.validate_request(data):
                return data
            return None
        except json.JSONDecodeError:
            return None

    def serialize_message(self, message: Dict[str, Any]) -> str:
        """Serialize message for transmission"""
        return json.dumps(message, separators=(',', ':'))

    def is_notification(self, message: Dict[str, Any]) -> bool:
        """Check if message is a notification (no ID)"""
        return "id" not in message

    def is_batch_request(self, message: Any) -> bool:
        """Check if this is a batch request"""
        return isinstance(message, list)

    def process_batch(self, batch: list) -> list:
        """Process batch requests"""

        responses = []
        for request in batch:
            if self.validate_request(request):
                # Each request would be processed individually
                # For now, return a placeholder
                if not self.is_notification(request):
                    responses.append(self.create_response(
                        {"status": "processed"},
                        request.get("id")
                    ))
        return responses

    def get_error_codes(self) -> Dict[int, str]:
        """Standard JSON-RPC error codes + MCP specific codes"""

        return {
            # Standard JSON-RPC errors
            -32700: "Parse error",
            -32600: "Invalid Request",
            -32601: "Method not found",
            -32602: "Invalid params",
            -32603: "Internal error",

            # MCP specific errors (custom range: -32000 to -32099)
            -32001: "Authentication required",
            -32002: "Permission denied",
            -32003: "Resource not found",
            -32004: "Tool execution failed",
            -32005: "Rate limit exceeded",
            -32006: "Subscription failed",
            -32007: "Invalid financial data",
            -32008: "Encryption required",
            -32009: "Session expired",
            -32010: "Fraud detected"
        }