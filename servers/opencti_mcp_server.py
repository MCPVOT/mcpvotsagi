#!/usr/bin/env python3
"""
OpenCTI MCP Server
==================
MCP server for OpenCTI threat intelligence integration
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from opencti_integration import OpenCTIMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(websocket, path):
    """Handle WebSocket connections"""
    server = OpenCTIMCPServer()
    logger.info(f"New OpenCTI MCP client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
    except Exception as e:
        logger.error(f"Error with client {websocket.remote_address}: {e}")
    finally:
        logger.info(f"OpenCTI MCP client disconnected: {websocket.remote_address}")

async def main():
    """Start the OpenCTI MCP server"""
    import websockets
    
    port = 3007  # OpenCTI MCP port
    server = await websockets.serve(handle_client, "localhost", port)
    logger.info(f"OpenCTI MCP Server started on ws://localhost:{port}")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("OpenCTI MCP server shutting down...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())