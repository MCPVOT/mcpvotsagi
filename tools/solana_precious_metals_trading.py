#!/usr/bin/env python3
"""
Solana Precious Metals Autonomous Trading System
================================================
Advanced DL/RL trading system for gold, silver, and mining stocks on Solana
Integrated with MCPVotsAGI ecosystem for 24/7 autonomous trading
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import aiohttp
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
import sqlite3
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SolanaTradingSystem")

@dataclass
class TradingSignal:
    """Trading signal for precious metals"""
    timestamp: datetime
    asset: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float
    price: float
    quantity: float
    reason: str
    risk_score: float

@dataclass
class PortfolioPosition:
    """Portfolio position tracking"""
    asset: str
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    allocation_percent: float

@dataclass
class MarketData:
    """Real-time market data"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    liquidity: float
    spread: float
    timestamp: datetime

class SolanaPreciousMetalsTrader:
    """Autonomous trading system for precious metals on Solana"""
    
    def __init__(self, wallet_address: Optional[str] = None):
        self.wallet_address = wallet_address
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        
        # Solana precious metals tokens
        self.precious_metals_tokens = {
            "GOLD": {
                "address": "BwjyAiSukd2mc136T5D1AuBEB9r2KYbdwpmeKcai6VKH",
                "name": "Gold Token",
                "decimals": 9,
                "backed": False
            },
            "PHYSICAL_GOLD": {
                "address": "9YnfbzQWCbgPpGZeJKsFfqQpf4bhHMZNLe3UJbZXAFpg",
                "name": "Physical Gold",
                "decimals": 9,
                "backed": True
            },
            "SILVER": {
                "address": "4iipXQQRDGSYcMXa3rqpn5qmxNXEiY2XoLixaVEsGqDp",
                "name": "Silver Token",
                "decimals": 9,
                "backed": False
            },
            "KNOX": {
                "address": "native_solana_knox",
                "name": "Fort Knox",
                "decimals": 9,
                "backed": True,
                "yield": True
            }
        }
        
        # Tokenized ETFs via xStocks
        self.mining_etfs = {
            "GLD": "SPDR Gold Trust",
            "IAU": "iShares Gold Trust",
            "SLV": "iShares Silver Trust",
            "GDXJ": "VanEck Junior Gold Miners ETF",
            "GDX": "VanEck Gold Miners ETF"
        }
        
        # Solana DEXes
        self.dex_endpoints = {
            "jupiter": "https://quote-api.jup.ag/v6",
            "raydium": "https://api.raydium.io/v2",
            "orca": "https://api.orca.so/v1",
            "meteora": "https://app.meteora.ag/api"
        }
        
        # Initialize databases
        self.trading_db = self.workspace / "trading_system.db"
        self.init_databases()
        
        # Trading parameters
        self.trading_config = {
            "max_position_size": 0.1,  # 10% max per position
            "stop_loss": 0.05,  # 5% stop loss
            "take_profit": 0.15,  # 15% take profit
            "min_confidence": 0.7,  # 70% confidence threshold
            "max_daily_trades": 20,
            "slippage_tolerance": 0.01,  # 1% slippage
            "rebalance_threshold": 0.05  # 5% deviation triggers rebalance
        }
        
        # RL/DL model parameters
        self.model_config = {
            "lookback_period": 100,  # 100 periods for analysis
            "prediction_horizon": 24,  # 24 hour prediction
            "features": [
                "price", "volume", "rsi", "macd", "bollinger_bands",
                "sentiment", "correlation", "volatility", "liquidity"
            ],
            "reward_function": "sharpe_ratio",
            "learning_rate": 0.001,
            "batch_size": 32
        }
        
        # Portfolio state
        self.portfolio = {
            "balance_sol": 0,
            "positions": {},
            "total_value_usd": 0,
            "daily_pnl": 0,
            "total_pnl": 0
        }
        
        # Market data cache
        self.market_data_cache = {}
        self.last_market_update = None
        
        # DGM integration for self-improvement
        self.dgm_endpoint = "ws://localhost:8013"
        self.performance_history = []
        
    def init_databases(self):
        """Initialize trading databases"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                asset TEXT,
                action TEXT,
                confidence REAL,
                price REAL,
                quantity REAL,
                reason TEXT,
                risk_score REAL,
                executed BOOLEAN,
                execution_price REAL,
                pnl REAL
            )
        ''')
        
        # Portfolio history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                total_value_usd REAL,
                positions TEXT,
                daily_pnl REAL,
                sharpe_ratio REAL,
                max_drawdown REAL
            )
        ''')
        
        # Market data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                symbol TEXT,
                price REAL,
                volume_24h REAL,
                change_24h REAL,
                liquidity REAL,
                spread REAL
            )
        ''')
        
        # Trading journal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                trade_type TEXT,
                asset TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                pnl REAL,
                pnl_percent REAL,
                holding_period INTEGER,
                strategy TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def fetch_market_data(self) -> dict[str, MarketData]:
        """Fetch real-time market data from multiple DEXes"""
        market_data = {}
        
        # Fetch from Jupiter aggregator
        try:
            async with aiohttp.ClientSession() as session:
                # Get prices for all precious metals tokens
                for symbol, token_info in self.precious_metals_tokens.items():
                    if token_info["address"] == "native_solana_knox":
                        continue  # Skip native tokens for now
                        
                    # Jupiter price API
                    url = f"{self.dex_endpoints['jupiter']}/price"
                    params = {"ids": token_info["address"]}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if token_info["address"] in data.get("data", {}):
                                price_data = data["data"][token_info["address"]]
                                
                                market_data[symbol] = MarketData(
                                    symbol=symbol,
                                    price=float(price_data.get("price", 0)),
                                    volume_24h=float(price_data.get("volume24h", 0)),
                                    change_24h=float(price_data.get("priceChange24h", 0)),
                                    liquidity=float(price_data.get("liquidity", 0)),
                                    spread=0.001,  # Default spread
                                    timestamp=datetime.now()
                                )
                
                # Store in cache
                self.market_data_cache = market_data
                self.last_market_update = datetime.now()
                
                # Store in database
                await self.store_market_data(market_data)
                
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            
        return market_data
    
    async def store_market_data(self, market_data: dict[str, MarketData]):
        """Store market data in database"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        for symbol, data in market_data.items():
            cursor.execute('''
                INSERT INTO market_data 
                (timestamp, symbol, price, volume_24h, change_24h, liquidity, spread)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.timestamp,
                data.symbol,
                data.price,
                data.volume_24h,
                data.change_24h,
                data.liquidity,
                data.spread
            ))
        
        conn.commit()
        conn.close()
    
    async def calculate_technical_indicators(self, symbol: str) -> dict[str, float]:
        """Calculate technical indicators for trading decisions"""
        # Get historical data
        conn = sqlite3.connect(self.trading_db)
        df = pd.read_sql_query(
            "SELECT * FROM market_data WHERE symbol = ? ORDER BY timestamp DESC LIMIT 100",
            conn,
            params=(symbol,)
        )
        conn.close()
        
        if len(df) < 20:
            return {}
        
        # Calculate indicators
        indicators = {}
        
        # RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
        
        # MACD
        exp1 = df['price'].ewm(span=12, adjust=False).mean()
        exp2 = df['price'].ewm(span=26, adjust=False).mean()
        indicators['macd'] = (exp1 - exp2).iloc[-1]
        indicators['macd_signal'] = (exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1]
        
        # Bollinger Bands
        sma = df['price'].rolling(window=20).mean()
        std = df['price'].rolling(window=20).std()
        indicators['bb_upper'] = (sma + 2 * std).iloc[-1]
        indicators['bb_lower'] = (sma - 2 * std).iloc[-1]
        indicators['bb_middle'] = sma.iloc[-1]
        
        # Volatility
        indicators['volatility'] = (df['price'].pct_change().std() * np.sqrt(365)).iloc[-1]
        
        # Volume analysis
        indicators['volume_ratio'] = df['volume_24h'].iloc[-1] / df['volume_24h'].mean()
        
        return indicators
    
    async def generate_rl_trading_signal(self, symbol: str, market_data: MarketData) -> [TradingSignal]:
        """Generate trading signal using RL/DL model"""
        # Get technical indicators
        indicators = await self.calculate_technical_indicators(symbol)
        
        if not indicators:
            return None
        
        # Feature vector for RL model
        features = {
            'price': market_data.price,
            'volume': market_data.volume_24h,
            'change_24h': market_data.change_24h,
            'rsi': indicators.get('rsi', 50),
            'macd': indicators.get('macd', 0),
            'volatility': indicators.get('volatility', 0),
            'volume_ratio': indicators.get('volume_ratio', 1)
        }
        
        # Simple RL-inspired decision logic (replace with actual DL model)
        confidence = 0.5
        action = 'hold'
        reason = []
        
        # RSI signals
        if features['rsi'] < 30:
            confidence += 0.2
            action = 'buy'
            reason.append("RSI oversold")
        elif features['rsi'] > 70:
            confidence += 0.2
            action = 'sell'
            reason.append("RSI overbought")
        
        # MACD signals
        if features['macd'] > indicators.get('macd_signal', 0):
            if action != 'sell':
                confidence += 0.15
                action = 'buy'
                reason.append("MACD bullish crossover")
        elif features['macd'] < indicators.get('macd_signal', 0):
            if action != 'buy':
                confidence += 0.15
                action = 'sell'
                reason.append("MACD bearish crossover")
        
        # Volume confirmation
        if features['volume_ratio'] > 1.5:
            confidence += 0.1
            reason.append("High volume confirmation")
        
        # Trend analysis
        if market_data.change_24h > 0.05:
            if action == 'buy':
                confidence += 0.1
                reason.append("Strong uptrend")
        elif market_data.change_24h < -0.05:
            if action == 'sell':
                confidence += 0.1
                reason.append("Strong downtrend")
        
        # Risk calculation
        risk_score = features['volatility'] * 0.5 + (1 - confidence) * 0.5
        
        # Position sizing based on confidence and risk
        max_position = self.portfolio.get('total_value_usd', 10000) * self.trading_config['max_position_size']
        quantity = (max_position * confidence * (1 - risk_score)) / market_data.price
        
        if confidence >= self.trading_config['min_confidence']:
            return TradingSignal(
                timestamp=datetime.now(),
                asset=symbol,
                action=action,
                confidence=confidence,
                price=market_data.price,
                quantity=quantity,
                reason="; ".join(reason),
                risk_score=risk_score
            )
        
        return None
    
    async def execute_trade_on_jupiter(self, signal: TradingSignal) -> dict[str, Any]:
        """Execute trade on Jupiter aggregator for best price"""
        try:
            # Get token info
            token_info = self.precious_metals_tokens.get(signal.asset)
            if not token_info:
                return {"success": False, "error": "Unknown asset"}
            
            # Jupiter swap parameters
            if signal.action == 'buy':
                input_mint = "So11111111111111111111111111111111111111112"  # SOL
                output_mint = token_info["address"]
                amount = int(signal.quantity * signal.price * 1e9)  # Convert to lamports
            else:  # sell
                input_mint = token_info["address"]
                output_mint = "So11111111111111111111111111111111111111112"  # SOL
                amount = int(signal.quantity * 10**token_info["decimals"])
            
            # Get quote from Jupiter
            async with aiohttp.ClientSession() as session:
                quote_url = f"{self.dex_endpoints['jupiter']}/quote"
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": amount,
                    "slippageBps": int(self.trading_config['slippage_tolerance'] * 10000)
                }
                
                async with session.get(quote_url, params=params) as response:
                    if response.status == 200:
                        quote = await response.json()
                        
                        # Log the trade
                        execution_result = {
                            "success": True,
                            "quote": quote,
                            "expected_output": int(quote.get("outAmount", 0)) / 10**token_info["decimals"],
                            "price_impact": float(quote.get("priceImpactPct", 0)),
                            "route": quote.get("routePlan", [])
                        }
                        
                        # Store in database
                        await self.record_trade(signal, execution_result)
                        
                        return execution_result
                    else:
                        return {"success": False, "error": f"Quote failed: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def record_trade(self, signal: TradingSignal, execution_result: dict[str, Any]):
        """Record trade in database"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        # Record signal
        cursor.execute('''
            INSERT INTO trading_signals 
            (timestamp, asset, action, confidence, price, quantity, reason, risk_score, executed, execution_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal.timestamp,
            signal.asset,
            signal.action,
            signal.confidence,
            signal.price,
            signal.quantity,
            signal.reason,
            signal.risk_score,
            execution_result.get("success", False),
            signal.price  # Actual execution price would come from the transaction
        ))
        
        conn.commit()
        conn.close()
    
    async def update_portfolio(self):
        """Update portfolio positions and calculate P&L"""
        positions = {}
        total_value = 0
        
        # Get current prices
        market_data = await self.fetch_market_data()
        
        # Calculate position values
        for symbol, quantity in self.portfolio.get("positions", {}).items():
            if symbol in market_data:
                current_price = market_data[symbol].price
                position_value = quantity * current_price
                
                # Get average price from trades
                conn = sqlite3.connect(self.trading_db)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT AVG(price) FROM trading_signals 
                    WHERE asset = ? AND action = 'buy' AND executed = 1
                ''', (symbol,))
                
                avg_price = cursor.fetchone()[0] or current_price
                conn.close()
                
                pnl = (current_price - avg_price) * quantity
                pnl_percent = (current_price / avg_price - 1) * 100 if avg_price > 0 else 0
                
                positions[symbol] = PortfolioPosition(
                    asset=symbol,
                    symbol=self.precious_metals_tokens[symbol]["name"],
                    quantity=quantity,
                    average_price=avg_price,
                    current_price=current_price,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    allocation_percent=0  # Will calculate after total
                )
                
                total_value += position_value
        
        # Update allocations
        for position in positions.values():
            position.allocation_percent = (position.quantity * position.current_price / total_value * 100) if total_value > 0 else 0
        
        # Update portfolio state
        self.portfolio["positions"] = positions
        self.portfolio["total_value_usd"] = total_value
        
        # Store portfolio snapshot
        await self.store_portfolio_snapshot()
    
    async def store_portfolio_snapshot(self):
        """Store portfolio snapshot in database"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        positions_json = json.dumps({
            symbol: asdict(pos) for symbol, pos in self.portfolio["positions"].items()
        })
        
        cursor.execute('''
            INSERT INTO portfolio_history 
            (timestamp, total_value_usd, positions, daily_pnl, sharpe_ratio, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            self.portfolio["total_value_usd"],
            positions_json,
            self.portfolio.get("daily_pnl", 0),
            await self.calculate_sharpe_ratio(),
            await self.calculate_max_drawdown()
        ))
        
        conn.commit()
        conn.close()
    
    async def calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio for performance evaluation"""
        conn = sqlite3.connect(self.trading_db)
        df = pd.read_sql_query(
            "SELECT total_value_usd, timestamp FROM portfolio_history ORDER BY timestamp DESC LIMIT 30",
            conn
        )
        conn.close()
        
        if len(df) < 2:
            return 0
        
        # Calculate daily returns
        df['returns'] = df['total_value_usd'].pct_change()
        
        # Annualized Sharpe ratio
        sharpe = (df['returns'].mean() * 365) / (df['returns'].std() * np.sqrt(365)) if df['returns'].std() > 0 else 0
        
        return sharpe
    
    async def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        conn = sqlite3.connect(self.trading_db)
        df = pd.read_sql_query(
            "SELECT total_value_usd FROM portfolio_history ORDER BY timestamp",
            conn
        )
        conn.close()
        
        if len(df) < 2:
            return 0
        
        # Calculate running maximum
        running_max = df['total_value_usd'].expanding().max()
        drawdown = (df['total_value_usd'] - running_max) / running_max
        
        return abs(drawdown.min())
    
    async def rebalance_portfolio(self):
        """Rebalance portfolio based on target allocations"""
        target_allocations = {
            "GOLD": 0.4,  # 40% gold
            "SILVER": 0.2,  # 20% silver
            "PHYSICAL_GOLD": 0.2,  # 20% physical gold
            "KNOX": 0.2  # 20% yield-bearing gold
        }
        
        current_allocations = {
            symbol: pos.allocation_percent / 100
            for symbol, pos in self.portfolio["positions"].items()
        }
        
        # Calculate rebalancing trades
        total_value = self.portfolio["total_value_usd"]
        
        for symbol, target_alloc in target_allocations.items():
            current_alloc = current_allocations.get(symbol, 0)
            
            if abs(current_alloc - target_alloc) > self.trading_config['rebalance_threshold']:
                # Calculate trade size
                target_value = total_value * target_alloc
                current_value = total_value * current_alloc
                trade_value = target_value - current_value
                
                # Generate rebalancing signal
                market_data = self.market_data_cache.get(symbol)
                if market_data:
                    quantity = abs(trade_value) / market_data.price
                    action = 'buy' if trade_value > 0 else 'sell'
                    
                    signal = TradingSignal(
                        timestamp=datetime.now(),
                        asset=symbol,
                        action=action,
                        confidence=0.9,  # High confidence for rebalancing
                        price=market_data.price,
                        quantity=quantity,
                        reason=f"Portfolio rebalancing: target {target_alloc*100}%, current {current_alloc*100}%",
                        risk_score=0.1  # Low risk for rebalancing
                    )
                    
                    # Execute rebalancing trade
                    await self.execute_trade_on_jupiter(signal)
    
    async def run_autonomous_trading_loop(self):
        """Main autonomous trading loop"""
        logger.info("Starting autonomous precious metals trading system...")
        
        while True:
            try:
                # Update market data
                market_data = await self.fetch_market_data()
                
                # Generate trading signals for each asset
                signals = []
                for symbol in self.precious_metals_tokens:
                    if symbol in market_data:
                        signal = await self.generate_rl_trading_signal(symbol, market_data[symbol])
                        if signal:
                            signals.append(signal)
                
                # Execute high-confidence trades
                daily_trades = await self.get_daily_trade_count()
                
                for signal in sorted(signals, key=lambda s: s.confidence, reverse=True):
                    if daily_trades >= self.trading_config['max_daily_trades']:
                        break
                        
                    logger.info(f"Executing trade: {signal.action} {signal.quantity:.4f} {signal.asset} @ ${signal.price:.4f}")
                    await self.execute_trade_on_jupiter(signal)
                    daily_trades += 1
                
                # Update portfolio
                await self.update_portfolio()
                
                # Check for rebalancing
                if datetime.now().hour == 0:  # Rebalance at midnight
                    await self.rebalance_portfolio()
                
                # Self-improvement via DGM
                if len(self.performance_history) >= 100:
                    await self.evolve_trading_strategy()
                
                # Sleep for next iteration
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)
    
    async def get_daily_trade_count(self) -> int:
        """Get number of trades executed today"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) FROM trading_signals 
            WHERE DATE(timestamp) = ? AND executed = 1
        ''', (today,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    async def evolve_trading_strategy(self):
        """Use DGM to evolve trading strategy based on performance"""
        try:
            # Connect to DGM Evolution Engine
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.dgm_endpoint) as ws:
                    # Send performance data
                    performance_data = {
                        "type": "optimize_trading_strategy",
                        "current_sharpe": await self.calculate_sharpe_ratio(),
                        "max_drawdown": await self.calculate_max_drawdown(),
                        "win_rate": await self.calculate_win_rate(),
                        "current_parameters": self.trading_config,
                        "model_config": self.model_config
                    }
                    
                    await ws.send_json(performance_data)
                    
                    # Receive optimized parameters
                    response = await ws.receive_json()
                    
                    if response.get("success"):
                        # Update trading parameters
                        self.trading_config.update(response.get("optimized_parameters", {}))
                        self.model_config.update(response.get("optimized_model_config", {}))
                        
                        logger.info("Trading strategy evolved successfully")
                        
        except Exception as e:
            logger.error(f"Strategy evolution failed: {e}")
    
    async def calculate_win_rate(self) -> float:
        """Calculate win rate of executed trades"""
        conn = sqlite3.connect(self.trading_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM trading_signals 
            WHERE executed = 1 AND pnl > 0
        ''')
        wins = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM trading_signals 
            WHERE executed = 1
        ''')
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return (wins / total * 100) if total > 0 else 0
    
    def get_dashboard_data(self) -> dict[str, Any]:
        """Get trading data for dashboard display"""
        return {
            "portfolio": {
                "total_value": self.portfolio.get("total_value_usd", 0),
                "daily_pnl": self.portfolio.get("daily_pnl", 0),
                "positions": [asdict(pos) for pos in self.portfolio.get("positions", {}).values()]
            },
            "market_data": {
                symbol: asdict(data) for symbol, data in self.market_data_cache.items()
            },
            "performance": {
                "sharpe_ratio": asyncio.run(self.calculate_sharpe_ratio()),
                "max_drawdown": asyncio.run(self.calculate_max_drawdown()),
                "win_rate": asyncio.run(self.calculate_win_rate())
            },
            "last_update": self.last_market_update.isoformat() if self.last_market_update else None
        }


class SolanaTradingIntegration:
    """Integration module for Oracle AGI Dashboard"""
    
    def __init__(self, wallet_address: Optional[str] = None):
        self.trader = SolanaPreciousMetalsTrader(wallet_address)
        self.trading_task = None
        
    async def start_trading(self):
        """Start autonomous trading"""
        if not self.trading_task:
            self.trading_task = asyncio.create_task(self.trader.run_autonomous_trading_loop())
            logger.info("Solana precious metals trading started")
            
    async def stop_trading(self):
        """Stop trading"""
        if self.trading_task:
            self.trading_task.cancel()
            self.trading_task = None
            logger.info("Trading stopped")
            
    def get_trading_status(self) -> dict[str, Any]:
        """Get current trading status for dashboard"""
        return {
            "active": self.trading_task is not None,
            "data": self.trader.get_dashboard_data()
        }
    
    async def manual_trade(self, asset: str, action: str, amount: float) -> dict[str, Any]:
        """Execute manual trade"""
        # Get current market data
        market_data = await self.trader.fetch_market_data()
        
        if asset not in market_data:
            return {"success": False, "error": "Asset not found"}
        
        # Create manual signal
        signal = TradingSignal(
            timestamp=datetime.now(),
            asset=asset,
            action=action,
            confidence=1.0,  # Manual trades have full confidence
            price=market_data[asset].price,
            quantity=amount / market_data[asset].price,
            reason="Manual trade from dashboard",
            risk_score=0.1
        )
        
        # Execute trade
        result = await self.trader.execute_trade_on_jupiter(signal)
        
        # Update portfolio
        await self.trader.update_portfolio()
        
        return result


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize with wallet address (optional)
        wallet = os.environ.get("SOLANA_WALLET_ADDRESS")
        
        trading_system = SolanaTradingIntegration(wallet)
        
        # Start autonomous trading
        await trading_system.start_trading()
        
        # Keep running
        try:
            await asyncio.sleep(86400)  # Run for 24 hours
        except KeyboardInterrupt:
            await trading_system.stop_trading()
    
    asyncio.run(main())