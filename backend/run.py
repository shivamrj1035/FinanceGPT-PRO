#!/usr/bin/env python
"""
FinanceGPT Pro - Backend Server Runner
Starts both FastAPI and MCP servers
"""

import asyncio
import uvicorn
import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('financebot.log')
    ]
)
logger = logging.getLogger(__name__)

async def run_servers():
    """
    Run both FastAPI and MCP servers concurrently
    """
    logger.info("🚀 Starting FinanceGPT Pro Backend Services...")

    # Import here to ensure path is set
    from api.main import app
    from mcp_server.server import MCPServer
    from mcp_server.mock_data import load_mock_data

    # Load configuration
    config = {
        "api_host": os.getenv("API_HOST", "0.0.0.0"),
        "api_port": int(os.getenv("API_PORT", 8000)),
        "mcp_http_port": int(os.getenv("MCP_HTTP_PORT", 9000)),
        "mcp_websocket_port": int(os.getenv("MCP_WEBSOCKET_PORT", 9001)),
    }

    # Initialize MCP Server
    mcp_config = {
        "server_name": "FinanceGPT Pro MCP Server",
        "version": "1.0.0",
        "port": config["mcp_http_port"],
        "websocket_port": config["mcp_websocket_port"],
        "enable_security": True,
        "enable_encryption": True,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "jwt_secret": os.getenv("JWT_SECRET", "hackathon-secret-2025"),
    }

    mock_data = load_mock_data()
    mcp_server = MCPServer(mcp_config)
    mcp_server.mock_data = mock_data

    # Start MCP Server
    logger.info(f"📡 Starting MCP Server on ports {config['mcp_http_port']} (HTTP) and {config['mcp_websocket_port']} (WebSocket)")
    await mcp_server.initialize()

    # Configure uvicorn
    uvicorn_config = uvicorn.Config(
        app=app,
        host=config["api_host"],
        port=config["api_port"],
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level="info",
        access_log=True
    )

    # Create uvicorn server
    server = uvicorn.Server(uvicorn_config)

    logger.info(f"🌐 Starting FastAPI on http://{config['api_host']}:{config['api_port']}")
    logger.info(f"📚 API Documentation available at http://localhost:{config['api_port']}/docs")
    logger.info("✅ All services started successfully!")
    logger.info("\n" + "="*50)
    logger.info("🎯 FinanceGPT Pro is ready for the hackathon!")
    logger.info("="*50 + "\n")

    # Run the server
    await server.serve()

def main():
    """
    Main entry point
    """
    try:
        # Run the async function
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()