#!/usr/bin/env python3
"""
Enhanced 24/7 RL Trading System with Ollama Integration
=======================================================
Advanced reinforcement learning trading system with continuous operation
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple
import aiohttp
import requests
from dataclasses import dataclass, asdict
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EnhancedRLTrading")

@dataclass
class TradingState:
    """Trading state representation"""
    price: float
    volume: float
    volatility: float
    rsi: float
    macd: float
    bollinger_position: float
    portfolio_value: float
    position_size: float
    time_features: list[float]

    def to_tensor(self) -> torch.Tensor:
        """Convert to PyTorch tensor"""
        features = [
            self.price, self.volume, self.volatility, self.rsi,
            self.macd, self.bollinger_position, self.portfolio_value,
            self.position_size
        ] + self.time_features
        return torch.FloatTensor(features)

@dataclass
class TradingAction:
    """Trading action representation"""
    action_type: str  # 'buy', 'sell', 'hold'
    quantity: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class DQNNetwork(nn.Module):
    """Deep Q-Network for trading decisions"""

    def __init__(self, state_size: int, action_size: int, hidden_size: int = 256):
        super(DQNNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size)
        )

    def forward(self, x):
        return self.network(x)

class OllamaLLMEnhancer:
    """Ollama LLM integration for trading enhancement"""

    def __init__(self, model_name: str = "qwen2.5-coder:latest"):
        self.base_url = "http://localhost:11434"
        self.model_name = model_name

    async def analyze_market_conditions(self, market_data: dict[str, Any]) -> dict[str, Any]:
        """Use Ollama to analyze market conditions"""
        prompt = f"""
        Analyze the following market data and provide trading insights:

        Price: ${market_data.get('price', 0):.2f}
        Volume: {market_data.get('volume', 0):.2f}
        RSI: {market_data.get('rsi', 0):.2f}
        MACD: {market_data.get('macd', 0):.4f}
        Volatility: {market_data.get('volatility', 0):.4f}

        Provide:
        1. Market sentiment (bullish/bearish/neutral)
        2. Risk level (low/medium/high)
        3. Recommended action (buy/sell/hold)
        4. Confidence level (0-100)
        5. Key factors influencing decision

        Respond in JSON format.
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        try:
                            analysis = json.loads(result.get("response", "{}"))
                            return analysis
                        except json.JSONDecodeError:
                            return {"error": "Invalid JSON response"}
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Ollama analysis error: {e}")
            return {"error": str(e)}

