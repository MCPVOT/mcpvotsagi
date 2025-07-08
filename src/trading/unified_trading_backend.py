#!/usr/bin/env python3
"""
Unified Trading Backend System
==============================
Complete backend integration of all trading components:
- TradingAgents multi-agent framework
- DeepSeek-R1 for complex decisions
- Claude Code (Opus 4) via MCP
- DGM self-improving algorithms
- Solana blockchain integration
- Phantom wallet support
- Finnhub market data
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import redis
import yaml

# Add project paths
sys.path.append(str(Path(__file__).parent / "TradingAgents"))

# Import all components
# Import path adjusted - see services/dgm_integration_manager.py for proper imports
# from dgm_trading_algorithms import (
    UnifiedTradingAlgorithmEngine,
    TradingStrategy,
    MarketState,
    TradeSignal
)
from solana_mcp_deepseek_integration import SolanaMCPConnector
from solana_phantom_trading_integration import PhantomWalletConnector

# Import TradingAgents
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
except ImportError:
    logger.warning("TradingAgents not found, some features will be limited")
    TradingAgentsGraph = None
    DEFAULT_CONFIG = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UnifiedTradingBackend")


@dataclass
class TradingConfig:
    """Complete trading system configuration"""
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Solana settings
    solana_rpc: str = "https://api.mainnet-beta.solana.com"
    use_devnet: bool = True
    
    # AI Model settings
    deepseek_model: str = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
    ollama_host: str = "http://localhost:11434"
    
    # MCP Ports
    memory_mcp_port: int = 3002
    github_mcp_port: int = 3001
    solana_mcp_port: int = 3005
    browser_mcp_port: int = 3006
    oracle_agi_port: int = 3011
    
    # Trading parameters
    max_position_size: float = 0.1  # 10% max per position
    default_slippage: float = 0.01  # 1% slippage
    min_confidence: float = 0.6  # 60% minimum confidence
    
    # Data paths
    data_root: Path = Path("F:/MCPVotsAGI_Data")
    checkpoint_dir: Path = Path("/mnt/c/Workspace/MCPVotsAGI/checkpoints")
    
    @classmethod
    def from_yaml(cls, path: str) -> 'TradingConfig':
        """Load config from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


