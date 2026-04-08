#!/usr/bin/env python3
"""
Enhanced DeepSeek-Powered Autonomous Trading Agent
=================================================
24/7 self-learning RL/ML agent with F:\ drive storage (853 GB)
Enhanced with advanced RL algorithms and massive data capabilities
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
from typing import Optional, Tuple, Deque
import websockets
import aiohttp
from dataclasses import dataclass, asdict
import sqlite3
import pickle
import h5py
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DeepSeekTradingAgentEnhanced")

# F:\ Drive Storage Configuration
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data")
RL_DATA_PATH = F_DRIVE_ROOT / "rl_training"
MARKET_DATA_PATH = F_DRIVE_ROOT / "market_data"
MODEL_PATH = F_DRIVE_ROOT / "models" / "trading_agents"
MEMORY_PATH = F_DRIVE_ROOT / "memory"

@dataclass
class EnhancedMarketState:
    """Enhanced market state with additional features"""
    timestamp: datetime
    prices: dict[str, float]
    volumes: dict[str, float]
    rsi: dict[str, float]
    macd: dict[str, Dict[str, float]]
    bollinger_bands: dict[str, Dict[str, float]]
    order_book_imbalance: dict[str, float]
    sentiment: float
    volatility: float
    correlation_matrix: np.ndarray
    market_regime: str  # 'trending', 'ranging', 'volatile'
    
class DeepQNetwork(nn.Module):
    """Deep Q-Network with attention mechanism"""
    
    def __init__(self, state_size: int, action_size: int, hidden_sizes: list[int] = [512, 256, 128]):
        super(DeepQNetwork, self).__init__()
        
        # Build layers
        layers = []
        prev_size = state_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
            
        # Attention layer
        self.attention = nn.MultiheadAttention(hidden_sizes[-1], num_heads=4)
        
        # Output layers
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_sizes[-1], hidden_sizes[-1] // 2),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1] // 2, 1)
        )
        
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_sizes[-1], hidden_sizes[-1] // 2),
            nn.ReLU(),
            nn.Linear(hidden_sizes[-1] // 2, action_size)
        )
        
        self.features = nn.Sequential(*layers[:-1])  # Remove last dropout
        
    def forward(self, x):
        features = self.features(x)
        
        # Self-attention
        features = features.unsqueeze(0)  # Add sequence dimension
        attn_output, _ = self.attention(features, features, features)
        features = attn_output.squeeze(0)
        
        # Dueling DQN
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Combine value and advantage
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        
        return q_values

class ExperienceReplayBuffer:
    """Massive experience replay buffer using F:\ drive storage"""
    
    def __init__(self, capacity: int = 10_000_000, chunk_size: int = 100_000):
        self.capacity = capacity
        self.chunk_size = chunk_size
        self.buffer_path = RL_DATA_PATH / "experience_replay"
        self.buffer_path.mkdir(parents=True, exist_ok=True)
        
        self.position = 0
        self.size = 0
        self.current_chunk = 0
        self.memory_cache = deque(maxlen=chunk_size)
        
        # Initialize metadata
        self.metadata_path = self.buffer_path / "metadata.json"
        self._load_metadata()
        
    def _load_metadata(self):
        """Load or create metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path) as f:
                metadata = json.load(f)
                self.position = metadata["position"]
                self.size = metadata["size"]
                self.current_chunk = metadata["current_chunk"]
        else:
            self._save_metadata()
            
    def _save_metadata(self):
        """Save metadata"""
        metadata = {
            "position": self.position,
            "size": self.size,
            "current_chunk": self.current_chunk,
            "capacity": self.capacity,
            "chunk_size": self.chunk_size
        }
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f)
            
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        experience = (state, action, reward, next_state, done)
        self.memory_cache.append(experience)
        
        # Save to disk when cache is full
        if len(self.memory_cache) >= self.chunk_size:
            self._save_chunk()
            
        self.position = (self.position + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)
        
    def _save_chunk(self):
        """Save current chunk to disk"""
        chunk_file = self.buffer_path / f"chunk_{self.current_chunk:06d}.h5"
        
        with h5py.File(chunk_file, 'w') as f:
            states = np.array([e[0] for e in self.memory_cache])
            actions = np.array([e[1] for e in self.memory_cache])
            rewards = np.array([e[2] for e in self.memory_cache])
            next_states = np.array([e[3] for e in self.memory_cache])
            dones = np.array([e[4] for e in self.memory_cache])
            
            f.create_dataset('states', data=states, compression='gzip')
            f.create_dataset('actions', data=actions)
            f.create_dataset('rewards', data=rewards)
            f.create_dataset('next_states', data=next_states, compression='gzip')
            f.create_dataset('dones', data=dones)
            
        self.current_chunk = (self.current_chunk + 1) % (self.capacity // self.chunk_size)
        self.memory_cache.clear()
        self._save_metadata()
        
    def sample(self, batch_size: int):
        """Sample batch from buffer"""
        if self.size < batch_size:
            return None
            
        # Sample from multiple chunks for diversity
        samples = []
        chunks_to_sample = min(5, self.current_chunk + 1)
        samples_per_chunk = batch_size // chunks_to_sample
        
        for i in range(chunks_to_sample):
            chunk_idx = (self.current_chunk - i) % (self.capacity // self.chunk_size)
            chunk_file = self.buffer_path / f"chunk_{chunk_idx:06d}.h5"
            
            if chunk_file.exists():
                with h5py.File(chunk_file, 'r') as f:
                    chunk_size = f['states'].shape[0]
                    indices = np.random.choice(chunk_size, samples_per_chunk, replace=False)
                    
                    states = f['states'][indices]
                    actions = f['actions'][indices]
                    rewards = f['rewards'][indices]
                    next_states = f['next_states'][indices]
                    dones = f['dones'][indices]
                    
                    for j in range(samples_per_chunk):
                        samples.append((states[j], actions[j], rewards[j], next_states[j], dones[j]))
                        
        # Add samples from current cache
        if len(self.memory_cache) > 0:
            cache_samples = min(batch_size - len(samples), len(self.memory_cache))
            indices = np.random.choice(len(self.memory_cache), cache_samples, replace=False)
            for idx in indices:
                samples.append(self.memory_cache[idx])
                
        return samples[:batch_size]

class AdvancedRLEngine:
    """Advanced RL engine with multiple algorithms"""
    
    def __init__(self, state_size: int = 50, action_size: int = 3):
        self.state_size = state_size
        self.action_size = action_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Networks
        self.q_network = DeepQNetwork(state_size, action_size).to(self.device)
        self.target_network = DeepQNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.0001)
        
        # RL parameters
        self.gamma = 0.99
        self.tau = 0.001  # Soft update parameter
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        
        # Experience replay with F:\ drive storage
        self.memory = ExperienceReplayBuffer(capacity=10_000_000)
        self.batch_size = 256
        
        # Training metrics
        self.training_history = []
        self.model_checkpoint_path = MODEL_PATH / "dqn_checkpoints"
        self.model_checkpoint_path.mkdir(parents=True, exist_ok=True)
        
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""
        if training and np.random.random() <= self.epsilon:
            return np.random.choice(self.action_size)
            
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
            
        return np.argmax(q_values.cpu().numpy())
        
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
        
    def replay(self):
        """Train on batch of experiences"""
        batch = self.memory.sample(self.batch_size)
        if batch is None:
            return None
            
        states = torch.FloatTensor([e[0] for e in batch]).to(self.device)
        actions = torch.LongTensor([e[1] for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e[2] for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e[3] for e in batch]).to(self.device)
        dones = torch.FloatTensor([e[4] for e in batch]).to(self.device)
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
            
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Soft update target network
        self._soft_update()
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return loss.item()
        
    def _soft_update(self):
        """Soft update target network"""
        for target_param, param in zip(self.target_network.parameters(), self.q_network.parameters()):
            target_param.data.copy_(self.tau * param.data + (1.0 - self.tau) * target_param.data)
            
    def save_checkpoint(self, episode: int, performance_metrics: dict[str, float]):
        """Save model checkpoint"""
        checkpoint = {
            'episode': episode,
            'model_state_dict': self.q_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'performance_metrics': performance_metrics,
            'training_history': self.training_history[-1000:]  # Last 1000 episodes
        }
        
        checkpoint_path = self.model_checkpoint_path / f"checkpoint_episode_{episode}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Keep only last 50 checkpoints
        checkpoints = sorted(self.model_checkpoint_path.glob("checkpoint_*.pt"))
        if len(checkpoints) > 50:
            for old_checkpoint in checkpoints[:-50]:
                old_checkpoint.unlink()
                
    def load_checkpoint(self, checkpoint_path: Optional[Path] = None):
        """Load model checkpoint"""
        if checkpoint_path is None:
            # Load latest checkpoint
            checkpoints = sorted(self.model_checkpoint_path.glob("checkpoint_*.pt"))
            if not checkpoints:
                logger.info("No checkpoint found")
                return False
            checkpoint_path = checkpoints[-1]
            
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['model_state_dict'])
        self.target_network.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_history = checkpoint.get('training_history', [])
        
        logger.info(f"Loaded checkpoint from episode {checkpoint['episode']}")
        return True

