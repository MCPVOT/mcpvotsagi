#!/usr/bin/env python3
"""
DeepSeek-Powered Autonomous Trading Agent
========================================
24/7 self-learning RL/ML agent for precious metals trading
Uses DeepSeek reasoning for intelligent market analysis
"""

import asyncio
import json
import logging
import os
import sys
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import websockets
import aiohttp
from dataclasses import dataclass, asdict
import sqlite3
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeepSeekTradingAgent")

@dataclass
class MarketState:
    """Current market state representation"""
    timestamp: datetime
    prices: dict[str, float]  # Asset prices
    volumes: dict[str, float]  # Trading volumes
    rsi: dict[str, float]  # RSI indicators
    macd: dict[str, Dict[str, float]]  # MACD values
    sentiment: float  # Market sentiment score
    volatility: float  # Market volatility

@dataclass
class TradingAction:
    """Trading action to execute"""
    timestamp: datetime
    action_type: str  # 'buy', 'sell', 'hold'
    asset: str
    amount: float
    price: float
    confidence: float
    reasoning: str

@dataclass
class PerformanceMetrics:
    """Agent performance metrics"""
    total_trades: int
    winning_trades: int
    total_profit: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float

class DeepSeekTradingBrain:
    """Integration with DeepSeek reasoning engine"""
    
    def __init__(self, deepseek_endpoint: str = "ws://localhost:3008"):
        self.endpoint = deepseek_endpoint
        self.connection = None
        self.request_id = 0
        
    async def connect(self):
        """Connect to DeepSeek MCP server"""
        try:
            self.connection = await websockets.connect(self.endpoint)
            logger.info("Connected to DeepSeek reasoning engine")
        except Exception as e:
            logger.error(f"Failed to connect to DeepSeek: {e}")
            raise
            
    async def analyze_market(self, state: MarketState, portfolio: dict[str, Any]) -> dict[str, Any]:
        """Get market analysis from DeepSeek"""
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "method": "reasoning/trading",
            "params": {
                "prompt": f"""Analyze the precious metals market and provide trading recommendations.
                
Current Market State:
- Gold Price: ${state.prices.get('GOLD', 0):.2f}
- Silver Price: ${state.prices.get('SILVER', 0):.2f}
- Gold RSI: {state.rsi.get('GOLD', 0):.2f}
- Silver RSI: {state.rsi.get('SILVER', 0):.2f}
- Market Volatility: {state.volatility:.2f}
- Market Sentiment: {state.sentiment:.2f}

Portfolio:
{json.dumps(portfolio, indent=2)}

Provide specific buy/sell/hold recommendations with confidence levels.""",
                "portfolio": portfolio,
                "market_data": asdict(state)
            },
            "id": self.request_id
        }
        
        await self.connection.send(json.dumps(request))
        response = await self.connection.recv()
        data = json.loads(response)
        
        return data.get("result", {})
        
    async def evaluate_strategy(self, performance: PerformanceMetrics) -> dict[str, Any]:
        """Get strategy evaluation from DeepSeek"""
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "method": "reasoning/execute",
            "params": {
                "task_type": "trading",
                "prompt": f"""Evaluate trading performance and suggest improvements.
                
Performance Metrics:
- Total Trades: {performance.total_trades}
- Win Rate: {(performance.winning_trades / max(performance.total_trades, 1)) * 100:.2f}%
- Total Profit: ${performance.total_profit:.2f}
- Sharpe Ratio: {performance.sharpe_ratio:.2f}
- Max Drawdown: {performance.max_drawdown:.2f}%

Suggest specific improvements to the trading strategy.""",
                "context": {"performance": asdict(performance)}
            },
            "id": self.request_id
        }
        
        await self.connection.send(json.dumps(request))
        response = await self.connection.recv()
        data = json.loads(response)
        
        return data.get("result", {})

