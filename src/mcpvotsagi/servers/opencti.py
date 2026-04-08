"""OpenCTI MCP Server — WebSocket MCP server for OpenCTI threat intelligence.

Requires the `opencti_integration` module to be available in PYTHONPATH,
or install via: pip install pycti
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def handle_client(websocket: websockets.WebSocketServerProtocol) -> None:
    """Handle WebSocket connections for OpenCTI MCP."""
    from services.opencti_integration import OpenCTIMCPServer

    server = OpenCTIMCPServer()
    logger.info("New OpenCTI MCP client connected: %s", websocket.remote_address)

    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
    except Exception as e:
        logger.error("Error with client %s: %s", websocket.remote_address, e)
    finally:
        logger.info("OpenCTI MCP client disconnected: %s", websocket.remote_address)


async def main() -> None:
    """Start the OpenCTI MCP server."""
    port = int(os.environ.get("OPENCTI_MCP_PORT", "3007"))
    async with websockets.serve(handle_client, "localhost", port):
        logger.info("OpenCTI MCP Server started on ws://localhost:%d", port)
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down")