class Enhanced24x7RLTradingSystem:
    """Enhanced 24/7 RL Trading System"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.data_path = self.base_path / "data" / "rl_models"
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Trading parameters
        self.state_size = 15  # Increased state size
        self.action_size = 5  # buy_small, buy_large, sell_small, sell_large, hold
        self.learning_rate = 0.001
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.memory_size = 10000

        # Initialize components
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = DQNNetwork(self.state_size, self.action_size).to(self.device)
        self.target_network = DQNNetwork(self.state_size, self.action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        self.memory = deque(maxlen=self.memory_size)

        # Ollama integration
        self.llm_enhancer = OllamaLLMEnhancer()

        # Trading state
        self.portfolio_value = 10000.0  # Starting portfolio
        self.position_size = 0.0
        self.current_price = 0.0
        self.running = False

        # Performance tracking
        self.performance_history = []
        self.trade_history = []

    async def start_24x7_operation(self):
        """Start 24/7 trading operation"""
        logger.info("🚀 Starting 24/7 RL Trading System...")
        self.running = True

        # Load existing model if available
        await self.load_model()

        # Start parallel tasks
        tasks = [
            asyncio.create_task(self.market_data_loop()),
            asyncio.create_task(self.trading_decision_loop()),
            asyncio.create_task(self.model_training_loop()),
            asyncio.create_task(self.performance_monitoring_loop()),
            asyncio.create_task(self.model_persistence_loop())
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping 24/7 trading system...")
            self.running = False
            await self.save_model()

    async def market_data_loop(self):
        """Continuous market data collection"""
        while self.running:
            try:
                # Simulate market data collection
                market_data = await self.fetch_market_data()

                # Process market data
                state = await self.process_market_data(market_data)

                # Store for decision making
                self.current_state = state
                self.current_price = market_data.get("price", self.current_price)

                await asyncio.sleep(1)  # 1-second intervals

            except Exception as e:
                logger.error(f"Market data error: {e}")
                await asyncio.sleep(5)

    async def trading_decision_loop(self):
        """Continuous trading decision making"""
        while self.running:
            try:
                if hasattr(self, 'current_state'):
                    # Get RL action
                    rl_action = await self.get_rl_action(self.current_state)

                    # Get LLM enhancement
                    llm_analysis = await self.llm_enhancer.analyze_market_conditions({
                        "price": self.current_price,
                        "portfolio_value": self.portfolio_value,
                        "position_size": self.position_size
                    })

                    # Combine RL and LLM decisions
                    final_action = await self.combine_decisions(rl_action, llm_analysis)

                    # Execute trade
                    await self.execute_trade(final_action)

                await asyncio.sleep(5)  # 5-second trading decisions

            except Exception as e:
                logger.error(f"Trading decision error: {e}")
                await asyncio.sleep(10)

    async def model_training_loop(self):
        """Continuous model training"""
        while self.running:
            try:
                if len(self.memory) >= self.batch_size:
                    await self.train_model()

                await asyncio.sleep(30)  # Train every 30 seconds

            except Exception as e:
                logger.error(f"Training error: {e}")
                await asyncio.sleep(60)

    async def performance_monitoring_loop(self):
        """Continuous performance monitoring"""
        while self.running:
            try:
                performance = {
                    "timestamp": datetime.now().isoformat(),
                    "portfolio_value": self.portfolio_value,
                    "position_size": self.position_size,
                    "current_price": self.current_price,
                    "epsilon": self.epsilon,
                    "memory_size": len(self.memory)
                }

                self.performance_history.append(performance)

                # Keep only last 1000 records
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]

                # Log performance every hour
                if len(self.performance_history) % 720 == 0:  # 720 * 5 seconds = 1 hour
                    logger.info(f"📊 Portfolio: ${self.portfolio_value:.2f}, Position: {self.position_size:.4f}")

                await asyncio.sleep(5)  # Monitor every 5 seconds

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)

    async def model_persistence_loop(self):
        """Periodic model saving"""
        while self.running:
            try:
                await self.save_model()
                await asyncio.sleep(3600)  # Save every hour

            except Exception as e:
                logger.error(f"Model persistence error: {e}")
                await asyncio.sleep(300)

    async def fetch_market_data(self) -> dict[str, Any]:
        """Fetch real-time market data"""
        # Simulate market data - replace with real Jupiter API calls
        import random
        import math

        now = datetime.now()
        base_price = 245.0  # SOL base price
        volatility = 0.02

        # Simulate price movement
        price_change = random.gauss(0, volatility)
        price = max(base_price * (1 + price_change), 1.0)

        # Generate technical indicators
        rsi = random.uniform(20, 80)
        macd = random.gauss(0, 0.1)
        volume = random.uniform(1000, 10000)

        return {
            "price": price,
            "volume": volume,
            "rsi": rsi,
            "macd": macd,
            "volatility": volatility,
            "timestamp": now.isoformat()
        }

    async def process_market_data(self, market_data: dict[str, Any]) -> TradingState:
        """Process market data into trading state"""
        now = datetime.now()

        # Time features
        time_features = [
            now.hour / 24.0,
            now.weekday() / 7.0,
            now.day / 31.0,
            math.sin(2 * math.pi * now.hour / 24),  # Cyclical hour
            math.cos(2 * math.pi * now.hour / 24)
        ]

        state = TradingState(
            price=market_data["price"],
            volume=market_data["volume"],
            volatility=market_data["volatility"],
            rsi=market_data["rsi"],
            macd=market_data["macd"],
            bollinger_position=0.5,  # Placeholder
            portfolio_value=self.portfolio_value,
            position_size=self.position_size,
            time_features=time_features
        )

        return state

    async def get_rl_action(self, state: TradingState) -> int:
        """Get action from RL model"""
        if random.random() <= self.epsilon:
            return random.randrange(self.action_size)

        state_tensor = state.to_tensor().unsqueeze(0).to(self.device)
        q_values = self.q_network(state_tensor)
        return q_values.argmax().item()

    async def combine_decisions(self, rl_action: int, llm_analysis: dict[str, Any]) -> TradingAction:
        """Combine RL and LLM decisions"""
        action_map = {
            0: "buy_small",
            1: "buy_large",
            2: "sell_small",
            3: "sell_large",
            4: "hold"
        }

        rl_action_type = action_map.get(rl_action, "hold")
        llm_recommendation = llm_analysis.get("recommended_action", "hold")
        llm_confidence = llm_analysis.get("confidence_level", 50) / 100.0

        # Combine decisions with weighted approach
        if rl_action_type == llm_recommendation:
            confidence = min(0.9, 0.6 + llm_confidence * 0.3)
            quantity = 0.1 if "small" in rl_action_type else 0.2
        else:
            confidence = 0.3
            quantity = 0.05
            rl_action_type = "hold"  # Conservative approach when disagreeing

        return TradingAction(
            action_type=rl_action_type.split('_')[0] if '_' in rl_action_type else rl_action_type,
            quantity=quantity,
            confidence=confidence
        )

    async def execute_trade(self, action: TradingAction):
        """Execute trading action"""
        if action.action_type == "hold":
            return

        trade_value = action.quantity * self.current_price * self.portfolio_value

        if action.action_type == "buy" and trade_value <= self.portfolio_value * 0.95:
            # Execute buy
            self.position_size += action.quantity
            self.portfolio_value -= trade_value * 1.001  # Include fees

            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "buy",
                "quantity": action.quantity,
                "price": self.current_price,
                "value": trade_value,
                "confidence": action.confidence
            }

        elif action.action_type == "sell" and self.position_size >= action.quantity:
            # Execute sell
            self.position_size -= action.quantity
            self.portfolio_value += trade_value * 0.999  # Include fees

            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "sell",
                "quantity": action.quantity,
                "price": self.current_price,
                "value": trade_value,
                "confidence": action.confidence
            }
        else:
            return  # Invalid trade

        self.trade_history.append(trade_record)
        logger.info(f"💰 Trade executed: {trade_record['action']} {trade_record['quantity']:.4f} @ ${trade_record['price']:.2f}")

    async def train_model(self):
        """Train the RL model"""
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states = torch.stack([exp[0] for exp in batch]).to(self.device)
        actions = torch.tensor([exp[1] for exp in batch]).to(self.device)
        rewards = torch.tensor([exp[2] for exp in batch]).to(self.device)
        next_states = torch.stack([exp[3] for exp in batch]).to(self.device)
        dones = torch.tensor([exp[4] for exp in batch]).to(self.device)

        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))

        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Update target network
        if len(self.memory) % 1000 == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

    async def save_model(self):
        """Save the trained model"""
        model_path = self.data_path / "enhanced_rl_model.pth"
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'portfolio_value': self.portfolio_value,
            'position_size': self.position_size
        }, model_path)

        # Save performance history
        history_path = self.data_path / "performance_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump({
                "performance": self.performance_history[-100:],  # Last 100 records
                "trades": self.trade_history[-50:]  # Last 50 trades
            }, f, indent=2)

    async def load_model(self):
        """Load existing model"""
        model_path = self.data_path / "enhanced_rl_model.pth"
        if model_path.exists():
            checkpoint = torch.load(model_path, map_location=self.device)
            self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
            self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint.get('epsilon', self.epsilon)
            self.portfolio_value = checkpoint.get('portfolio_value', self.portfolio_value)
            self.position_size = checkpoint.get('position_size', self.position_size)
            logger.info(f"✅ Model loaded from {model_path}")

async def main():
    """Main function"""
    system = Enhanced24x7RLTradingSystem()
    await system.start_24x7_operation()

if __name__ == "__main__":
    asyncio.run(main())