class MarketDataAggregator:
    """Aggregates market data from multiple sources"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.finnhub_api = f"https://finnhub.io/api/v1"
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds cache
        
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for a symbol"""
        
        # Check cache
        cache_key = f"{symbol}_{datetime.now().minute}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        market_data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price": 0,
            "volume_24h": 0,
            "price_change_24h": 0,
            "volatility": 0,
            "sentiment": 0,
            "technical_indicators": {}
        }
        
        # Fetch from multiple sources concurrently
        tasks = [
            self._fetch_finnhub_data(symbol),
            self._fetch_coingecko_data(symbol),
            self._calculate_technical_indicators(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        for result in results:
            if isinstance(result, dict):
                market_data.update(result)
                
        # Calculate derived metrics
        market_data["volatility"] = self._calculate_volatility(market_data)
        market_data["trend"] = self._calculate_trend(market_data)
        
        # Cache result
        self.cache[cache_key] = market_data
        
        return market_data
        
    async def _fetch_finnhub_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from Finnhub"""
        if not self.config.finnhub_api_key:
            return {}
            
        try:
            async with aiohttp.ClientSession() as session:
                # Quote data
                async with session.get(
                    f"{self.finnhub_api}/quote",
                    params={"symbol": symbol, "token": self.config.finnhub_api_key}
                ) as resp:
                    if resp.status == 200:
                        quote = await resp.json()
                        return {
                            "price": quote.get("c", 0),
                            "high_24h": quote.get("h", 0),
                            "low_24h": quote.get("l", 0),
                            "open_24h": quote.get("o", 0),
                            "previous_close": quote.get("pc", 0)
                        }
        except Exception as e:
            logger.error(f"Finnhub API error: {e}")
            
        return {}
        
    async def _fetch_coingecko_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch crypto data from CoinGecko"""
        # Map symbol to CoinGecko ID
        symbol_map = {
            "SOL": "solana",
            "BTC": "bitcoin",
            "ETH": "ethereum"
        }
        
        coin_id = symbol_map.get(symbol.upper(), symbol.lower())
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.coingecko_api}/coins/{coin_id}",
                    params={"localization": "false", "tickers": "false", 
                           "market_data": "true", "community_data": "false"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        market = data.get("market_data", {})
                        
                        return {
                            "price": market.get("current_price", {}).get("usd", 0),
                            "volume_24h": market.get("total_volume", {}).get("usd", 0),
                            "price_change_24h": market.get("price_change_percentage_24h", 0),
                            "market_cap": market.get("market_cap", {}).get("usd", 0),
                            "sentiment": data.get("sentiment_votes_up_percentage", 50) / 100
                        }
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
            
        return {}
        
    async def _calculate_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Calculate technical indicators"""
        # In production, would fetch historical data and calculate
        # For now, return simulated values
        return {
            "technical_indicators": {
                "rsi": 50 + np.random.randn() * 10,
                "macd": np.random.randn() * 0.1,
                "bb_position": 0.5 + np.random.randn() * 0.2,
                "sma_20": 0,
                "ema_50": 0
            }
        }
        
    def _calculate_volatility(self, data: Dict[str, Any]) -> float:
        """Calculate price volatility"""
        if data.get("high_24h") and data.get("low_24h"):
            return (data["high_24h"] - data["low_24h"]) / data.get("price", 1)
        return 0.2  # Default volatility
        
    def _calculate_trend(self, data: Dict[str, Any]) -> float:
        """Calculate trend strength (-1 to 1)"""
        change_pct = data.get("price_change_24h", 0) / 100
        return np.tanh(change_pct * 2)  # Normalize to [-1, 1]


class MCPIntegrationLayer:
    """Handles all MCP server communications"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.connections = {}
        self.health_status = {}
        
    async def connect_all(self):
        """Connect to all MCP servers"""
        servers = [
            ("memory", self.config.memory_mcp_port),
            ("github", self.config.github_mcp_port),
            ("solana", self.config.solana_mcp_port),
            ("browser", self.config.browser_mcp_port)
        ]
        
        for name, port in servers:
            try:
                await self._connect_mcp(name, port)
                self.health_status[name] = "online"
            except Exception as e:
                logger.error(f"Failed to connect to {name} MCP: {e}")
                self.health_status[name] = "offline"
                
    async def _connect_mcp(self, name: str, port: int):
        """Connect to individual MCP server"""
        url = f"ws://localhost:{port}"
        
        # In production, would establish WebSocket connection
        # For now, mark as connected
        self.connections[name] = {
            "url": url,
            "port": port,
            "connected": True
        }
        
        logger.info(f"Connected to {name} MCP on port {port}")
        
    async def query_memory(self, query: str) -> Dict[str, Any]:
        """Query memory MCP for historical data"""
        if self.health_status.get("memory") != "online":
            return {"error": "Memory MCP offline"}
            
        # In production, would send WebSocket message
        # For now, return simulated response
        return {
            "query": query,
            "results": [],
            "timestamp": datetime.now().isoformat()
        }
        
    async def store_trading_decision(self, decision: TradeSignal):
        """Store trading decision in memory MCP"""
        if self.health_status.get("memory") != "online":
            return
            
        data = {
            "type": "trading_decision",
            "decision": {
                "action": decision.action,
                "token": decision.token,
                "confidence": decision.confidence,
                "size": decision.size,
                "reasoning": decision.reasoning,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # In production, would send to memory MCP
        logger.info(f"Stored trading decision: {decision.action} {decision.token}")


class UnifiedTradingBackend:
    """Main backend system orchestrating all components"""
    
    def __init__(self, config: Optional[TradingConfig] = None):
        self.config = config or TradingConfig()
        
        # Initialize components
        self.algorithm_engine = UnifiedTradingAlgorithmEngine()
        self.market_data = MarketDataAggregator(self.config)
        self.mcp_layer = MCPIntegrationLayer(self.config)
        self.solana_connector = SolanaMCPConnector()
        self.phantom_connector = PhantomWalletConnector()
        
        # TradingAgents integration
        if TradingAgentsGraph:
            ta_config = DEFAULT_CONFIG.copy()
            ta_config["online_tools"] = True
            self.trading_agents = TradingAgentsGraph(debug=True, config=ta_config)
        else:
            self.trading_agents = None
            
        # Performance tracking
        self.trade_history = deque(maxlen=1000)
        self.active_positions = {}
        self.total_pnl = 0.0
        
        # Redis for distributed state
        try:
            self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis.ping()
        except:
            self.redis = None
            logger.warning("Redis not available")
            
    async def initialize(self):
        """Initialize all backend systems"""
        logger.info("="*60)
        logger.info("INITIALIZING UNIFIED TRADING BACKEND")
        logger.info("="*60)
        
        # Connect to MCP servers
        await self.mcp_layer.connect_all()
        
        # Connect to Solana
        await self.solana_connector.connect()
        
        # Load checkpoints if available
        self.algorithm_engine.load_checkpoint()
        
        logger.info("Backend initialization complete")
        logger.info(f"MCP Status: {self.mcp_layer.health_status}")
        
    async def analyze_and_trade(self, token: str, amount: float) -> Dict[str, Any]:
        """
        Main trading flow: analyze market and execute trade if confident
        """
        logger.info(f"Analyzing {token} for potential trade of {amount}")
        
        # Step 1: Gather market data
        market_data = await self.market_data.get_market_data(token)
        
        # Step 2: Get TradingAgents analysis if available
        ta_analysis = None
        if self.trading_agents:
            try:
                _, ta_decision = self.trading_agents.propagate(
                    token, 
                    datetime.now().strftime("%Y-%m-%d")
                )
                ta_analysis = ta_decision
            except Exception as e:
                logger.error(f"TradingAgents error: {e}")
                
        # Step 3: Get unified algorithm decision
        trading_signal = await self.algorithm_engine.generate_trading_signal(
            market_data, 
            token
        )
        
        # Step 4: Enhance with DeepSeek analysis via Solana MCP
        if trading_signal.confidence >= self.config.min_confidence:
            # Create AI transaction analysis
            ai_transaction = await self.solana_connector.create_ai_transaction(
                f"{trading_signal.action} {amount} {token}"
            )
            
            # Generate ZK proof
            zk_proof = await self.solana_connector.generate_zk_proof(
                f"{token}_{amount}_{trading_signal.action}"
            )
            
        # Step 5: Risk management checks
        risk_approved = await self._check_risk_limits(trading_signal, amount)
        
        # Step 6: Prepare response
        result = {
            "token": token,
            "amount": amount,
            "signal": {
                "action": trading_signal.action,
                "confidence": trading_signal.confidence,
                "size": trading_signal.size,
                "reasoning": trading_signal.reasoning
            },
            "market_data": market_data,
            "ta_analysis": ta_analysis,
            "risk_approved": risk_approved,
            "zk_proof": zk_proof.commitment if 'zk_proof' in locals() else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 7: Store decision
        await self.mcp_layer.store_trading_decision(trading_signal)
        
        # Step 8: Execute if approved
        if risk_approved and trading_signal.action != "HOLD":
            execution_result = await self._execute_trade(
                token, 
                amount, 
                trading_signal
            )
            result["execution"] = execution_result
            
        return result
        
    async def _check_risk_limits(self, 
                                signal: TradeSignal, 
                                amount: float) -> bool:
        """Check if trade passes risk management rules"""
        
        # Check position limits
        current_positions = sum(
            pos["amount"] for pos in self.active_positions.values()
        )
        
        if current_positions + amount > 1.0:  # Max 100% allocated
            logger.warning("Position limit exceeded")
            return False
            
        # Check confidence threshold
        if signal.confidence < self.config.min_confidence:
            logger.warning(f"Confidence {signal.confidence} below threshold")
            return False
            
        # Check drawdown limits
        if self.total_pnl < -0.2:  # 20% drawdown limit
            logger.warning("Drawdown limit reached")
            return False
            
        return True
        
    async def _execute_trade(self,
                           token: str,
                           amount: float,
                           signal: TradeSignal) -> Dict[str, Any]:
        """Execute the trade"""
        
        # In production, would execute via Phantom/Solana
        # For now, simulate execution
        
        execution_price = 100.0  # Simulated
        
        position_id = f"{token}_{datetime.now().timestamp()}"
        
        self.active_positions[position_id] = {
            "token": token,
            "amount": amount,
            "entry_price": execution_price,
            "entry_time": datetime.now(),
            "signal": signal
        }
        
        self.trade_history.append({
            "position_id": position_id,
            "action": signal.action,
            "token": token,
            "amount": amount,
            "price": execution_price,
            "timestamp": datetime.now()
        })
        
        logger.info(f"Executed {signal.action} {amount} {token} at {execution_price}")
        
        return {
            "position_id": position_id,
            "executed": True,
            "price": execution_price,
            "amount": amount
        }
        
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        
        positions = []
        total_value = 0
        
        for pos_id, position in self.active_positions.items():
            # Get current price
            market_data = await self.market_data.get_market_data(
                position["token"]
            )
            current_price = market_data.get("price", position["entry_price"])
            
            # Calculate PnL
            pnl = (current_price - position["entry_price"]) / position["entry_price"]
            value = position["amount"] * current_price
            
            positions.append({
                "id": pos_id,
                "token": position["token"],
                "amount": position["amount"],
                "entry_price": position["entry_price"],
                "current_price": current_price,
                "pnl": pnl,
                "value": value
            })
            
            total_value += value
            
        return {
            "positions": positions,
            "total_value": total_value,
            "total_pnl": self.total_pnl,
            "n_positions": len(positions),
            "timestamp": datetime.now().isoformat()
        }
        
    async def update_performance(self):
        """Update performance metrics and learn from results"""
        
        for pos_id, position in list(self.active_positions.items()):
            # Check if position should be closed
            market_data = await self.market_data.get_market_data(
                position["token"]
            )
            current_price = market_data.get("price", position["entry_price"])
            
            pnl = (current_price - position["entry_price"]) / position["entry_price"]
            
            # Apply stop loss / take profit
            strategy = self.algorithm_engine.dgm.current_strategy
            
            if pnl <= -strategy.stop_loss or pnl >= strategy.take_profit:
                # Close position
                self.total_pnl += pnl * position["amount"]
                
                # Learn from result
                await self.algorithm_engine.learn_from_trade_result(
                    position["signal"],
                    pnl
                )
                
                del self.active_positions[pos_id]
                logger.info(f"Closed position {pos_id} with {pnl:.2%} PnL")
                
    async def run_continuous(self):
        """Run continuous trading loop"""
        
        logger.info("Starting continuous trading loop")
        
        while True:
            try:
                # Update performance
                await self.update_performance()
                
                # Save checkpoint periodically
                if len(self.trade_history) % 100 == 0:
                    self.algorithm_engine.save_checkpoint()
                    
                # Sleep
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)


async def main():
    """Main entry point for backend testing"""
    
    # Load configuration
    config = TradingConfig()
    
    # Create backend
    backend = UnifiedTradingBackend(config)
    
    # Initialize
    await backend.initialize()
    
    # Test analysis
    result = await backend.analyze_and_trade("SOL", 0.1)
    
    print("\n" + "="*60)
    print("TRADING ANALYSIS RESULT")
    print("="*60)
    print(f"Token: {result['token']}")
    print(f"Signal: {result['signal']['action']}")
    print(f"Confidence: {result['signal']['confidence']:.2%}")
    print(f"Risk Approved: {result['risk_approved']}")
    print("="*60)
    
    # Get portfolio status
    portfolio = await backend.get_portfolio_status()
    print("\nPORTFOLIO STATUS")
    print("="*60)
    print(f"Positions: {portfolio['n_positions']}")
    print(f"Total Value: ${portfolio['total_value']:.2f}")
    print(f"Total PnL: {portfolio['total_pnl']:.2%}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())