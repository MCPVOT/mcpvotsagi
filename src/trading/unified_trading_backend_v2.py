#!/usr/bin/env python3
"""
Unified Trading Backend System V2
=================================
Refactored with improved architecture, error handling, and performance
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import redis
import yaml
from contextlib import asynccontextmanager
import aioredis
from functools import lru_cache, wraps
import backoff
import prometheus_client as prom

# Add project paths
sys.path.append(str(Path(__file__).parent / "TradingAgents"))

# Metrics
trade_counter = prom.Counter('trades_total', 'Total number of trades', ['action', 'token'])
trade_latency = prom.Histogram('trade_latency_seconds', 'Trade execution latency')
error_counter = prom.Counter('errors_total', 'Total number of errors', ['component'])

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trading_backend.log')
    ]
)
logger = logging.getLogger("UnifiedTradingBackend")


class TradingAction(Enum):
    """Trading action enumeration"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class TradingConfigV2:
    """Enhanced trading system configuration with validation"""
    # API Keys
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    finnhub_api_key: str = field(default_factory=lambda: os.getenv("FINNHUB_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))

    # Solana settings
    solana_rpc: str = "https://api.mainnet-beta.solana.com"
    solana_ws: str = "wss://api.mainnet-beta.solana.com"
    use_devnet: bool = True

    # AI Model settings
    deepseek_model: str = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
    ollama_host: str = "http://localhost:11434"
    model_timeout: int = 30

    # MCP Ports
    mcp_ports: Dict[str, int] = field(default_factory=lambda: {
        "memory": 3002,
        "github": 3001,
        "solana": 3005,
        "browser": 3006,
        "oracle": 3011
    })

    # Trading parameters
    max_position_size: float = 0.1
    default_slippage: float = 0.01
    min_confidence: float = 0.6
    max_drawdown: float = 0.2
    position_timeout: int = 86400  # 24 hours

    # Performance settings
    cache_ttl: int = 60
    max_concurrent_trades: int = 10
    rate_limit_per_minute: int = 60

    # Data paths
    data_root: Path = field(default_factory=lambda: Path("F:/MCPVotsAGI_Data"))
    checkpoint_dir: Path = field(default_factory=lambda: Path("/mnt/c/Workspace/MCPVotsAGI/checkpoints"))

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()
        self._ensure_directories()

    def _validate(self):
        """Validate configuration parameters"""
        if self.max_position_size > 1.0 or self.max_position_size <= 0:
            raise ValueError("max_position_size must be between 0 and 1")

        if self.min_confidence < 0 or self.min_confidence > 1:
            raise ValueError("min_confidence must be between 0 and 1")

        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not set - market data will be limited")

    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'TradingConfigV2':
        """Load configuration from YAML file with validation"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


class RateLimiter:
    """Rate limiting with sliding window"""

    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire rate limit slot"""
        async with self._lock:
            now = datetime.now()

            # Remove old calls outside window
            while self.calls and (now - self.calls[0]).seconds > self.window_seconds:
                self.calls.popleft()

            # Check if we can make a call
            if len(self.calls) >= self.max_calls:
                sleep_time = self.window_seconds - (now - self.calls[0]).seconds
                await asyncio.sleep(sleep_time)
                return await self.acquire()

            self.calls.append(now)


def with_retry(max_attempts: int = 3, backoff_factor: float = 2.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")

            raise last_exception

        return wrapper
    return decorator


class BaseComponent(ABC):
    """Base class for all system components"""

    def __init__(self, name: str, config: TradingConfigV2):
        self.name = name
        self.config = config
        self.status = ComponentStatus.HEALTHY
        self.last_health_check = datetime.now()
        self._initialized = False

    async def initialize(self):
        """Initialize component"""
        if not self._initialized:
            await self._initialize()
            self._initialized = True
            logger.info(f"{self.name} initialized successfully")

    @abstractmethod
    async def _initialize(self):
        """Component-specific initialization"""
        pass

    @abstractmethod
    async def health_check(self) -> ComponentStatus:
        """Check component health"""
        pass

    async def cleanup(self):
        """Cleanup component resources"""
        logger.info(f"Cleaning up {self.name}")


class CacheManager:
    """Centralized cache management with TTL and LRU eviction"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._access_count: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.now() < expiry:
                    self._access_count[key] += 1
                    return value
                else:
                    del self._cache[key]
                    del self._access_count[key]
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        async with self._lock:
            # Evict LRU items if cache is full
            if len(self._cache) >= self.max_size:
                lru_key = min(self._access_count, key=self._access_count.get)
                del self._cache[lru_key]
                del self._access_count[lru_key]

            ttl = ttl or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)
            self._access_count[key] = 1

    async def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        async with self._lock:
            if pattern:
                keys_to_delete = [k for k in self._cache if pattern in k]
                for key in keys_to_delete:
                    del self._cache[key]
                    self._access_count.pop(key, None)
            else:
                self._cache.clear()
                self._access_count.clear()


class EnhancedMarketDataAggregator(BaseComponent):
    """Enhanced market data aggregation with caching and fallbacks"""

    def __init__(self, config: TradingConfigV2):
        super().__init__("MarketDataAggregator", config)
        self.cache = CacheManager(max_size=500, default_ttl=config.cache_ttl)
        self.rate_limiter = RateLimiter(60, 60)  # 60 requests per minute
        self.data_sources = []

    async def _initialize(self):
        """Initialize data sources"""
        # Import data sources
        from finnhub_integration import FinnhubClient

        if self.config.finnhub_api_key:
            self.data_sources.append(("finnhub", FinnhubClient(self.config.finnhub_api_key)))

        # Add more data sources as needed
        logger.info(f"Initialized {len(self.data_sources)} data sources")

    async def health_check(self) -> ComponentStatus:
        """Check data source health"""
        if not self.data_sources:
            return ComponentStatus.UNHEALTHY

        # Check at least one source is working
        for name, source in self.data_sources:
            try:
                # Simple connectivity check
                if hasattr(source, 'get_quote'):
                    await source.get_quote("AAPL")
                    return ComponentStatus.HEALTHY
            except:
                continue

        return ComponentStatus.DEGRADED

    @with_retry(max_attempts=3)
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data with caching and fallbacks"""
        # Check cache first
        cache_key = f"market_data:{symbol}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        await self.rate_limiter.acquire()

        market_data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "source": None,
            "data_quality": "unknown"
        }

        # Try each data source
        for name, source in self.data_sources:
            try:
                if name == "finnhub" and hasattr(source, 'get_quote'):
                    quote = await source.get_quote(symbol)
                    if quote:
                        market_data.update({
                            "price": quote.current_price,
                            "high_24h": quote.high,
                            "low_24h": quote.low,
                            "volume_24h": 0,  # Would need additional API call
                            "source": "finnhub",
                            "data_quality": "high"
                        })

                        # Get additional data
                        indicators = await source.get_technical_indicators(symbol)
                        market_data["technical_indicators"] = indicators

                        break

            except Exception as e:
                logger.warning(f"Failed to get data from {name}: {e}")
                continue

        # Calculate derived metrics
        if "price" in market_data and market_data.get("high_24h") and market_data.get("low_24h"):
            market_data["volatility"] = (market_data["high_24h"] - market_data["low_24h"]) / market_data["price"]
            market_data["price_position"] = (market_data["price"] - market_data["low_24h"]) / (market_data["high_24h"] - market_data["low_24h"])
        else:
            market_data["volatility"] = 0.2  # Default
            market_data["price_position"] = 0.5

        # Cache the result
        await self.cache.set(cache_key, market_data, ttl=30)  # 30 second cache

        return market_data


class AdvancedMCPIntegrationLayer(BaseComponent):
    """Advanced MCP integration with connection pooling and health monitoring"""

    def __init__(self, config: TradingConfigV2):
        super().__init__("MCPIntegration", config)
        self.connections = {}
        self.connection_pools = {}
        self.health_status = {}
        self._health_check_task = None

    async def _initialize(self):
        """Initialize MCP connections with pooling"""
        for name, port in self.config.mcp_ports.items():
            try:
                # Create connection pool for each MCP
                pool = MCPConnectionPool(name, port, max_connections=5)
                await pool.initialize()
                self.connection_pools[name] = pool
                self.health_status[name] = ComponentStatus.HEALTHY
                logger.info(f"Connected to {name} MCP on port {port}")
            except Exception as e:
                logger.error(f"Failed to connect to {name} MCP: {e}")
                self.health_status[name] = ComponentStatus.UNHEALTHY

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._monitor_health())

    async def _monitor_health(self):
        """Continuously monitor MCP health"""
        while True:
            try:
                for name, pool in self.connection_pools.items():
                    try:
                        # Perform health check
                        async with pool.acquire() as conn:
                            # Send ping or health check message
                            self.health_status[name] = ComponentStatus.HEALTHY
                    except:
                        self.health_status[name] = ComponentStatus.UNHEALTHY

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    async def health_check(self) -> ComponentStatus:
        """Check overall MCP health"""
        healthy_count = sum(1 for status in self.health_status.values()
                          if status == ComponentStatus.HEALTHY)
        total_count = len(self.health_status)

        if healthy_count == total_count:
            return ComponentStatus.HEALTHY
        elif healthy_count > 0:
            return ComponentStatus.DEGRADED
        else:
            return ComponentStatus.UNHEALTHY

    async def query_memory(self, query: str, timeout: int = 10) -> Dict[str, Any]:
        """Query memory MCP with timeout and error handling"""
        if self.health_status.get("memory") != ComponentStatus.HEALTHY:
            return {"error": "Memory MCP unavailable", "fallback": True}

        try:
            pool = self.connection_pools.get("memory")
            if pool:
                async with pool.acquire() as conn:
                    # Send query with timeout
                    result = await asyncio.wait_for(
                        conn.send_query(query),
                        timeout=timeout
                    )
                    return result
        except asyncio.TimeoutError:
            logger.error("Memory query timeout")
            error_counter.labels(component="memory_mcp").inc()
            return {"error": "Query timeout", "fallback": True}
        except Exception as e:
            logger.error(f"Memory query error: {e}")
            error_counter.labels(component="memory_mcp").inc()
            return {"error": str(e), "fallback": True}

    async def cleanup(self):
        """Cleanup MCP connections"""
        if self._health_check_task:
            self._health_check_task.cancel()

        for pool in self.connection_pools.values():
            await pool.close()


class MCPConnectionPool:
    """Connection pool for MCP servers"""

    def __init__(self, name: str, port: int, max_connections: int = 5):
        self.name = name
        self.port = port
        self.max_connections = max_connections
        self._pool = asyncio.Queue(maxsize=max_connections)
        self._created = 0

    async def initialize(self):
        """Initialize connection pool"""
        # Pre-create some connections
        for _ in range(min(2, self.max_connections)):
            conn = await self._create_connection()
            await self._pool.put(conn)

    async def _create_connection(self):
        """Create a new MCP connection"""
        try:
            # Create actual WebSocket connection to MCP server
            import websockets
            uri = f"ws://localhost:{self.port}/mcp"
            websocket = await websockets.connect(uri)
            self._created += 1
            return MCPConnection(self.name, self.port, websocket)
        except Exception as e:
            logger.error(f"Failed to create MCP connection to {self.name}:{self.port}: {e}")
            raise ConnectionError(f"Unable to connect to MCP server {self.name}:{self.port}")

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool"""
        if self._pool.empty() and self._created < self.max_connections:
            conn = await self._create_connection()
        else:
            conn = await self._pool.get()

        try:
            yield conn
        finally:
            await self._pool.put(conn)

    async def close(self):
        """Close all connections"""
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()


class MCPConnection:
    """Real MCP connection for production use"""

    def __init__(self, name: str, port: int, websocket=None):
        self.name = name
        self.port = port
        self.websocket = websocket

    async def send_query(self, query: str) -> Dict[str, Any]:
        """Send query to MCP server"""
        if not self.websocket:
            raise ConnectionError(f"No websocket connection to {self.name}")

        try:
            # Send MCP protocol message
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "query",
                "params": {"query": query}
            }
            await self.websocket.send(json.dumps(message))

            # Receive response
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"MCP query failed: {e}")
            raise

    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None


class OptimizedTradingEngine(BaseComponent):
    """Optimized trading engine with circuit breakers and risk management"""

    def __init__(self, config: TradingConfigV2):
        super().__init__("TradingEngine", config)
        self.active_trades = {}
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
        self.risk_manager = RiskManager(config)

    async def _initialize(self):
        """Initialize trading engine components"""
        # Import algorithm components
        from dgm_trading_algorithms import UnifiedTradingAlgorithmEngine

        self.algorithm_engine = UnifiedTradingAlgorithmEngine()
        self.algorithm_engine.load_checkpoint()

    async def health_check(self) -> ComponentStatus:
        """Check trading engine health"""
        if self.circuit_breaker.current_state == "open":
            return ComponentStatus.UNHEALTHY
        elif len(self.active_trades) > self.config.max_concurrent_trades * 0.8:
            return ComponentStatus.DEGRADED
        else:
            return ComponentStatus.HEALTHY

    @trade_latency.time()
    async def execute_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade with circuit breaker protection"""

        # Check circuit breaker
        if not self.circuit_breaker.call(lambda: True):
            logger.warning("Circuit breaker is open, rejecting trade")
            return {"status": "rejected", "reason": "circuit_breaker_open"}

        # Check risk limits
        risk_check = await self.risk_manager.check_trade(signal)
        if not risk_check["approved"]:
            logger.warning(f"Trade rejected by risk manager: {risk_check['reason']}")
            return {"status": "rejected", "reason": risk_check["reason"]}

        # Check concurrent trade limit
        if len(self.active_trades) >= self.config.max_concurrent_trades:
            return {"status": "rejected", "reason": "max_concurrent_trades"}

        try:
            # Execute trade
            trade_id = f"{signal['token']}_{datetime.now().timestamp()}"
            self.active_trades[trade_id] = {
                "signal": signal,
                "start_time": datetime.now(),
                "status": "executing"
            }

            # Record metrics
            trade_counter.labels(
                action=signal["action"],
                token=signal["token"]
            ).inc()

            # Simulate execution (in production, would execute via exchange)
            await asyncio.sleep(0.1)

            # Update active trades
            self.active_trades[trade_id]["status"] = "completed"

            # Success callback for circuit breaker
            self.circuit_breaker.call(lambda: True)

            return {
                "status": "executed",
                "trade_id": trade_id,
                "execution_time": datetime.now().isoformat()
            }

        except Exception as e:
            # Failure callback for circuit breaker
            self.circuit_breaker.record_failure()
            error_counter.labels(component="trading_engine").inc()

            logger.error(f"Trade execution failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def cleanup_stale_trades(self):
        """Clean up stale trades"""
        now = datetime.now()
        stale_trades = []

        for trade_id, trade in self.active_trades.items():
            if (now - trade["start_time"]).seconds > self.config.position_timeout:
                stale_trades.append(trade_id)

        for trade_id in stale_trades:
            logger.warning(f"Cleaning up stale trade: {trade_id}")
            del self.active_trades[trade_id]


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.current_state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.current_state == "open":
            if self._should_attempt_reset():
                self.current_state = "half_open"
            else:
                return None

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        return (self.last_failure_time and
                (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout)

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.current_state = "closed"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.current_state = "open"
            logger.warning("Circuit breaker opened due to repeated failures")

    def record_failure(self):
        """Manually record a failure"""
        self._on_failure()


class RiskManager:
    """Advanced risk management with position sizing and drawdown control"""

    def __init__(self, config: TradingConfigV2):
        self.config = config
        self.portfolio_value = 100000  # Example starting value
        self.current_positions = {}
        self.daily_pnl = 0
        self.max_daily_loss = config.max_drawdown * self.portfolio_value

    async def check_trade(self, signal: Dict[str, Any]) -> Dict[str, bool]:
        """Check if trade passes risk rules"""

        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return {"approved": False, "reason": "daily_loss_limit"}

        # Check position concentration
        position_value = signal.get("size", 0.1) * self.portfolio_value
        if position_value > self.config.max_position_size * self.portfolio_value:
            return {"approved": False, "reason": "position_too_large"}

        # Check correlation risk
        if await self._check_correlation_risk(signal):
            return {"approved": False, "reason": "high_correlation_risk"}

        # Calculate position size using Kelly Criterion
        optimal_size = self._calculate_kelly_size(signal)

        return {
            "approved": True,
            "recommended_size": optimal_size,
            "risk_score": self._calculate_risk_score(signal)
        }

    def _calculate_kelly_size(self, signal: Dict[str, Any]) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        win_probability = signal.get("confidence", 0.5)
        win_loss_ratio = 1.5  # Example ratio

        # Kelly formula: f = p - q/b
        # where p = win probability, q = loss probability, b = win/loss ratio
        kelly_fraction = win_probability - (1 - win_probability) / win_loss_ratio

        # Apply safety factor
        safe_kelly = kelly_fraction * 0.25  # Use 25% of Kelly

        # Ensure within limits
        return max(0.01, min(safe_kelly, self.config.max_position_size))

    async def _check_correlation_risk(self, signal: Dict[str, Any]) -> bool:
        """Check if new position increases correlation risk"""
        # Simplified check - in production would calculate actual correlations
        token = signal.get("token")
        similar_positions = sum(1 for pos in self.current_positions.values()
                              if pos.get("token") == token)

        return similar_positions >= 3  # Max 3 positions in same token

    def _calculate_risk_score(self, signal: Dict[str, Any]) -> float:
        """Calculate overall risk score for position"""
        base_risk = 1.0 - signal.get("confidence", 0.5)
        volatility_factor = signal.get("volatility", 0.2) * 2
        size_factor = signal.get("size", 0.1) / self.config.max_position_size

        return min(1.0, base_risk * (1 + volatility_factor) * (1 + size_factor))


class UnifiedTradingBackendV2:
    """Enhanced unified trading backend with improved architecture"""

    def __init__(self, config: Optional[TradingConfigV2] = None):
        self.config = config or TradingConfigV2()

        # Core components
        self.components: Dict[str, BaseComponent] = {
            "market_data": EnhancedMarketDataAggregator(self.config),
            "mcp_integration": AdvancedMCPIntegrationLayer(self.config),
            "trading_engine": OptimizedTradingEngine(self.config)
        }

        # State management
        self.state_manager = StateManager()

        # Metrics server
        self.metrics_server = None

        # Background tasks
        self._background_tasks = []

    async def initialize(self):
        """Initialize all backend systems with proper error handling"""
        logger.info("="*60)
        logger.info("INITIALIZING UNIFIED TRADING BACKEND V2")
        logger.info("="*60)

        # Initialize components in dependency order
        initialization_order = ["market_data", "mcp_integration", "trading_engine"]

        for component_name in initialization_order:
            component = self.components.get(component_name)
            if component:
                try:
                    await component.initialize()
                    logger.info(f"✓ {component_name} initialized")
                except Exception as e:
                    logger.error(f"✗ Failed to initialize {component_name}: {e}")
                    # Decide whether to continue or abort
                    if component_name in ["market_data", "trading_engine"]:
                        raise  # Critical components

        # Start background tasks
        self._start_background_tasks()

        # Start metrics server
        prom.start_http_server(8000)
        logger.info("Metrics server started on port 8000")

        # Load state
        await self.state_manager.load_state()

        logger.info("Backend initialization complete")

    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        tasks = [
            self._health_monitor(),
            self._cleanup_task(),
            self._state_persistence_task()
        ]

        for task in tasks:
            self._background_tasks.append(asyncio.create_task(task))

    async def _health_monitor(self):
        """Monitor component health"""
        while True:
            try:
                health_report = {}

                for name, component in self.components.items():
                    try:
                        status = await component.health_check()
                        health_report[name] = status.value
                    except Exception as e:
                        logger.error(f"Health check failed for {name}: {e}")
                        health_report[name] = "unknown"

                # Log health status
                unhealthy = [name for name, status in health_report.items()
                           if status != "healthy"]

                if unhealthy:
                    logger.warning(f"Unhealthy components: {unhealthy}")

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

    async def _cleanup_task(self):
        """Periodic cleanup tasks"""
        while True:
            try:
                # Clean up stale trades
                trading_engine = self.components.get("trading_engine")
                if trading_engine:
                    await trading_engine.cleanup_stale_trades()

                # Clean up cache
                market_data = self.components.get("market_data")
                if market_data and hasattr(market_data, 'cache'):
                    # Remove old cache entries
                    pass

                await asyncio.sleep(300)  # Every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")

    async def _state_persistence_task(self):
        """Persist state periodically"""
        while True:
            try:
                await self.state_manager.save_state()
                await asyncio.sleep(300)  # Every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"State persistence error: {e}")

    async def analyze_and_trade(self,
                              token: str,
                              amount: float,
                              strategy_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main trading flow with enhanced error handling and monitoring
        """
        start_time = datetime.now()
        request_id = f"{token}_{start_time.timestamp()}"

        logger.info(f"[{request_id}] Analyzing {token} for {amount}")

        try:
            # Step 1: Get market data with fallback
            market_data = await self.components["market_data"].get_market_data(token)

            if market_data.get("data_quality") == "unknown":
                logger.warning(f"[{request_id}] Low quality market data")

            # Step 2: Get trading signal
            trading_engine = self.components["trading_engine"]

            # Use algorithm engine directly for now
            signal = await trading_engine.algorithm_engine.generate_trading_signal(
                market_data,
                token
            )

            # Step 3: Apply strategy override if provided
            if strategy_override:
                signal = self._apply_strategy_override(signal, strategy_override)

            # Step 4: Risk checks
            risk_check = await trading_engine.risk_manager.check_trade({
                "token": token,
                "amount": amount,
                "action": signal.action,
                "confidence": signal.confidence,
                "size": signal.size
            })

            # Step 5: Execute if approved
            execution_result = None
            if risk_check["approved"] and signal.action != "HOLD":
                execution_result = await trading_engine.execute_trade({
                    "token": token,
                    "amount": amount * risk_check.get("recommended_size", signal.size),
                    "action": signal.action,
                    "confidence": signal.confidence
                })

            # Step 6: Store decision in memory
            await self._store_decision(request_id, signal, execution_result)

            # Calculate latency
            latency = (datetime.now() - start_time).total_seconds()

            return {
                "request_id": request_id,
                "token": token,
                "amount": amount,
                "signal": {
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "size": risk_check.get("recommended_size", signal.size),
                    "reasoning": signal.reasoning
                },
                "market_data": market_data,
                "risk_check": risk_check,
                "execution": execution_result,
                "latency": latency,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[{request_id}] Trading analysis failed: {e}")
            error_counter.labels(component="main_flow").inc()

            return {
                "request_id": request_id,
                "token": token,
                "amount": amount,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _apply_strategy_override(self, signal: Any, override: Dict[str, Any]) -> Any:
        """Apply strategy overrides to signal"""
        # Modify signal based on override parameters
        if "min_confidence" in override and signal.confidence < override["min_confidence"]:
            signal.action = "HOLD"

        if "max_position_size" in override:
            signal.size = min(signal.size, override["max_position_size"])

        return signal

    async def _store_decision(self, request_id: str, signal: Any, execution: Optional[Dict[str, Any]]):
        """Store trading decision in memory MCP"""
        try:
            mcp = self.components.get("mcp_integration")
            if mcp:
                decision_data = {
                    "request_id": request_id,
                    "signal": {
                        "action": signal.action,
                        "confidence": signal.confidence,
                        "reasoning": signal.reasoning
                    },
                    "execution": execution,
                    "timestamp": datetime.now().isoformat()
                }

                # Store in memory MCP
                await mcp.query_memory(f"STORE decision:{request_id} {json.dumps(decision_data)}")

        except Exception as e:
            logger.error(f"Failed to store decision: {e}")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "metrics": {},
            "configuration": {
                "max_position_size": self.config.max_position_size,
                "min_confidence": self.config.min_confidence,
                "max_concurrent_trades": self.config.max_concurrent_trades
            }
        }

        # Get component status
        for name, component in self.components.items():
            try:
                health = await component.health_check()
                status["components"][name] = health.value
            except:
                status["components"][name] = "unknown"

        # Get metrics
        trading_engine = self.components.get("trading_engine")
        if trading_engine:
            status["metrics"]["active_trades"] = len(trading_engine.active_trades)
            status["metrics"]["circuit_breaker"] = trading_engine.circuit_breaker.current_state

        return status

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down trading backend...")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Save final state
        await self.state_manager.save_state()

        # Cleanup components
        for component in self.components.values():
            await component.cleanup()

        logger.info("Shutdown complete")


class StateManager:
    """Manage persistent state across restarts"""

    def __init__(self, state_file: str = "trading_state.json"):
        self.state_file = Path(state_file)
        self.state = {}

    async def load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded state from {self.state_file}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

    async def save_state(self):
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self.state.get(key, default)

    def set(self, key: str, value: Any):
        """Set state value"""
        self.state[key] = value


async def main():
    """Enhanced main entry point with proper lifecycle management"""

    # Load configuration
    config_path = Path("trading_config.yaml")
    if config_path.exists():
        config = TradingConfigV2.from_yaml(config_path)
    else:
        config = TradingConfigV2()

    # Create backend
    backend = UnifiedTradingBackendV2(config)

    try:
        # Initialize
        await backend.initialize()

        # Example trade analysis
        result = await backend.analyze_and_trade(
            "SOL",
            0.1,
            strategy_override={"min_confidence": 0.7}
        )

        print("\n" + "="*60)
        print("TRADING ANALYSIS RESULT")
        print("="*60)
        print(f"Token: {result['token']}")
        print(f"Signal: {result.get('signal', {}).get('action', 'ERROR')}")
        print(f"Confidence: {result.get('signal', {}).get('confidence', 0):.2%}")
        print(f"Latency: {result.get('latency', 0):.3f}s")
        print("="*60)

        # Get system status
        status = await backend.get_system_status()
        print("\nSYSTEM STATUS")
        print("="*60)
        print(f"Components: {status['components']}")
        print(f"Active Trades: {status['metrics'].get('active_trades', 0)}")
        print("="*60)

        # Keep running for demo
        await asyncio.sleep(5)

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Graceful shutdown
        await backend.shutdown()


if __name__ == "__main__":
    asyncio.run(main())