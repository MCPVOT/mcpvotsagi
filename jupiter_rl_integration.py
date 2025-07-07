
#!/usr/bin/env python3
"""
Jupiter RL Integration V3 - Enhanced
====================================
Advanced reinforcement learning integration with Jupiter DEX
Features machine learning models, advanced strategies, and real-time optimization
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sqlite3
import pickle
import os
from dataclasses import dataclass
from enum import Enum
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JupiterRL")

# Import our components
try:
    from jupiter_api_wrapper import JupiterAPIWrapper, TokenInfo, PriceData
    from deepseek_r1_trading_agent_enhanced import DeepSeekR1TradingAgent
    HAS_JUPITER = True
except ImportError as e:
    logger.warning(f"Jupiter components not available: {e}")
    HAS_JUPITER = False

# ML libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    HAS_ML = True
except ImportError:
    logger.warning("ML libraries not available - using simplified models")
    HAS_ML = False

@dataclass
class RLState:
    """RL state representation"""
    price_history: List[float]
    volume_history: List[float]
    volatility: float
    rsi: float
    macd: float
    bollinger_position: float
    portfolio_value: float
    active_positions: int
    market_trend: str
    timestamp: datetime

@dataclass
class RLAction:
    """RL action representation"""
    action_type: str  # 'BUY', 'SELL', 'HOLD'
    amount: float
    confidence: float
    risk_score: float
    expected_return: float
    stop_loss: float
    take_profit: float

@dataclass
class RLReward:
    """RL reward calculation"""
    immediate_reward: float
    risk_adjusted_reward: float
    long_term_reward: float
    total_reward: float
    penalty: float

class RLTradingStrategy(Enum):
    """Available RL trading strategies"""
    Q_LEARNING = "q_learning"
    DEEP_Q_NETWORK = "dqn"
    POLICY_GRADIENT = "policy_gradient"
    ACTOR_CRITIC = "actor_critic"
    RANDOM_FOREST = "random_forest"
    ENSEMBLE = "ensemble"

class DeepQNetwork(nn.Module):
    """Deep Q-Network for RL trading"""

    def __init__(self, state_size: int, action_size: int, hidden_size: int = 256):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, action_size)
        )

    def forward(self, x):
        return self.network(x)

class JupiterRLIntegration:
    """Advanced Jupiter RL Integration with enhanced ML capabilities"""

    def __init__(self):
        self.jupiter_api = JupiterAPIWrapper() if HAS_JUPITER else None
        self.deepseek_agent = DeepSeekR1TradingAgent() if HAS_JUPITER else None
        self.f_drive_path = "F:/ULTIMATE_AGI_DATA/RL_TRADING/"
        self.models_path = os.path.join(self.f_drive_path, "models")
        self.data_path = os.path.join(self.f_drive_path, "data")
        self.db_path = os.path.join(self.f_drive_path, "rl_integration.db")

        # Ensure directories exist
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)

        # RL Parameters
        self.state_size = 20  # Features in state vector
        self.action_size = 5  # Number of possible actions
        self.learning_rate = 0.001
        self.gamma = 0.95  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.memory_size = 10000
        self.batch_size = 32

        # Models
        self.dqn_model = None
        self.random_forest = None
        self.scaler = StandardScaler()

        # Training data
        self.memory = []
        self.state_history = []
        self.action_history = []
        self.reward_history = []

        # Performance tracking
        self.total_reward = 0.0
        self.episode_rewards = []
        self.win_rate = 0.0
        self.sharpe_ratio = 0.0

        # Initialize models
        self._initialize_models()
        self._initialize_database()

        logger.info("🧠 Jupiter RL Integration initialized")

    def _initialize_models(self):
        """Initialize ML models"""
        try:
            if HAS_ML:
                # Initialize Deep Q-Network
                self.dqn_model = DeepQNetwork(self.state_size, self.action_size)
                self.dqn_optimizer = optim.Adam(self.dqn_model.parameters(), lr=self.learning_rate)
                self.dqn_criterion = nn.MSELoss()

                # Initialize Random Forest
                self.random_forest = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )

                # Try to load existing models
                self._load_models()

            logger.info("✅ ML models initialized")

        except Exception as e:
            logger.error(f"Error initializing models: {e}")

    def _initialize_database(self):
        """Initialize SQLite database for RL data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rl_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_pair TEXT NOT NULL,
                    price_history TEXT NOT NULL,
                    volume_history TEXT NOT NULL,
                    volatility REAL NOT NULL,
                    rsi REAL NOT NULL,
                    macd REAL NOT NULL,
                    bollinger_position REAL NOT NULL,
                    portfolio_value REAL NOT NULL,
                    active_positions INTEGER NOT NULL,
                    market_trend TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rl_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    confidence REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    expected_return REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (state_id) REFERENCES rl_states (id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rl_rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id INTEGER NOT NULL,
                    immediate_reward REAL NOT NULL,
                    risk_adjusted_reward REAL NOT NULL,
                    long_term_reward REAL NOT NULL,
                    total_reward REAL NOT NULL,
                    penalty REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (action_id) REFERENCES rl_actions (id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rl_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode INTEGER NOT NULL,
                    total_reward REAL NOT NULL,
                    win_rate REAL NOT NULL,
                    sharpe_ratio REAL NOT NULL,
                    max_drawdown REAL NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("📊 RL database initialized")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    async def analyze_trading_opportunity(self, token_pair: str) -> Dict[str, Any]:
        """Enhanced trading opportunity analysis with RL"""
        try:
            logger.info(f"🔍 Analyzing trading opportunity for {token_pair}")

            # Get market data
            market_data = await self._get_market_data(token_pair)
            if not market_data:
                return {"error": "Failed to get market data"}

            # Create RL state
            rl_state = await self._create_rl_state(token_pair, market_data)

            # Get RL action recommendation
            rl_action = await self._get_rl_action(rl_state)

            # Use DeepSeek for additional analysis
            deepseek_analysis = await self._get_deepseek_analysis(market_data)

            # Combine analyses
            combined_analysis = {
                "token_pair": token_pair,
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "rl_state": {
                    "volatility": rl_state.volatility,
                    "rsi": rl_state.rsi,
                    "macd": rl_state.macd,
                    "bollinger_position": rl_state.bollinger_position,
                    "market_trend": rl_state.market_trend
                },
                "rl_action": {
                    "action_type": rl_action.action_type,
                    "amount": rl_action.amount,
                    "confidence": rl_action.confidence,
                    "risk_score": rl_action.risk_score,
                    "expected_return": rl_action.expected_return,
                    "stop_loss": rl_action.stop_loss,
                    "take_profit": rl_action.take_profit
                },
                "deepseek_analysis": deepseek_analysis,
                "recommendation": await self._generate_recommendation(rl_action, deepseek_analysis)
            }

            # Store analysis
            await self._store_analysis(combined_analysis)

            # Update RL models
            await self._update_rl_models(rl_state, rl_action)

            return combined_analysis

        except Exception as e:
            logger.error(f"Error analyzing trading opportunity: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def _get_market_data(self, token_pair: str) -> Optional[Dict]:
        """Get comprehensive market data"""
        try:
            if not self.jupiter_api:
                return None

            # Parse token pair
            base_token, quote_token = token_pair.split('/')

            # Get tokens list
            tokens = await self.jupiter_api.get_tokens()
            if not tokens:
                return None

            # Find token addresses
            base_address = None
            quote_address = None

            for token in tokens:
                if token.symbol == base_token:
                    base_address = token.address
                if token.symbol == quote_token:
                    quote_address = token.address

            if not base_address or not quote_address:
                logger.warning(f"Token addresses not found for {token_pair}")
                return None

            # Get quote
            quote = await self.jupiter_api.get_quote(
                input_mint=base_address,
                output_mint=quote_address,
                amount=1000000  # 1 token
            )

            # Get prices
            prices = await self.jupiter_api.get_prices([base_address, quote_address])

            return {
                "base_token": base_token,
                "quote_token": quote_token,
                "base_address": base_address,
                "quote_address": quote_address,
                "quote": quote,
                "prices": prices,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None

    async def _create_rl_state(self, token_pair: str, market_data: Dict) -> RLState:
        """Create RL state from market data"""
        try:
            # Extract real market data
            quote = market_data.get("quote", {})
            prices = market_data.get("prices", {})
            token_info = market_data.get("token_info", {})

            # Get real price history from Jupiter API
            current_price = float(quote.get("price", 0)) if quote.get("price") else 0

            # Try to get historical data - if not available, use current price
            if hasattr(self, 'jupiter_api') and self.jupiter_api:
                try:
                    # Get recent price history (last 10 data points)
                    historical_data = await self.jupiter_api.get_historical_prices(
                        token_info.get("mint", ""),
                        hours=24
                    )
                    if historical_data:
                        price_history = [float(p) for p in historical_data[-10:]]
                        volume_history = [float(v.get("volume", 0)) for v in historical_data[-10:]]
                    else:
                        price_history = [current_price] * 5
                        volume_history = [float(quote.get("volume", 1000))] * 5
                except Exception as e:
                    logger.warning(f"Could not get historical data: {e}")
                    price_history = [current_price] * 5
                    volume_history = [float(quote.get("volume", 1000))] * 5
            else:
                price_history = [current_price] * 5
                volume_history = [float(quote.get("volume", 1000))] * 5

            # Calculate real technical indicators
            volatility = await self._calculate_volatility(price_history)
            rsi = await self._calculate_rsi(price_history)
            macd = await self._calculate_macd(price_history)
            bollinger_position = await self._calculate_bollinger_position(price_history)

            # Market trend analysis from real data
            market_trend = await self._determine_market_trend(price_history)

            # Use real portfolio value if available
            portfolio_value = getattr(self, 'portfolio_value', 10000.0)
            active_positions = getattr(self, 'active_positions', 0)

            return RLState(
                price_history=price_history,
                volume_history=volume_history,
                volatility=volatility,
                rsi=rsi,
                macd=macd,
                bollinger_position=bollinger_position,
                portfolio_value=portfolio_value,
                active_positions=active_positions,
                market_trend=market_trend,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error creating RL state: {e}")
            # Return minimal state with real current price if available
            current_price = float(market_data.get("quote", {}).get("price", 100)) if market_data.get("quote", {}).get("price") else 100
            return RLState(
                price_history=[current_price],
                volume_history=[1000.0],
                volatility=0.1,
                rsi=50.0,
                macd=0.0,
                bollinger_position=0.0,
                portfolio_value=10000.0,
                active_positions=0,
                market_trend="NEUTRAL",
                timestamp=datetime.now()
            )

    async def _get_rl_action(self, rl_state: RLState) -> RLAction:
        """Get RL action recommendation"""
        try:
            # Convert state to feature vector
            state_vector = self._state_to_vector(rl_state)

            if HAS_ML and self.dqn_model:
                # Use DQN model
                action_values = self._predict_dqn(state_vector)
                action_index = np.argmax(action_values)

                # Map action index to action
                actions = ['HOLD', 'BUY_SMALL', 'BUY_LARGE', 'SELL_SMALL', 'SELL_LARGE']
                action_type = actions[action_index]

                # Calculate action parameters
                if action_type == 'HOLD':
                    amount = 0.0
                    confidence = 0.5
                elif 'BUY' in action_type:
                    amount = 0.1 if 'SMALL' in action_type else 0.2
                    confidence = 0.7
                    action_type = 'BUY'
                else:  # SELL
                    amount = 0.1 if 'SMALL' in action_type else 0.2
                    confidence = 0.7
                    action_type = 'SELL'

            else:
                # Use rule-based system
                if rl_state.rsi < 30 and rl_state.macd > 0:
                    action_type = 'BUY'
                    amount = 0.1
                    confidence = 0.6
                elif rl_state.rsi > 70 and rl_state.macd < 0:
                    action_type = 'SELL'
                    amount = 0.1
                    confidence = 0.6
                else:
                    action_type = 'HOLD'
                    amount = 0.0
                    confidence = 0.5

            # Calculate risk and returns
            risk_score = self._calculate_risk_score(rl_state)
            expected_return = self._calculate_expected_return(rl_state, action_type)

            # Calculate stop loss and take profit
            current_price = rl_state.price_history[-1]
            stop_loss = current_price * 0.98 if action_type == 'BUY' else current_price * 1.02
            take_profit = current_price * 1.05 if action_type == 'BUY' else current_price * 0.95

            return RLAction(
                action_type=action_type,
                amount=amount,
                confidence=confidence,
                risk_score=risk_score,
                expected_return=expected_return,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

        except Exception as e:
            logger.error(f"Error getting RL action: {e}")
            return RLAction(
                action_type='HOLD',
                amount=0.0,
                confidence=0.5,
                risk_score=0.5,
                expected_return=0.0,
                stop_loss=0.0,
                take_profit=0.0
            )

    async def _get_deepseek_analysis(self, market_data: Dict) -> Dict:
        """Get analysis from DeepSeek agent"""
        try:
            if not self.deepseek_agent:
                return {"analysis": "DeepSeek agent not available"}

            # Use DeepSeek for market analysis
            analysis = await self.deepseek_agent.analyze_market_conditions(market_data)
            return analysis

        except Exception as e:
            logger.error(f"Error getting DeepSeek analysis: {e}")
            return {"error": str(e)}

    async def _generate_recommendation(self, rl_action: RLAction, deepseek_analysis: Dict) -> Dict:
        """Generate combined recommendation"""
        try:
            # Combine RL and DeepSeek recommendations
            recommendation = {
                "action": rl_action.action_type,
                "confidence": rl_action.confidence,
                "risk_level": "LOW" if rl_action.risk_score < 0.3 else "MEDIUM" if rl_action.risk_score < 0.7 else "HIGH",
                "position_size": rl_action.amount,
                "expected_return": rl_action.expected_return,
                "stop_loss": rl_action.stop_loss,
                "take_profit": rl_action.take_profit,
                "reasoning": f"RL model suggests {rl_action.action_type} with {rl_action.confidence:.2f} confidence",
                "deepseek_confirmation": deepseek_analysis.get("recommendation", "No additional insights")
            }

            return recommendation

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return {"error": str(e)}

    async def _store_analysis(self, analysis: Dict):
        """Store analysis results"""
        try:
            timestamp = datetime.now().isoformat()
            filename = f"rl_analysis_{timestamp.replace(':', '-')}.json"
            filepath = os.path.join(self.data_path, filename)

            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"📁 Analysis stored: {filename}")

        except Exception as e:
            logger.error(f"Error storing analysis: {e}")

    async def _update_rl_models(self, rl_state: RLState, rl_action: RLAction):
        """Update RL models with new data"""
        try:
            # Add to memory
            state_vector = self._state_to_vector(rl_state)
            action_vector = self._action_to_vector(rl_action)

            self.memory.append({
                "state": state_vector,
                "action": action_vector,
                "timestamp": datetime.now()
            })

            # Limit memory size
            if len(self.memory) > self.memory_size:
                self.memory.pop(0)

            # Train models periodically
            if len(self.memory) >= self.batch_size and len(self.memory) % 10 == 0:
                await self._train_models()

        except Exception as e:
            logger.error(f"Error updating RL models: {e}")

    def _state_to_vector(self, rl_state: RLState) -> np.ndarray:
        """Convert RL state to feature vector"""
        try:
            features = [
                rl_state.volatility,
                rl_state.rsi,
                rl_state.macd,
                rl_state.bollinger_position,
                rl_state.portfolio_value / 10000.0,  # Normalized
                rl_state.active_positions,
                1.0 if rl_state.market_trend == "BULLISH" else 0.0,
                1.0 if rl_state.market_trend == "BEARISH" else 0.0,
                # Price history features
                np.mean(rl_state.price_history),
                np.std(rl_state.price_history),
                np.max(rl_state.price_history),
                np.min(rl_state.price_history),
                # Volume history features
                np.mean(rl_state.volume_history),
                np.std(rl_state.volume_history),
                np.max(rl_state.volume_history),
                np.min(rl_state.volume_history),
                # Additional real market features
                len(rl_state.price_history),
                len(rl_state.volume_history),
                rl_state.rsi,
                rl_state.macd
            ]

            return np.array(features, dtype=np.float32)

        except Exception as e:
            logger.error(f"Error converting state to vector: {e}")
            return np.zeros(self.state_size, dtype=np.float32)

    def _action_to_vector(self, rl_action: RLAction) -> np.ndarray:
        """Convert RL action to vector"""
        try:
            action_index = 0
            if rl_action.action_type == 'BUY':
                action_index = 1 if rl_action.amount < 0.15 else 2
            elif rl_action.action_type == 'SELL':
                action_index = 3 if rl_action.amount < 0.15 else 4

            return np.array([action_index], dtype=np.int32)

        except Exception as e:
            logger.error(f"Error converting action to vector: {e}")
            return np.array([0], dtype=np.int32)

    async def _train_models(self):
        """Train RL models with accumulated data"""
        try:
            if not HAS_ML or len(self.memory) < self.batch_size:
                return

            logger.info("🎯 Training RL models...")

            # Prepare training data
            states = []
            actions = []
            rewards = []

            for i, memory_item in enumerate(self.memory[-self.batch_size:]):
                states.append(memory_item["state"])
                actions.append(memory_item["action"])
                # Simulate reward (in real implementation, this would be actual returns)
                rewards.append(np.random.normal(0, 0.1))

            states = np.array(states)
            actions = np.array(actions)
            rewards = np.array(rewards)

            # Train DQN
            if self.dqn_model:
                await self._train_dqn(states, actions, rewards)

            # Train Random Forest
            if self.random_forest and len(states) > 10:
                await self._train_random_forest(states, rewards)

            # Save models
            await self._save_models()

            logger.info("✅ RL models trained successfully")

        except Exception as e:
            logger.error(f"Error training models: {e}")

    async def _train_dqn(self, states: np.ndarray, actions: np.ndarray, rewards: np.ndarray):
        """Train Deep Q-Network"""
        try:
            if not self.dqn_model:
                return

            # Convert to tensors
            states_tensor = torch.FloatTensor(states)
            actions_tensor = torch.LongTensor(actions.flatten())
            rewards_tensor = torch.FloatTensor(rewards)

            # Forward pass
            current_q_values = self.dqn_model(states_tensor)
            current_q_values = current_q_values.gather(1, actions_tensor.unsqueeze(1))

            # Calculate target Q-values
            target_q_values = rewards_tensor.unsqueeze(1)

            # Calculate loss
            loss = self.dqn_criterion(current_q_values, target_q_values)

            # Backward pass
            self.dqn_optimizer.zero_grad()
            loss.backward()
            self.dqn_optimizer.step()

            # Update epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

        except Exception as e:
            logger.error(f"Error training DQN: {e}")

    async def _train_random_forest(self, states: np.ndarray, rewards: np.ndarray):
        """Train Random Forest model"""
        try:
            if not self.random_forest:
                return

            # Scale features
            states_scaled = self.scaler.fit_transform(states)

            # Train model
            self.random_forest.fit(states_scaled, rewards)

        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")

    def _predict_dqn(self, state_vector: np.ndarray) -> np.ndarray:
        """Predict using DQN model"""
        try:
            if not self.dqn_model:
                return np.zeros(self.action_size)

            state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
            with torch.no_grad():
                q_values = self.dqn_model(state_tensor)

            return q_values.numpy().flatten()

        except Exception as e:
            logger.error(f"Error predicting with DQN: {e}")
            return np.zeros(self.action_size)

    async def _save_models(self):
        """Save trained models"""
        try:
            if HAS_ML:
                if self.dqn_model:
                    torch.save(self.dqn_model.state_dict(), os.path.join(self.models_path, "dqn_model.pth"))

                if self.random_forest:
                    with open(os.path.join(self.models_path, "random_forest.pkl"), 'wb') as f:
                        pickle.dump(self.random_forest, f)

                with open(os.path.join(self.models_path, "scaler.pkl"), 'wb') as f:
                    pickle.dump(self.scaler, f)

            logger.info("💾 Models saved successfully")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    def _load_models(self):
        """Load existing models"""
        try:
            if HAS_ML:
                dqn_path = os.path.join(self.models_path, "dqn_model.pth")
                rf_path = os.path.join(self.models_path, "random_forest.pkl")
                scaler_path = os.path.join(self.models_path, "scaler.pkl")

                if os.path.exists(dqn_path) and self.dqn_model:
                    self.dqn_model.load_state_dict(torch.load(dqn_path))
                    logger.info("📂 DQN model loaded")

                if os.path.exists(rf_path):
                    with open(rf_path, 'rb') as f:
                        self.random_forest = pickle.load(f)
                    logger.info("📂 Random Forest model loaded")

                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    logger.info("📂 Scaler loaded")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

    # Technical indicator calculations
    async def _calculate_volatility(self, price_history: List[float]) -> float:
        """Calculate price volatility"""
        if len(price_history) < 2:
            return 0.1
        return float(np.std(price_history))

    async def _calculate_rsi(self, price_history: List[float]) -> float:
        """Calculate RSI"""
        if len(price_history) < 2:
            return 50.0

        deltas = np.diff(price_history)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi)

    async def _calculate_macd(self, price_history: List[float]) -> float:
        """Calculate MACD"""
        if len(price_history) < 12:
            return 0.0

        # Simple MACD calculation
        ema_12 = np.mean(price_history[-12:])
        ema_26 = np.mean(price_history[-26:]) if len(price_history) >= 26 else np.mean(price_history)

        return float(ema_12 - ema_26)

    async def _calculate_bollinger_position(self, price_history: List[float]) -> float:
        """Calculate position relative to Bollinger Bands"""
        if len(price_history) < 20:
            return 0.0

        sma = np.mean(price_history[-20:])
        std = np.std(price_history[-20:])

        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)

        current_price = price_history[-1]

        if upper_band == lower_band:
            return 0.0

        return float((current_price - lower_band) / (upper_band - lower_band))

    async def _determine_market_trend(self, price_history: List[float]) -> str:
        """Determine market trend"""
        if len(price_history) < 3:
            return "NEUTRAL"

        recent_trend = np.mean(price_history[-3:]) - np.mean(price_history[-6:-3]) if len(price_history) >= 6 else 0

        if recent_trend > 0.01:
            return "BULLISH"
        elif recent_trend < -0.01:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def _calculate_risk_score(self, rl_state: RLState) -> float:
        """Calculate risk score for current state"""
        risk_factors = [
            rl_state.volatility,
            abs(rl_state.rsi - 50) / 50,  # Distance from neutral RSI
            abs(rl_state.macd),
            rl_state.active_positions / 10  # Normalized position count
        ]

        return float(np.mean(risk_factors))

    def _calculate_expected_return(self, rl_state: RLState, action_type: str) -> float:
        """Calculate expected return for action"""
        if action_type == 'HOLD':
            return 0.0

        # Simple expected return calculation
        trend_factor = 1.0 if rl_state.market_trend == "BULLISH" else -1.0 if rl_state.market_trend == "BEARISH" else 0.0
        volatility_factor = rl_state.volatility

        if action_type == 'BUY':
            return trend_factor * 0.02 - volatility_factor * 0.01
        else:  # SELL
            return -trend_factor * 0.02 - volatility_factor * 0.01

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "total_reward": self.total_reward,
            "episode_rewards": self.episode_rewards[-10:],  # Last 10 episodes
            "win_rate": self.win_rate,
            "sharpe_ratio": self.sharpe_ratio,
            "memory_size": len(self.memory),
            "epsilon": self.epsilon,
            "models_loaded": {
                "dqn": self.dqn_model is not None,
                "random_forest": self.random_forest is not None,
                "scaler": hasattr(self.scaler, 'scale_')
            }
        }

# Test function
async def test_jupiter_rl():
    """Test Jupiter RL integration"""
    rl_integration = JupiterRLIntegration()

    # Test trading opportunity analysis
    result = await rl_integration.analyze_trading_opportunity("SOL/USDC")
    print(f"Analysis result: {json.dumps(result, indent=2)}")

    # Show performance metrics
    metrics = rl_integration.get_performance_metrics()
    print(f"Performance metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_jupiter_rl())