class MarketDataManager:
    """Manages market data storage and retrieval from F:\ drive"""
    
    def __init__(self):
        self.data_path = MARKET_DATA_PATH
        self.price_history_path = self.data_path / "price_history"
        self.indicators_path = self.data_path / "indicators"
        self.tick_data_path = self.data_path / "tick_data"
        
        # Ensure directories exist
        for path in [self.price_history_path, self.indicators_path, self.tick_data_path]:
            path.mkdir(parents=True, exist_ok=True)
            
        # Initialize database connection
        self.db_path = self.data_path / "market_data.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize market data database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Price data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp REAL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                timeframe TEXT,
                UNIQUE(symbol, timestamp, timeframe)
            )
        """)
        
        # Indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp REAL,
                indicator_name TEXT,
                value REAL,
                parameters TEXT,
                UNIQUE(symbol, timestamp, indicator_name, parameters)
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_symbol_time ON price_data(symbol, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicators_symbol_time ON indicators(symbol, timestamp)")
        
        conn.commit()
        conn.close()
        
    async def store_market_data(self, symbol: str, data: pd.DataFrame):
        """Store market data to F:\ drive"""
        # Store in database
        conn = sqlite3.connect(self.db_path)
        data['symbol'] = symbol
        data.to_sql('price_data', conn, if_exists='append', index=False)
        conn.close()
        
        # Store in parquet for fast access
        parquet_path = self.price_history_path / f"{symbol}_{datetime.now().strftime('%Y%m')}.parquet"
        data.to_parquet(parquet_path, compression='snappy')
        
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Retrieve historical data from F:\ drive"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT timestamp, open, high, low, close, volume
            FROM price_data
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """
        
        df = pd.read_sql_query(
            query, 
            conn, 
            params=(symbol, start_date.timestamp(), end_date.timestamp())
        )
        
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
        return df
        
    async def calculate_indicators(self, symbol: str, df: pd.DataFrame) -> dict[str, pd.Series]:
        """Calculate and store technical indicators"""
        indicators = {}
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        indicators['macd'] = exp1 - exp2
        indicators['signal'] = indicators['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        indicators['bb_upper'] = sma + (std * 2)
        indicators['bb_lower'] = sma - (std * 2)
        indicators['bb_middle'] = sma
        
        # Store indicators
        conn = sqlite3.connect(self.db_path)
        for indicator_name, values in indicators.items():
            for timestamp, value in values.items():
                if not pd.isna(value):
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO indicators 
                        (symbol, timestamp, indicator_name, value, parameters)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, timestamp.timestamp(), indicator_name, float(value), "default"))
                    
        conn.commit()
        conn.close()
        
        return indicators