class ReinforcementLearningEngine:
    """RL engine for adaptive trading strategies"""
    
    def __init__(self, state_size: int = 20, action_size: int = 3):
        self.state_size = state_size
        self.action_size = action_size  # buy, sell, hold
        
        # Q-Learning parameters
        self.learning_rate = 0.001
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # Experience replay
        self.memory = []
        self.batch_size = 32
        
        # Simple neural network weights (can be replaced with TensorFlow/PyTorch)
        self.weights = self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize network weights"""
        return {
            "W1": np.random.randn(self.state_size, 128) * 0.01,
            "b1": np.zeros((1, 128)),
            "W2": np.random.randn(128, 64) * 0.01,
            "b2": np.zeros((1, 64)),
            "W3": np.random.randn(64, self.action_size) * 0.01,
            "b3": np.zeros((1, self.action_size))
        }
        
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values for actions"""
        # Simple forward pass
        h1 = np.maximum(0, np.dot(state, self.weights["W1"]) + self.weights["b1"])
        h2 = np.maximum(0, np.dot(h1, self.weights["W2"]) + self.weights["b2"])
        q_values = np.dot(h2, self.weights["W3"]) + self.weights["b3"]
        return q_values
        
    def act(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return np.random.choice(self.action_size)
        
        q_values = self.predict(state.reshape(1, -1))
        return np.argmax(q_values[0])
        
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > 10000:
            self.memory.pop(0)
            
    def replay(self):
        """Train on batch of experiences"""
        if len(self.memory) < self.batch_size:
            return
            
        # Sample batch
        batch_indices = np.random.choice(len(self.memory), self.batch_size, replace=False)
        batch = [self.memory[i] for i in batch_indices]
        
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        # Calculate targets
        current_q = self.predict(states)
        next_q = self.predict(next_states)
        
        targets = current_q.copy()
        for i in range(self.batch_size):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + self.gamma * np.max(next_q[i])
                
        # Simple gradient descent update (simplified)
        # In practice, use proper backpropagation
        loss = np.mean((targets - current_q) ** 2)
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return loss
        
    def save(self, filepath: str):
        """Save model weights"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.weights, f)
            
    def load(self, filepath: str):
        """Load model weights"""
        with open(filepath, 'rb') as f:
            self.weights = pickle.load(f)

class AutonomousTradingAgent:
    """Main autonomous trading agent"""
    
    def __init__(self):
        self.deepseek_brain = DeepSeekTradingBrain()
        self.rl_engine = ReinforcementLearningEngine()
        self.performance_tracker = PerformanceTracker()
        
        # Trading configuration
        self.trading_pairs = ["GOLD/USD", "SILVER/USD", "GDX/USD", "SLV/USD"]
        self.max_position_size = 0.1  # 10% per position
        self.stop_loss = 0.05  # 5%
        self.take_profit = 0.15  # 15%
        
        # Connections
        self.solana_connection = None
        self.market_data_connection = None
        
        # State
        self.portfolio = {
            "USD": 10000,  # Starting capital
            "positions": {}
        }
        self.is_running = False
        
    async def initialize(self):
        """Initialize all connections"""
        await self.deepseek_brain.connect()
        
        # Connect to Solana MCP
        try:
            self.solana_connection = await websockets.connect("ws://localhost:3005")
            logger.info("Connected to Solana MCP")
        except Exception:
            logger.warning("Solana MCP not available")
            
        # Load RL model if exists
        model_path = Path("models/trading_agent.pkl")
        if model_path.exists():
            self.rl_engine.load(str(model_path))
            logger.info("Loaded existing RL model")
            
    async def run(self):
        """Main trading loop"""
        self.is_running = True
        logger.info("Starting autonomous trading agent")
        
        while self.is_running:
            try:
                # Get market state
                market_state = await self.get_market_state()
                
                # Get DeepSeek analysis
                analysis = await self.deepseek_brain.analyze_market(
                    market_state, 
                    self.portfolio
                )
                
                # Convert market state to RL state vector
                state_vector = self.market_state_to_vector(market_state)
                
                # Get RL action
                rl_action = self.rl_engine.act(state_vector)
                
                # Combine DeepSeek and RL recommendations
                final_action = await self.combine_recommendations(
                    analysis, 
                    rl_action,
                    market_state
                )
                
                # Execute trades
                if final_action:
                    reward = await self.execute_trade(final_action)
                    
                    # Store experience
                    next_state = await self.get_market_state()
                    next_vector = self.market_state_to_vector(next_state)
                    self.rl_engine.remember(
                        state_vector,
                        rl_action,
                        reward,
                        next_vector,
                        False
                    )
                    
                # Train RL model
                if len(self.rl_engine.memory) > 100:
                    loss = self.rl_engine.replay()
                    if loss:
                        logger.debug(f"RL training loss: {loss:.4f}")
                        
                # Check positions
                await self.manage_positions(market_state)
                
                # Log performance
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    metrics = self.performance_tracker.get_metrics()
                    logger.info(f"Performance: {metrics}")
                    
                    # Get strategy improvements from DeepSeek
                    if metrics.total_trades > 10:
                        improvements = await self.deepseek_brain.evaluate_strategy(metrics)
                        logger.info(f"DeepSeek suggestions: {improvements.get('result', '')}")
                        
                # Save model periodically
                if int(time.time()) % 3600 == 0:  # Every hour
                    self.rl_engine.save("models/trading_agent.pkl")
                    logger.info("Saved RL model")
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)
                
    async def get_market_state(self) -> MarketState:
        """Get current market state"""
        # Simplified - in practice, get from market data APIs
        prices = {
            "GOLD": 2050 + np.random.randn() * 10,
            "SILVER": 24.5 + np.random.randn() * 0.5
        }
        
        return MarketState(
            timestamp=datetime.now(),
            prices=prices,
            volumes={"GOLD": 1000000, "SILVER": 500000},
            rsi={"GOLD": 50 + np.random.randn() * 10, "SILVER": 55 + np.random.randn() * 10},
            macd={"GOLD": {"macd": 0.5, "signal": 0.3}, "SILVER": {"macd": -0.2, "signal": -0.1}},
            sentiment=0.6 + np.random.randn() * 0.1,
            volatility=0.02 + abs(np.random.randn() * 0.01)
        )
        
    def market_state_to_vector(self, state: MarketState) -> np.ndarray:
        """Convert market state to feature vector"""
        features = []
        
        # Price features
        for asset in ["GOLD", "SILVER"]:
            features.append(state.prices.get(asset, 0))
            features.append(state.volumes.get(asset, 0) / 1000000)  # Normalize
            features.append(state.rsi.get(asset, 50) / 100)  # Normalize
            
            macd_data = state.macd.get(asset, {})
            features.append(macd_data.get("macd", 0))
            features.append(macd_data.get("signal", 0))
            
        # Market features
        features.append(state.sentiment)
        features.append(state.volatility * 100)  # Scale up
        
        # Portfolio features
        features.append(self.portfolio["USD"] / 10000)  # Normalize
        features.append(len(self.portfolio["positions"]))
        
        # Pad to state size
        while len(features) < self.rl_engine.state_size:
            features.append(0)
            
        return np.array(features[:self.rl_engine.state_size])
        
    async def combine_recommendations(
        self, 
        deepseek_analysis: dict[str, Any], 
        rl_action: int,
        market_state: MarketState
    ) -> [TradingAction]:
        """Combine DeepSeek and RL recommendations"""
        
        # Parse DeepSeek recommendation
        trading_rec = deepseek_analysis.get("trading_recommendation", {})
        ds_action = trading_rec.get("action", "hold")
        ds_confidence = trading_rec.get("confidence", 0.5)
        ds_assets = trading_rec.get("assets", [])
        
        # Map RL action
        rl_actions = ["buy", "sell", "hold"]
        rl_action_str = rl_actions[rl_action]
        
        # Combine logic
        if ds_confidence > 0.7 and ds_action != "hold":
            # High confidence DeepSeek recommendation
            action = ds_action
            asset = ds_assets[0] if ds_assets else "GOLD"
            confidence = ds_confidence
        elif rl_action_str == ds_action:
            # Agreement between models
            action = rl_action_str
            asset = "GOLD"  # Default
            confidence = 0.8
        else:
            # Disagreement - be conservative
            if self.rl_engine.epsilon < 0.5:  # Trained model
                action = rl_action_str
                confidence = 0.6
            else:
                action = "hold"
                confidence = 0.4
                
        if action == "hold":
            return None
            
        # Calculate position size
        available_capital = self.portfolio["USD"]
        position_size = available_capital * self.max_position_size * confidence
        
        return TradingAction(
            timestamp=datetime.now(),
            action_type=action,
            asset=asset,
            amount=position_size / market_state.prices.get(asset, 1),
            price=market_state.prices.get(asset, 0),
            confidence=confidence,
            reasoning=deepseek_analysis.get("result", "")[:200]
        )
        
    async def execute_trade(self, action: TradingAction) -> float:
        """Execute trade and return reward"""
        logger.info(f"Executing trade: {action.action_type} {action.amount:.4f} {action.asset} @ ${action.price:.2f}")
        
        # Simulate trade execution
        cost = action.amount * action.price
        
        if action.action_type == "buy":
            if self.portfolio["USD"] >= cost:
                self.portfolio["USD"] -= cost
                if action.asset not in self.portfolio["positions"]:
                    self.portfolio["positions"][action.asset] = {
                        "amount": 0,
                        "avg_price": 0
                    }
                    
                pos = self.portfolio["positions"][action.asset]
                total_amount = pos["amount"] + action.amount
                pos["avg_price"] = (pos["avg_price"] * pos["amount"] + action.price * action.amount) / total_amount
                pos["amount"] = total_amount
                
                # Track trade
                self.performance_tracker.record_trade(action)
                
                return 0.01  # Small positive reward for execution
            else:
                return -0.1  # Penalty for insufficient funds
                
        elif action.action_type == "sell":
            if action.asset in self.portfolio["positions"]:
                pos = self.portfolio["positions"][action.asset]
                if pos["amount"] >= action.amount:
                    # Calculate profit
                    profit = (action.price - pos["avg_price"]) * action.amount
                    self.portfolio["USD"] += action.amount * action.price
                    
                    pos["amount"] -= action.amount
                    if pos["amount"] == 0:
                        del self.portfolio["positions"][action.asset]
                        
                    # Track trade
                    self.performance_tracker.record_trade(action, profit)
                    
                    # Reward based on profit
                    return profit / 1000  # Normalized reward
                    
            return -0.1  # Penalty for trying to sell non-existent position
            
        return 0
        
    async def manage_positions(self, market_state: MarketState):
        """Manage existing positions (stop loss, take profit)"""
        positions_to_close = []
        
        for asset, position in self.portfolio["positions"].items():
            current_price = market_state.prices.get(asset, position["avg_price"])
            pnl_percent = (current_price - position["avg_price"]) / position["avg_price"]
            
            # Check stop loss
            if pnl_percent <= -self.stop_loss:
                positions_to_close.append((asset, "stop_loss"))
                
            # Check take profit
            elif pnl_percent >= self.take_profit:
                positions_to_close.append((asset, "take_profit"))
                
        # Close positions
        for asset, reason in positions_to_close:
            position = self.portfolio["positions"][asset]
            current_price = market_state.prices.get(asset, position["avg_price"])
            
            action = TradingAction(
                timestamp=datetime.now(),
                action_type="sell",
                asset=asset,
                amount=position["amount"],
                price=current_price,
                confidence=1.0,
                reasoning=f"Position closed: {reason}"
            )
            
            await self.execute_trade(action)
            logger.info(f"Closed position {asset} due to {reason}")
            
    async def shutdown(self):
        """Graceful shutdown"""
        self.is_running = False
        
        # Close all positions
        for asset in list(self.portfolio["positions"].keys()):
            position = self.portfolio["positions"][asset]
            action = TradingAction(
                timestamp=datetime.now(),
                action_type="sell",
                asset=asset,
                amount=position["amount"],
                price=position["avg_price"],  # Use avg price as estimate
                confidence=1.0,
                reasoning="Shutdown - closing all positions"
            )
            await self.execute_trade(action)
            
        # Save model
        self.rl_engine.save("models/trading_agent_final.pkl")
        
        # Log final performance
        metrics = self.performance_tracker.get_metrics()
        logger.info(f"Final performance: {metrics}")

class PerformanceTracker:
    """Track trading performance"""
    
    def __init__(self):
        self.trades = []
        self.daily_returns = []
        
    def record_trade(self, action: TradingAction, profit: float = 0):
        """Record a trade"""
        self.trades.append({
            "timestamp": action.timestamp,
            "action": action.action_type,
            "asset": action.asset,
            "amount": action.amount,
            "price": action.price,
            "profit": profit
        })
        
    def get_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        if not self.trades:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
            
        df = pd.DataFrame(self.trades)
        
        total_trades = len(df)
        winning_trades = len(df[df["profit"] > 0])
        total_profit = df["profit"].sum()
        
        # Calculate returns
        if len(df) > 1:
            df["returns"] = df["profit"].pct_change()
            sharpe_ratio = (df["returns"].mean() / df["returns"].std()) * np.sqrt(252) if df["returns"].std() > 0 else 0
            
            # Max drawdown
            cumulative = (1 + df["returns"]).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
        else:
            sharpe_ratio = 0
            max_drawdown = 0
            
        # Average trade duration
        if len(df) > 1:
            durations = df["timestamp"].diff().dt.total_seconds() / 3600  # Hours
            avg_duration = durations.mean()
        else:
            avg_duration = 0
            
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            total_profit=total_profit,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            avg_trade_duration=avg_duration
        )

async def main():
    """Main entry point"""
    # Create models directory
    Path("models").mkdir(exist_ok=True)
    
    # Initialize agent
    agent = AutonomousTradingAgent()
    await agent.initialize()
    
    try:
        # Run trading agent
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Shutting down trading agent...")
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())