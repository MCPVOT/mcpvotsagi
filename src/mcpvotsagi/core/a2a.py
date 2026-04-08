"""
Enhanced A2A (Agent-to-Agent) Communication System
Implements advanced A2A protocol with message queues, agent discovery, and fault tolerance
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import redis.asyncio as redis
import websockets

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """A2A Message types"""

    PING = "ping"
    PONG = "pong"
    REGISTER = "register"
    UNREGISTER = "unregister"
    DISCOVER = "discover"
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class AgentStatus(Enum):
    """Agent status states"""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class AgentInfo:
    """Agent information structure"""

    agent_id: str
    name: str
    capabilities: list[str]
    endpoint: str
    status: AgentStatus
    metadata: dict[str, Any]
    last_seen: datetime
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["last_seen"] = self.last_seen.isoformat()
        return data


@dataclass
class A2AMessage:
    """A2A Message structure"""

    message_id: str
    source_agent: str
    target_agent: str | None
    message_type: MessageType
    payload: dict[str, Any]
    timestamp: datetime
    expires_at: datetime | None = None
    priority: int = 1
    correlation_id: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["message_type"] = self.message_type.value
        data["timestamp"] = self.timestamp.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> A2AMessage:
        return cls(
            message_id=data["message_id"],
            source_agent=data["source_agent"],
            target_agent=data.get("target_agent"),
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            priority=data.get("priority", 1),
            correlation_id=data.get("correlation_id"),
        )


class A2AMessageQueue:
    """Redis-based message queue for reliable A2A communication"""

    def __init__(self, redis_url: str | None = None):
        if redis_url is None:
            password = os.environ.get("REDIS_PASSWORD", "")
            redis_url = f"redis://:{password}@localhost:6379/0" if password else "redis://localhost:6379/0"
        self.redis_url = redis_url
        self._redis: redis.Redis | None = None
        self.subscribers: dict[str, set[Callable]] = {}
        self._subscription_tasks: dict[str, asyncio.Task] = {}

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self._redis = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self._redis.ping()
            logger.info("Connected to Redis message queue")
        except Exception as e:
            logger.error("Failed to connect to Redis: %s", e)
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        # Cancel subscription tasks
        for task in self._subscription_tasks.values():
            task.cancel()
        self._subscription_tasks.clear()

        if self._redis:
            await self._redis.aclose()
            logger.info("Disconnected from Redis")

    async def publish(self, channel: str, message: A2AMessage) -> None:
        """Publish message to channel."""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        message_data = json.dumps(message.to_dict())
        await self._redis.publish(channel, message_data)

        # Also store in persistent queue for reliability
        queue_key = f"queue:{channel}"
        await self._redis.lpush(queue_key, message_data)

        logger.debug("Published message %s to %s", message.message_id, channel)

    async def subscribe(self, agent_id: str, callback: Callable) -> None:
        """Subscribe to agent-specific channel."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = set()
        self.subscribers[agent_id].add(callback)

        # Only spawn ONE subscription task per agent
        if agent_id not in self._subscription_tasks:
            task = asyncio.create_task(self._subscription_handler(agent_id))
            self._subscription_tasks[agent_id] = task

        logger.info("Subscribed agent %s to message queue", agent_id)

    async def _subscription_handler(self, agent_id: str) -> None:
        """Handle subscription for agent."""
        if not self._redis:
            return

        pubsub = self._redis.pubsub()
        try:
            await pubsub.subscribe(f"agent:{agent_id}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        message_data = json.loads(message["data"])
                        a2a_message = A2AMessage.from_dict(message_data)

                        for callback in self.subscribers.get(agent_id, set()):
                            try:
                                await callback(a2a_message)
                            except Exception as e:
                                logger.error("Callback error for %s: %s", agent_id, e)
                    except Exception as e:
                        logger.error("Message processing error: %s", e)
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe()
            await pubsub.aclose()

    async def get_queued_messages(self, agent_id: str, limit: int = 10) -> list[A2AMessage]:
        """Get queued messages for agent."""
        if not self._redis:
            return []

        queue_key = f"queue:agent:{agent_id}"
        messages: list[A2AMessage] = []

        for _ in range(limit):
            message_data = await self._redis.rpop(queue_key)
            if not message_data:
                break

            try:
                message = A2AMessage.from_dict(json.loads(message_data))

                # Check if message expired
                if message.expires_at and datetime.now() > message.expires_at:
                    continue

                messages.append(message)
            except Exception as e:
                logger.error("Failed to parse queued message: %s", e)

        return messages


class AgentRegistry:
    """Agent discovery and registry service"""

    def __init__(self, db_path: str = "agents_registry.db"):
        self.db_path = Path(db_path)
        self.agents: dict[str, AgentInfo] = {}
        self.capabilities_index: dict[str, set[str]] = {}
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

        self._load_agents_from_db()
        logger.info("Agent registry initialized with %d agents", len(self.agents))

    def _load_agents_from_db(self) -> None:
        """Load agents from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM agents")

        for row in cursor.fetchall():
            agent_info = AgentInfo(
                agent_id=row[0],
                name=row[1],
                capabilities=json.loads(row[2]),
                endpoint=row[3],
                status=AgentStatus(row[4]),
                metadata=json.loads(row[5]),
                last_seen=datetime.fromisoformat(row[6]),
                version=row[7],
            )
            self.agents[agent_info.agent_id] = agent_info

            for capability in agent_info.capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = set()
                self.capabilities_index[capability].add(agent_info.agent_id)

        conn.close()

    async def register_agent(self, agent_info: AgentInfo) -> bool:
        """Register or update agent."""
        try:
            self.agents[agent_info.agent_id] = agent_info

            for capability in agent_info.capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = set()
                self.capabilities_index[capability].add(agent_info.agent_id)

            # Run sqlite3 in thread to avoid blocking the event loop
            await asyncio.to_thread(self._save_agent_to_db, agent_info)

            logger.info("Registered agent: %s (%s)", agent_info.name, agent_info.agent_id)
            return True

        except Exception as e:
            logger.error("Failed to register agent %s: %s", agent_info.agent_id, e)
            return False

    def _save_agent_to_db(self, agent_info: AgentInfo) -> None:
        """Save agent to SQLite (runs in thread)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO agents
            (agent_id, name, capabilities, endpoint, status, metadata, last_seen, version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_info.agent_id,
                agent_info.name,
                json.dumps(agent_info.capabilities),
                agent_info.endpoint,
                agent_info.status.value,
                json.dumps(agent_info.metadata),
                agent_info.last_seen.isoformat(),
                agent_info.version,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent."""
        try:
            if agent_id not in self.agents:
                return False

            agent_info = self.agents[agent_id]

            for capability in agent_info.capabilities:
                if capability in self.capabilities_index:
                    self.capabilities_index[capability].discard(agent_id)
                    if not self.capabilities_index[capability]:
                        del self.capabilities_index[capability]

            del self.agents[agent_id]

            await asyncio.to_thread(self._delete_agent_from_db, agent_id)

            logger.info("Unregistered agent: %s", agent_id)
            return True

        except Exception as e:
            logger.error("Failed to unregister agent %s: %s", agent_id, e)
            return False

    def _delete_agent_from_db(self, agent_id: str) -> None:
        """Delete agent from SQLite (runs in thread)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
        conn.commit()
        conn.close()

    def discover_agents(self, capability: str | None = None) -> list[AgentInfo]:
        """Discover agents by capability."""
        if capability:
            agent_ids = self.capabilities_index.get(capability, set())
            return [self.agents[aid] for aid in agent_ids if aid in self.agents]
        return list(self.agents.values())

    def get_agent(self, agent_id: str) -> AgentInfo | None:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status."""
        if agent_id not in self.agents:
            return False

        self.agents[agent_id].status = status
        self.agents[agent_id].last_seen = datetime.now()

        await asyncio.to_thread(
            self._update_agent_status_in_db,
            agent_id,
            status,
            datetime.now().isoformat(),
        )
        return True

    def _update_agent_status_in_db(self, agent_id: str, status: AgentStatus, iso_now: str) -> None:
        """Update agent status in SQLite (runs in thread)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE agents SET status = ?, last_seen = ? WHERE agent_id = ?",
            (status.value, iso_now, agent_id),
        )
        conn.commit()
        conn.close()

    async def cleanup_stale_agents(self, timeout_minutes: int = 10) -> None:
        """Remove agents that haven't been seen recently."""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        stale_agents = [aid for aid, info in self.agents.items() if info.last_seen < cutoff_time]

        for agent_id in stale_agents:
            await self.unregister_agent(agent_id)

        if stale_agents:
            logger.info("Cleaned up %d stale agents", len(stale_agents))


class A2AProtocolGateway:
    """Enhanced A2A protocol gateway with routing and fault tolerance"""

    def __init__(self, port: int = 8001):
        self.port = port
        self.message_queue = A2AMessageQueue()
        self.agent_registry = AgentRegistry()
        self.connections: dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: dict[MessageType, Callable] = {}
        self.start_time: float = 0.0
        self.stats: dict[str, int] = {
            "messages_sent": 0,
            "messages_received": 0,
            "connections_active": 0,
            "errors": 0,
        }

        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self.message_handlers[MessageType.PING] = self._handle_ping
        self.message_handlers[MessageType.REGISTER] = self._handle_register
        self.message_handlers[MessageType.UNREGISTER] = self._handle_unregister
        self.message_handlers[MessageType.DISCOVER] = self._handle_discover
        self.message_handlers[MessageType.REQUEST] = self._handle_request
        self.message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat

    async def start_server(self) -> None:
        """Start the A2A WebSocket server."""
        await self.message_queue.connect()
        self.start_time = time.time()

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

        # Start WebSocket server
        async with websockets.serve(
            self._handle_connection,
            "localhost",
            self.port,
        ):
            logger.info("A2A Protocol Gateway started on ws://localhost:%d", self.port)
            await asyncio.Future()  # Run forever

    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Handle new WebSocket connections."""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        self.stats["connections_active"] += 1

        logger.info("New A2A connection: %s", connection_id)

        try:
            async for message in websocket:
                await self._process_message(connection_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info("A2A connection closed: %s", connection_id)
        except Exception as e:
            logger.error("A2A connection error %s: %s", connection_id, e)
            self.stats["errors"] += 1
        finally:
            self.connections.pop(connection_id, None)
            self.stats["connections_active"] -= 1

    async def _process_message(self, connection_id: str, raw_message: str | bytes) -> None:
        """Process incoming A2A message."""
        try:
            message_data = json.loads(raw_message)
            message = A2AMessage.from_dict(message_data)

            self.stats["messages_received"] += 1

            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(connection_id, message)
            else:
                await self._send_error(connection_id, f"Unknown message type: {message.message_type}")

        except Exception as e:
            logger.error("Message processing error: %s", e)
            await self._send_error(connection_id, f"Message processing error: {e}")
            self.stats["errors"] += 1

    async def _handle_ping(self, connection_id: str, message: A2AMessage) -> None:
        """Handle ping message."""
        pong_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=message.source_agent,
            message_type=MessageType.PONG,
            payload={"timestamp": datetime.now().isoformat()},
            timestamp=datetime.now(),
            correlation_id=message.message_id,
        )
        await self._send_message(connection_id, pong_message)

    async def _handle_register(self, connection_id: str, message: A2AMessage) -> None:
        """Handle agent registration."""
        try:
            agent_data = message.payload
            agent_info = AgentInfo(
                agent_id=agent_data["agent_id"],
                name=agent_data["name"],
                capabilities=agent_data["capabilities"],
                endpoint=agent_data.get("endpoint", f"ws://{connection_id}"),
                status=AgentStatus(agent_data.get("status", "online")),
                metadata=agent_data.get("metadata", {}),
                last_seen=datetime.now(),
                version=agent_data.get("version", "1.0.0"),
            )

            success = await self.agent_registry.register_agent(agent_info)

            response = A2AMessage(
                message_id=str(uuid.uuid4()),
                source_agent="a2a_gateway",
                target_agent=message.source_agent,
                message_type=MessageType.RESPONSE,
                payload={
                    "success": success,
                    "agent_id": agent_info.agent_id,
                    "message": "Agent registered successfully" if success else "Registration failed",
                },
                timestamp=datetime.now(),
                correlation_id=message.message_id,
            )

            await self._send_message(connection_id, response)

        except Exception as e:
            await self._send_error(connection_id, f"Registration error: {e}")

    async def _handle_unregister(self, connection_id: str, message: A2AMessage) -> None:
        """Handle agent unregistration."""
        agent_id = message.payload.get("agent_id", message.source_agent)
        success = await self.agent_registry.unregister_agent(agent_id)

        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=message.source_agent,
            message_type=MessageType.RESPONSE,
            payload={
                "success": success,
                "agent_id": agent_id,
                "message": "Agent unregistered" if success else "Agent not found",
            },
            timestamp=datetime.now(),
            correlation_id=message.message_id,
        )
        await self._send_message(connection_id, response)

    async def _handle_discover(self, connection_id: str, message: A2AMessage) -> None:
        """Handle agent discovery."""
        capability = message.payload.get("capability")
        agents = self.agent_registry.discover_agents(capability)

        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=message.source_agent,
            message_type=MessageType.RESPONSE,
            payload={
                "agents": [agent.to_dict() for agent in agents],
                "count": len(agents),
                "capability": capability,
            },
            timestamp=datetime.now(),
            correlation_id=message.message_id,
        )

        await self._send_message(connection_id, response)

    async def _handle_request(self, connection_id: str, message: A2AMessage) -> None:
        """Handle agent request routing."""
        target_agent = message.target_agent

        if target_agent:
            await self.message_queue.publish(f"agent:{target_agent}", message)
        else:
            await self._broadcast_message(message)

    async def _handle_heartbeat(self, connection_id: str, message: A2AMessage) -> None:
        """Handle agent heartbeat."""
        agent_id = message.source_agent
        await self.agent_registry.update_agent_status(agent_id, AgentStatus.ONLINE)

        response = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=agent_id,
            message_type=MessageType.RESPONSE,
            payload={"heartbeat_ack": True},
            timestamp=datetime.now(),
            correlation_id=message.message_id,
        )

        await self._send_message(connection_id, response)

    async def _send_message(self, connection_id: str, message: A2AMessage) -> None:
        """Send message to specific connection."""
        if connection_id in self.connections:
            try:
                websocket = self.connections[connection_id]
                await websocket.send(json.dumps(message.to_dict()))
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.error("Failed to send message to %s: %s", connection_id, e)

    async def _broadcast_message(self, message: A2AMessage) -> None:
        """Broadcast message to all connections."""
        message_json = json.dumps(message.to_dict())

        # Iterate over a COPY to avoid mutation during iteration
        for connection_id, websocket in list(self.connections.items()):
            try:
                await websocket.send(message_json)
                self.stats["messages_sent"] += 1
            except Exception as e:
                logger.error("Broadcast failed to %s: %s", connection_id, e)

    async def _send_error(self, connection_id: str, error_message: str) -> None:
        """Send error message."""
        error_msg = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent="a2a_gateway",
            target_agent=None,
            message_type=MessageType.ERROR,
            payload={"error": error_message},
            timestamp=datetime.now(),
        )
        await self._send_message(connection_id, error_msg)

    async def _cleanup_task(self) -> None:
        """Periodic cleanup task."""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                await self.agent_registry.cleanup_stale_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Cleanup task error: %s", e)

    def get_stats(self) -> dict[str, Any]:
        """Get gateway statistics."""
        return {
            **self.stats,
            "registered_agents": len(self.agent_registry.agents),
            "capabilities": list(self.agent_registry.capabilities_index.keys()),
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0,
        }


class A2AClient:
    """A2A client for connecting to an A2A gateway."""

    def __init__(self, agent_id: str, name: str, capabilities: list[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.websocket: websockets.WebSocketServerProtocol | None = None
        self.message_handlers: dict[MessageType, Callable] = {}
        self._pending_requests: dict[str, asyncio.Future] = {}

    async def connect(self, gateway_url: str = "ws://localhost:8001") -> None:
        """Connect to A2A gateway."""
        self.websocket = await websockets.connect(gateway_url)

        register_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=None,
            message_type=MessageType.REGISTER,
            payload={
                "agent_id": self.agent_id,
                "name": self.name,
                "capabilities": self.capabilities,
                "status": "online",
            },
            timestamp=datetime.now(),
        )

        await self.websocket.send(json.dumps(register_message.to_dict()))

        # Start message handler
        asyncio.create_task(self._message_handler())
        logger.info("A2A client %s connected and registered", self.name)

    async def _message_handler(self) -> None:
        """Handle incoming messages."""
        if not self.websocket:
            return

        try:
            async for raw_message in self.websocket:
                try:
                    a2a_message = A2AMessage.from_dict(json.loads(raw_message))

                    # Resolve pending correlation
                    if a2a_message.correlation_id and a2a_message.correlation_id in self._pending_requests:
                        future = self._pending_requests.pop(a2a_message.correlation_id)
                        if not future.done():
                            future.set_result(a2a_message)
                        continue

                    handler = self.message_handlers.get(a2a_message.message_type)
                    if handler:
                        await handler(a2a_message)

                except Exception as e:
                    logger.error("Client message handler error: %s", e)
        except websockets.exceptions.ConnectionClosed:
            logger.info("A2A client disconnected")
        except asyncio.CancelledError:
            pass

    async def send_message(
        self,
        target_agent: str,
        payload: dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
    ) -> None:
        """Send message to another agent."""
        if not self.websocket:
            raise RuntimeError("Not connected to gateway")

        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=target_agent,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(),
        )

        await self.websocket.send(json.dumps(message.to_dict()))

    async def discover_agents(self, capability: str | None = None, timeout: float = 5.0) -> list[AgentInfo]:
        """Discover agents with specific capability."""
        if not self.websocket:
            raise RuntimeError("Not connected to gateway")

        correlation_id = str(uuid.uuid4())
        future: asyncio.Future[A2AMessage] = asyncio.get_event_loop().create_future()
        self._pending_requests[correlation_id] = future

        discover_message = A2AMessage(
            message_id=correlation_id,
            source_agent=self.agent_id,
            target_agent=None,
            message_type=MessageType.DISCOVER,
            payload={"capability": capability} if capability else {},
            timestamp=datetime.now(),
        )

        await self.websocket.send(json.dumps(discover_message.to_dict()))

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            agents_data = response.payload.get("agents", [])
            return [
                AgentInfo(
                    agent_id=a["agent_id"],
                    name=a["name"],
                    capabilities=a["capabilities"],
                    endpoint=a["endpoint"],
                    status=AgentStatus(a["status"]),
                    metadata=a["metadata"],
                    last_seen=datetime.fromisoformat(a["last_seen"]),
                    version=a.get("version", "1.0.0"),
                )
                for a in agents_data
            ]
        except asyncio.TimeoutError:
            logger.warning("Discover agents request timed out")
            return []
        finally:
            self._pending_requests.pop(correlation_id, None)

    async def disconnect(self) -> None:
        """Disconnect from gateway."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None


async def main() -> None:
    """Start the A2A Protocol Gateway."""
    gateway = A2AProtocolGateway(port=8001)

    logger.info("Starting Enhanced A2A Communication System...")

    try:
        await gateway.start_server()
    except KeyboardInterrupt:
        logger.info("Shutting down A2A gateway...")
    except Exception as e:
        logger.error("A2A gateway error: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