class EnhancedAutonomousTradingAgent:
    """Enhanced autonomous trading agent with F:\ drive storage"""
    
    def __init__(self):
        self.deepseek_brain = DeepSeekTradingBrain()
        self.rl_engine = AdvancedRLEngine(state_size=50, action_size=3)
        self.market_data_manager = MarketDataManager()
        self.performance_tracker = EnhancedPerformanceTracker()
        
        # Trading configuration
        self.trading_pairs = ["GOLD/USD", "SILVER/USD", "PLATINUM/USD", "PALLADIUM/USD"]
        self.max_position_size = 0.1
        self.stop_loss = 0.05
        self.take_profit = 0.15
        
        # Portfolio
        self.portfolio = {
            "USD": 100000,  # $100k starting capital
            "positions": {},
            "pending_orders": []
        }
        
        # Market regime detection
        self.regime_detector = MarketRegimeDetector()
        
        # Risk management
        self.risk_manager = RiskManager(
            max_drawdown=0.20,
            position_limit=4,
            correlation_threshold=0.7
        )
        
        self.is_running = False
        self.episode = 0
        
    async def initialize(self):
        """Initialize all components"""
        await self.deepseek_brain.connect()
        
        # Load RL model if exists
        self.rl_engine.load_checkpoint()
        
        # Load historical market data
        logger.info("Loading historical market data from F:\\ drive...")
        for symbol in self.trading_pairs:
            # Load last 30 days of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            data = await self.market_data_manager.get_historical_data(
                symbol.replace("/USD", ""),
                start_date,
                end_date
            )
            
            if not data.empty:
                logger.info(f"Loaded {len(data)} candles for {symbol}")
                
    async def run(self):
        """Enhanced main trading loop"""
        self.is_running = True
        logger.info("Starting enhanced autonomous trading agent")
        
        while self.is_running:
            try:
                self.episode += 1
                episode_start = time.time()
                
                # Get enhanced market state
                market_state = await self.get_enhanced_market_state()
                
                # Detect market regime
                regime = self.regime_detector.detect_regime(market_state)
                market_state.market_regime = regime
                
                # Get DeepSeek analysis
                analysis = await self.deepseek_brain.analyze_market(
                    market_state,
                    self.portfolio
                )
                
                # Convert to RL state vector
                state_vector = self.market_state_to_enhanced_vector(market_state)
                
                # Get RL action
                rl_action = self.rl_engine.act(state_vector)
                
                # Risk check
                risk_assessment = self.risk_manager.assess_risk(
                    self.portfolio,
                    market_state
                )
                
                # Combine recommendations with risk management
                final_action = await self.combine_with_risk_management(
                    analysis,
                    rl_action,
                    market_state,
                    risk_assessment
                )
                
                # Execute trades
                if final_action and risk_assessment['allow_new_trades']:
                    reward = await self.execute_enhanced_trade(final_action)
                    
                    # Store experience
                    next_state = await self.get_enhanced_market_state()
                    next_vector = self.market_state_to_enhanced_vector(next_state)
                    
                    self.rl_engine.remember(
                        state_vector,
                        rl_action,
                        reward,
                        next_vector,
                        False
                    )
                    
                # Train RL model
                if self.episode % 10 == 0:
                    losses = []
                    for _ in range(10):  # Multiple training steps
                        loss = self.rl_engine.replay()
                        if loss:
                            losses.append(loss)
                            
                    if losses:
                        avg_loss = np.mean(losses)
                        logger.debug(f"Episode {self.episode} - Avg training loss: {avg_loss:.4f}")
                        
                # Manage positions
                await self.manage_enhanced_positions(market_state)
                
                # Performance tracking
                if self.episode % 100 == 0:
                    metrics = self.performance_tracker.get_enhanced_metrics()
                    logger.info(f"Episode {self.episode} Performance: {metrics}")
                    
                    # Save checkpoint
                    self.rl_engine.save_checkpoint(self.episode, asdict(metrics))
                    
                    # Get strategy improvements from DeepSeek
                    if metrics.total_trades > 50:
                        improvements = await self.deepseek_brain.evaluate_strategy(metrics)
                        logger.info(f"DeepSeek improvements: {improvements.get('result', '')[:200]}")
                        
                # Store market data
                await self.store_current_market_data(market_state)
                
                # Adaptive sleep based on market volatility
                sleep_time = 30 if market_state.volatility < 0.02 else 15
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(60)
                
    async def get_enhanced_market_state(self) -> EnhancedMarketState:
        """Get enhanced market state with additional features"""
        # Get basic prices (simplified for example)
        prices = {}
        volumes = {}
        rsi = {}
        macd = {}
        bollinger_bands = {}
        order_book_imbalance = {}
        
        for pair in self.trading_pairs:
            symbol = pair.replace("/USD", "")
            
            # Get recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=24)
            
            df = await self.market_data_manager.get_historical_data(symbol, start_date, end_date)
            
            if not df.empty:
                prices[symbol] = df['close'].iloc[-1]
                volumes[symbol] = df['volume'].sum()
                
                # Calculate indicators
                indicators = await self.market_data_manager.calculate_indicators(symbol, df)
                
                rsi[symbol] = indicators['rsi'].iloc[-1] if 'rsi' in indicators else 50
                macd[symbol] = {
                    'macd': indicators['macd'].iloc[-1] if 'macd' in indicators else 0,
                    'signal': indicators['signal'].iloc[-1] if 'signal' in indicators else 0
                }
                bollinger_bands[symbol] = {
                    'upper': indicators['bb_upper'].iloc[-1] if 'bb_upper' in indicators else prices[symbol],
                    'middle': indicators['bb_middle'].iloc[-1] if 'bb_middle' in indicators else prices[symbol],
                    'lower': indicators['bb_lower'].iloc[-1] if 'bb_lower' in indicators else prices[symbol]
                }
            else:
                # Use random data for testing
                prices[symbol] = 2000 + np.random.randn() * 50
                volumes[symbol] = 1000000 + np.random.randn() * 100000
                rsi[symbol] = 50 + np.random.randn() * 10
                macd[symbol] = {'macd': np.random.randn(), 'signal': np.random.randn()}
                bollinger_bands[symbol] = {
                    'upper': prices[symbol] * 1.02,
                    'middle': prices[symbol],
                    'lower': prices[symbol] * 0.98
                }
                
            order_book_imbalance[symbol] = np.random.uniform(-1, 1)
            
        # Calculate correlation matrix
        price_series = pd.DataFrame(prices, index=[0])
        correlation_matrix = np.eye(len(self.trading_pairs))  # Simplified
        
        return EnhancedMarketState(
            timestamp=datetime.now(),
            prices=prices,
            volumes=volumes,
            rsi=rsi,
            macd=macd,
            bollinger_bands=bollinger_bands,
            order_book_imbalance=order_book_imbalance,
            sentiment=0.6 + np.random.randn() * 0.1,
            volatility=0.02 + abs(np.random.randn() * 0.01),
            correlation_matrix=correlation_matrix,
            market_regime='ranging'  # Will be updated by regime detector
        )
        
    def market_state_to_enhanced_vector(self, state: EnhancedMarketState) -> np.ndarray:
        """Convert enhanced market state to feature vector"""
        features = []
        
        # Price features
        for asset in ["GOLD", "SILVER", "PLATINUM", "PALLADIUM"]:
            if asset in state.prices:
                features.append(state.prices[asset] / 10000)  # Normalize
                features.append(state.volumes[asset] / 10000000)  # Normalize
                features.append(state.rsi[asset] / 100)
                
                # MACD features
                macd_data = state.macd.get(asset, {})
                features.append(np.tanh(macd_data.get('macd', 0)))  # Normalize with tanh
                features.append(np.tanh(macd_data.get('signal', 0)))
                
                # Bollinger Bands features
                bb_data = state.bollinger_bands.get(asset, {})
                price = state.prices[asset]
                features.append((price - bb_data.get('lower', price)) / (bb_data.get('upper', price) - bb_data.get('lower', price) + 1e-8))
                
                # Order book imbalance
                features.append(state.order_book_imbalance.get(asset, 0))
            else:
                features.extend([0] * 7)  # 7 features per asset
                
        # Market features
        features.append(state.sentiment)
        features.append(state.volatility * 100)
        
        # Market regime encoding (one-hot)
        regimes = ['trending', 'ranging', 'volatile']
        regime_encoding = [1 if state.market_regime == r else 0 for r in regimes]
        features.extend(regime_encoding)
        
        # Portfolio features
        features.append(self.portfolio['USD'] / 100000)  # Normalize
        features.append(len(self.portfolio['positions']) / 10)  # Normalize
        
        # Risk metrics
        total_exposure = sum(pos['amount'] * pos['current_price'] for pos in self.portfolio['positions'].values())
        features.append(total_exposure / 100000)  # Normalize
        
        # Time features (cyclical encoding)
        hour = state.timestamp.hour
        features.append(np.sin(2 * np.pi * hour / 24))
        features.append(np.cos(2 * np.pi * hour / 24))
        
        # Day of week (cyclical encoding)
        dow = state.timestamp.weekday()
        features.append(np.sin(2 * np.pi * dow / 7))
        features.append(np.cos(2 * np.pi * dow / 7))
        
        # Pad to state size
        while len(features) < self.rl_engine.state_size:
            features.append(0)
            
        return np.array(features[:self.rl_engine.state_size], dtype=np.float32)
        
    async def store_current_market_data(self, market_state: EnhancedMarketState):
        """Store current market data to F:\ drive"""
        for symbol in market_state.prices.keys():
            data = pd.DataFrame({
                'timestamp': [market_state.timestamp],
                'open': [market_state.prices[symbol]],
                'high': [market_state.prices[symbol] * 1.001],
                'low': [market_state.prices[symbol] * 0.999],
                'close': [market_state.prices[symbol]],
                'volume': [market_state.volumes[symbol]],
                'timeframe': ['1m']
            })
            
            await self.market_data_manager.store_market_data(symbol, data)
            
    async def combine_with_risk_management(
        self,
        deepseek_analysis: dict[str, Any],
        rl_action: int,
        market_state: EnhancedMarketState,
        risk_assessment: dict[str, Any]
    ) -> [TradingAction]:
        """Combine recommendations with risk management"""
        
        if not risk_assessment['allow_new_trades']:
            logger.warning(f"Risk manager blocking trades: {risk_assessment['reason']}")
            return None
            
        # Parse DeepSeek recommendation
        trading_rec = deepseek_analysis.get('trading_recommendation', {})
        ds_action = trading_rec.get('action', 'hold')
        ds_confidence = trading_rec.get('confidence', 0.5)
        ds_assets = trading_rec.get('assets', [])
        
        # Adjust confidence based on market regime
        regime_multipliers = {
            'trending': 1.2,
            'ranging': 0.8,
            'volatile': 0.6
        }
        
        adjusted_confidence = ds_confidence * regime_multipliers.get(market_state.market_regime, 1.0)
        
        # Map RL action
        rl_actions = ['buy', 'sell', 'hold']
        rl_action_str = rl_actions[rl_action]
        
        # Enhanced decision logic
        if adjusted_confidence > 0.8 and ds_action != 'hold':
            action = ds_action
            asset = ds_assets[0] if ds_assets else 'GOLD'
            confidence = adjusted_confidence
        elif rl_action_str == ds_action and adjusted_confidence > 0.6:
            action = rl_action_str
            asset = self._select_best_asset(market_state)
            confidence = (adjusted_confidence + 0.7) / 2
        else:
            # Use ensemble voting
            votes = {'buy': 0, 'sell': 0, 'hold': 0}
            
            # DeepSeek vote
            votes[ds_action] += adjusted_confidence
            
            # RL vote
            votes[rl_action_str] += 0.7
            
            # Technical indicators vote
            tech_signal = self._get_technical_signal(market_state, 'GOLD')
            votes[tech_signal] += 0.5
            
            action = max(votes, key=votes.get)
            confidence = votes[action] / sum(votes.values())
            asset = 'GOLD'
            
        if action == 'hold' or confidence < 0.6:
            return None
            
        # Risk-adjusted position sizing
        base_size = self.portfolio['USD'] * self.max_position_size
        risk_multiplier = 1.0 - risk_assessment['portfolio_risk']
        regime_size_adj = 0.8 if market_state.market_regime == 'volatile' else 1.0
        
        position_size = base_size * confidence * risk_multiplier * regime_size_adj
        
        return TradingAction(
            timestamp=datetime.now(),
            action_type=action,
            asset=asset,
            amount=position_size / market_state.prices.get(asset, 1),
            price=market_state.prices.get(asset, 0),
            confidence=confidence,
            reasoning=f"{deepseek_analysis.get('result', '')[:100]}... Risk score: {risk_assessment['portfolio_risk']:.2f}"
        )
        
    def _select_best_asset(self, market_state: EnhancedMarketState) -> str:
        """Select best asset based on technical indicators"""
        scores = {}
        
        for asset in ['GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']:
            if asset not in market_state.prices:
                continue
                
            score = 0
            
            # RSI score
            rsi = market_state.rsi.get(asset, 50)
            if 30 < rsi < 70:
                score += (70 - rsi) / 40  # Prefer oversold
                
            # Bollinger Bands score
            bb = market_state.bollinger_bands.get(asset, {})
            price = market_state.prices[asset]
            if bb:
                bb_position = (price - bb['lower']) / (bb['upper'] - bb['lower'] + 1e-8)
                score += 1 - bb_position  # Prefer near lower band
                
            # Order book score
            score += (1 + market_state.order_book_imbalance.get(asset, 0)) / 2
            
            scores[asset] = score
            
        return max(scores, key=scores.get)
        
    def _get_technical_signal(self, market_state: EnhancedMarketState, asset: str) -> str:
        """Get technical analysis signal"""
        rsi = market_state.rsi.get(asset, 50)
        macd_data = market_state.macd.get(asset, {})
        
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1
            
        # MACD signals
        if macd_data.get('macd', 0) > macd_data.get('signal', 0):
            buy_signals += 1
        else:
            sell_signals += 1
            
        if buy_signals > sell_signals:
            return 'buy'
        elif sell_signals > buy_signals:
            return 'sell'
        else:
            return 'hold'
            
    async def execute_enhanced_trade(self, action: TradingAction) -> float:
        """Execute trade with enhanced features"""
        logger.info(f"Executing: {action.action_type} {action.amount:.4f} {action.asset} @ ${action.price:.2f} (conf: {action.confidence:.2%})")
        
        # Add transaction costs
        commission_rate = 0.001  # 0.1%
        slippage_rate = 0.0005  # 0.05%
        
        effective_price = action.price * (1 + slippage_rate if action.action_type == 'buy' else 1 - slippage_rate)
        cost = action.amount * effective_price
        commission = cost * commission_rate
        
        if action.action_type == 'buy':
            total_cost = cost + commission
            
            if self.portfolio['USD'] >= total_cost:
                self.portfolio['USD'] -= total_cost
                
                if action.asset not in self.portfolio['positions']:
                    self.portfolio['positions'][action.asset] = {
                        'amount': 0,
                        'avg_price': 0,
                        'current_price': effective_price,
                        'entry_time': datetime.now(),
                        'unrealized_pnl': 0
                    }
                    
                pos = self.portfolio['positions'][action.asset]
                total_amount = pos['amount'] + action.amount
                pos['avg_price'] = (pos['avg_price'] * pos['amount'] + effective_price * action.amount) / total_amount
                pos['amount'] = total_amount
                pos['current_price'] = effective_price
                
                # Track trade
                self.performance_tracker.record_trade(action, commission=commission)
                
                # Store trade in database
                await self._store_trade_record(action, commission)
                
                return 0.01  # Small positive reward
            else:
                return -0.1  # Penalty for insufficient funds
                
        elif action.action_type == 'sell':
            if action.asset in self.portfolio['positions']:
                pos = self.portfolio['positions'][action.asset]
                
                if pos['amount'] >= action.amount:
                    # Calculate profit
                    revenue = action.amount * effective_price
                    cost_basis = action.amount * pos['avg_price']
                    gross_profit = revenue - cost_basis
                    net_profit = gross_profit - commission
                    
                    self.portfolio['USD'] += revenue - commission
                    
                    pos['amount'] -= action.amount
                    if pos['amount'] < 0.0001:  # Essentially zero
                        del self.portfolio['positions'][action.asset]
                    else:
                        # Update current price
                        pos['current_price'] = effective_price
                        
                    # Track trade
                    self.performance_tracker.record_trade(action, profit=net_profit, commission=commission)
                    
                    # Store trade in database
                    await self._store_trade_record(action, commission, net_profit)
                    
                    # Reward based on profit percentage
                    return net_profit / cost_basis if cost_basis > 0 else 0
                    
            return -0.1  # Penalty for trying to sell non-existent position
            
        return 0
        
    async def _store_trade_record(self, action: TradingAction, commission: float, profit: float = None):
        """Store trade record to F:\ drive database"""
        trade_db_path = F_DRIVE_ROOT / "trading" / "trade_history" / "trades.db"
        
        conn = sqlite3.connect(trade_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades 
            (trade_id, timestamp, symbol, side, quantity, price, commission, pnl, strategy, reasoning, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hashlib.sha256(f"{action.timestamp.isoformat()}".encode()).hexdigest()[:16],
            action.timestamp.timestamp(),
            action.asset,
            action.action_type,
            action.amount,
            action.price,
            commission,
            profit or 0,
            'deepseek_rl_ensemble',
            action.reasoning[:500],  # Truncate reasoning
            action.confidence
        ))
        
        conn.commit()
        conn.close()
        
    async def manage_enhanced_positions(self, market_state: EnhancedMarketState):
        """Enhanced position management with trailing stops"""
        positions_to_close = []
        
        for asset, position in self.portfolio['positions'].items():
            current_price = market_state.prices.get(asset, position['avg_price'])
            position['current_price'] = current_price
            
            # Update unrealized PnL
            position['unrealized_pnl'] = (current_price - position['avg_price']) * position['amount']
            pnl_percent = (current_price - position['avg_price']) / position['avg_price']
            
            # Time-based stop loss (tighten over time)
            hold_time = (datetime.now() - position['entry_time']).total_seconds() / 3600  # Hours
            dynamic_stop_loss = self.stop_loss * (1 - min(hold_time / 168, 0.5))  # Tighten up to 50% over a week
            
            # Volatility-adjusted take profit
            volatility_multiplier = 1 + market_state.volatility * 10
            dynamic_take_profit = self.take_profit * volatility_multiplier
            
            # Check dynamic stop loss
            if pnl_percent <= -dynamic_stop_loss:
                positions_to_close.append((asset, f'dynamic_stop_loss_{dynamic_stop_loss:.2%}'))
                
            # Check dynamic take profit
            elif pnl_percent >= dynamic_take_profit:
                positions_to_close.append((asset, f'dynamic_take_profit_{dynamic_take_profit:.2%}'))
                
            # Trailing stop loss for profitable positions
            elif pnl_percent > 0.05:  # 5% profit
                trailing_stop = pnl_percent - 0.03  # 3% trailing stop
                if current_price < position['avg_price'] * (1 + trailing_stop):
                    positions_to_close.append((asset, 'trailing_stop'))
                    
        # Close positions
        for asset, reason in positions_to_close:
            position = self.portfolio['positions'][asset]
            current_price = market_state.prices.get(asset, position['avg_price'])
            
            action = TradingAction(
                timestamp=datetime.now(),
                action_type='sell',
                asset=asset,
                amount=position['amount'],
                price=current_price,
                confidence=1.0,
                reasoning=f"Position closed: {reason}"
            )
            
            reward = await self.execute_enhanced_trade(action)
            logger.info(f"Closed {asset} position: {reason}, reward: {reward:.4f}")
            
    async def shutdown(self):
        """Enhanced shutdown with data persistence"""
        self.is_running = False
        
        logger.info("Shutting down enhanced trading agent...")
        
        # Close all positions
        for asset in list(self.portfolio['positions'].keys()):
            position = self.portfolio['positions'][asset]
            action = TradingAction(
                timestamp=datetime.now(),
                action_type='sell',
                asset=asset,
                amount=position['amount'],
                price=position['current_price'],
                confidence=1.0,
                reasoning="Shutdown - closing all positions"
            )
            await self.execute_enhanced_trade(action)
            
        # Save final checkpoint
        metrics = self.performance_tracker.get_enhanced_metrics()
        self.rl_engine.save_checkpoint(self.episode, asdict(metrics))
        
        # Save experience replay buffer metadata
        self.rl_engine.memory._save_metadata()
        
        # Generate final report
        await self._generate_final_report(metrics)
        
        logger.info(f"Final performance: {metrics}")
        logger.info(f"Total episodes: {self.episode}")
        logger.info(f"Experience buffer size: {self.rl_engine.memory.size}")
        
    async def _generate_final_report(self, metrics):
        """Generate comprehensive trading report"""
        report_path = F_DRIVE_ROOT / "trading" / "reports" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_episodes": self.episode,
            "performance_metrics": asdict(metrics),
            "portfolio_value": self.portfolio['USD'] + sum(
                pos['amount'] * pos['current_price'] 
                for pos in self.portfolio['positions'].values()
            ),
            "experience_buffer_size": self.rl_engine.memory.size,
            "model_epsilon": self.rl_engine.epsilon,
            "training_history": self.rl_engine.training_history[-1000:]  # Last 1000 episodes
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Final report saved to: {report_path}")

class MarketRegimeDetector:
    """Detect market regime (trending, ranging, volatile)"""
    
    def detect_regime(self, market_state: EnhancedMarketState) -> str:
        """Detect current market regime"""
        # Simplified regime detection
        volatility = market_state.volatility
        
        # Check price momentum across assets
        momentum_scores = []
        for asset in ['GOLD', 'SILVER']:
            if asset in market_state.rsi:
                rsi = market_state.rsi[asset]
                if rsi > 70 or rsi < 30:
                    momentum_scores.append(1)
                else:
                    momentum_scores.append(0)
                    
        avg_momentum = np.mean(momentum_scores) if momentum_scores else 0.5
        
        if volatility > 0.03:
            return 'volatile'
        elif avg_momentum > 0.7:
            return 'trending'
        else:
            return 'ranging'

class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, max_drawdown: float = 0.20, position_limit: int = 4, correlation_threshold: float = 0.7):
        self.max_drawdown = max_drawdown
        self.position_limit = position_limit
        self.correlation_threshold = correlation_threshold
        self.peak_portfolio_value = 100000  # Starting value
        
    def assess_risk(self, portfolio: dict[str, Any], market_state: EnhancedMarketState) -> dict[str, Any]:
        """Comprehensive risk assessment"""
        
        # Calculate current portfolio value
        portfolio_value = portfolio['USD']
        for asset, position in portfolio['positions'].items():
            current_price = market_state.prices.get(asset, position['avg_price'])
            portfolio_value += position['amount'] * current_price
            
        # Update peak value
        self.peak_portfolio_value = max(self.peak_portfolio_value, portfolio_value)
        
        # Calculate drawdown
        current_drawdown = (self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value
        
        # Position count risk
        position_count = len(portfolio['positions'])
        
        # Correlation risk (simplified)
        correlation_risk = 0
        if position_count > 1:
            # In practice, calculate actual correlations
            correlation_risk = min(position_count / self.position_limit, 1.0) * 0.5
            
        # Overall portfolio risk score (0-1)
        portfolio_risk = (
            current_drawdown / self.max_drawdown * 0.4 +
            position_count / self.position_limit * 0.3 +
            correlation_risk * 0.3
        )
        
        # Determine if new trades are allowed
        allow_new_trades = (
            current_drawdown < self.max_drawdown * 0.8 and
            position_count < self.position_limit and
            portfolio_risk < 0.8
        )
        
        return {
            'portfolio_value': portfolio_value,
            'current_drawdown': current_drawdown,
            'position_count': position_count,
            'portfolio_risk': portfolio_risk,
            'allow_new_trades': allow_new_trades,
            'reason': self._get_risk_reason(current_drawdown, position_count, portfolio_risk)
        }
        
    def _get_risk_reason(self, drawdown: float, positions: int, risk_score: float) -> str:
        """Get human-readable risk reason"""
        reasons = []
        
        if drawdown > self.max_drawdown * 0.8:
            reasons.append(f"High drawdown: {drawdown:.1%}")
        if positions >= self.position_limit:
            reasons.append(f"Position limit reached: {positions}")
        if risk_score > 0.8:
            reasons.append(f"High risk score: {risk_score:.2f}")
            
        return "; ".join(reasons) if reasons else "Risk within limits"

class EnhancedPerformanceTracker:
    """Enhanced performance tracking with F:\ drive storage"""
    
    def __init__(self):
        self.trades_db_path = F_DRIVE_ROOT / "trading" / "trade_history" / "trades.db"
        self.metrics_db_path = F_DRIVE_ROOT / "trading" / "metrics" / "performance.db"
        
        # Ensure directories exist
        self.trades_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_databases()
        
    def _init_databases(self):
        """Initialize performance tracking databases"""
        # Trades database
        conn = sqlite3.connect(self.trades_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                timestamp REAL,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                price REAL,
                commission REAL,
                pnl REAL,
                strategy TEXT,
                reasoning TEXT,
                confidence REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Metrics database
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_performance (
                date TEXT PRIMARY KEY,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_pnl REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                portfolio_value REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
    def record_trade(self, action: TradingAction, profit: float = 0, commission: float = 0):
        """Record trade with enhanced tracking"""
        # Implementation handled by execute_enhanced_trade
        pass
        
    def get_enhanced_metrics(self) -> PerformanceMetrics:
        """Calculate enhanced performance metrics"""
        conn = sqlite3.connect(self.trades_db_path)
        
        # Get all trades
        df = pd.read_sql_query("""
            SELECT timestamp, symbol, side, quantity, price, commission, pnl, confidence
            FROM trades
            ORDER BY timestamp
        """, conn)
        
        conn.close()
        
        if df.empty:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
            
        # Calculate metrics
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        total_profit = df['pnl'].sum()
        
        # Calculate returns for Sharpe ratio
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        
        # Daily returns
        daily_pnl = df.groupby(df.index.date)['pnl'].sum()
        daily_returns = daily_pnl.pct_change().dropna()
        
        if len(daily_returns) > 1:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
            
        # Max drawdown
        cumulative_returns = (1 + daily_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Average trade duration
        buy_trades = df[df['side'] == 'buy'].copy()
        sell_trades = df[df['side'] == 'sell'].copy()
        
        avg_duration = 0
        if not buy_trades.empty and not sell_trades.empty:
            # Match buy and sell trades by symbol
            durations = []
            for symbol in buy_trades['symbol'].unique():
                symbol_buys = buy_trades[buy_trades['symbol'] == symbol]
                symbol_sells = sell_trades[sell_trades['symbol'] == symbol]
                
                for _, buy in symbol_buys.iterrows():
                    next_sells = symbol_sells[symbol_sells.index > buy.name]
                    if not next_sells.empty:
                        duration = (next_sells.index[0] - buy.name).total_seconds() / 3600
                        durations.append(duration)
                        
            avg_duration = np.mean(durations) if durations else 0
            
        # Store daily metrics
        self._store_daily_metrics({
            'date': datetime.now().date(),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'total_pnl': total_profit,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_value': 100000 + total_profit  # Simplified
        })
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            total_profit=total_profit,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            avg_trade_duration=avg_duration
        )
        
    def _store_daily_metrics(self, metrics: dict[str, Any]):
        """Store daily performance metrics"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_performance
            (date, total_trades, winning_trades, total_pnl, sharpe_ratio, max_drawdown, portfolio_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(metrics['date']),
            metrics['total_trades'],
            metrics['winning_trades'],
            metrics['total_pnl'],
            metrics['sharpe_ratio'],
            metrics['max_drawdown'],
            metrics['portfolio_value']
        ))
        
        conn.commit()
        conn.close()

# Import DeepSeekTradingBrain from original file
from deepseek_trading_agent import DeepSeekTradingBrain, TradingAction, PerformanceMetrics

async def main():
    """Enhanced main entry point"""
    # Ensure F:\ drive storage is configured
    if not F_DRIVE_ROOT.exists():
        logger.error(f"F:\\ drive storage not found at {F_DRIVE_ROOT}")
        logger.info("Please run: python configure_f_drive_storage.py")
        return
        
    # Create required directories
    required_dirs = [
        MODEL_PATH / "dqn_checkpoints",
        RL_DATA_PATH / "experience_replay",
        RL_DATA_PATH / "tensorboard",
        F_DRIVE_ROOT / "trading" / "reports"
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        
    logger.info(f"Using F:\\ drive storage at: {F_DRIVE_ROOT}")
    logger.info(f"Available space: {shutil.disk_usage(str(F_DRIVE_ROOT)).free / (1024**3):.2f} GB")
    
    # Initialize enhanced agent
    agent = EnhancedAutonomousTradingAgent()
    await agent.initialize()
    
    try:
        # Run enhanced trading agent
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Shutting down enhanced trading agent...")
        await agent.shutdown()

if __name__ == "__main__":
    # Check if PyTorch is available
    if not torch.cuda.is_available():
        logger.warning("CUDA not available. Using CPU for neural networks.")
    else:
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        
    asyncio.run(main())