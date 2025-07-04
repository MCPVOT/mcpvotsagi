#!/usr/bin/env python3
"""
DGM (Dynamic Gödel Machine) Trading Algorithms
==============================================
Complete implementation of self-improving trading algorithms
including DGM, RL, and other advanced techniques
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
from abc import ABC, abstractmethod
import random
import hashlib
import pickle
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DGMTradingAlgorithms")


@dataclass
class TradingStrategy:
    """Trading strategy parameters"""
    risk_tolerance: float = 0.5
    position_sizing: float = 0.05
    stop_loss: float = 0.03
    take_profit: float = 0.10
    max_positions: int = 10
    rebalance_threshold: float = 0.1
    slippage_tolerance: float = 0.01
    
    def to_tensor(self) -> torch.Tensor:
        """Convert strategy to tensor for neural network"""
        return torch.tensor([
            self.risk_tolerance,
            self.position_sizing,
            self.stop_loss,
            self.take_profit,
            self.max_positions / 100.0,  # Normalize
            self.rebalance_threshold,
            self.slippage_tolerance
        ])


@dataclass
class MarketState:
    """Current market state"""
    timestamp: datetime
    volatility: float
    trend_strength: float
    volume_profile: float
    sentiment_score: float
    correlation_matrix: Optional[np.ndarray] = None
    
    def to_tensor(self) -> torch.Tensor:
        """Convert market state to tensor"""
        base_features = torch.tensor([
            self.volatility,
            self.trend_strength,
            self.volume_profile,
            self.sentiment_score
        ])
        
        if self.correlation_matrix is not None:
            corr_features = torch.tensor(self.correlation_matrix.flatten()[:10])
            return torch.cat([base_features, corr_features])
        
        return base_features


@dataclass
class TradeSignal:
    """Trading signal with metadata"""
    action: str  # BUY, SELL, HOLD
    token: str
    confidence: float
    size: float
    reasoning: List[str]
    strategy_used: str
    expected_return: float
    risk_score: float


class DynamicGodelMachine:
    """
    Dynamic Gödel Machine implementation for self-improving trading
    Based on Schmidhuber's work on self-referential systems
    """
    
    def __init__(self, initial_strategy: TradingStrategy):
        self.current_strategy = initial_strategy
        self.proof_searcher_active = True
        self.improvement_history = []
        self.theorem_prover = TheoremProver()
        self.strategy_evaluator = StrategyEvaluator()
        self.meta_learner = MetaLearner()
        
        # Performance tracking
        self.performance_buffer = deque(maxlen=1000)
        self.current_utility = 0.0
        
        # Proof search parameters
        self.proof_search_depth = 5
        self.improvement_threshold = 1.05  # 5% improvement required
        
    async def search_for_improvement(self,
                                   market_state: MarketState,
                                   recent_performance: List[float]) -> Optional[TradingStrategy]:
        """
        Main proof search loop - looks for provable improvements
        """
        if not self.proof_searcher_active:
            return None
            
        logger.info("DGM: Starting proof search for strategy improvement")
        
        # Generate candidate improvements
        candidates = await self._generate_candidates(market_state)
        
        best_improvement = None
        best_expected_utility = self.current_utility
        
        for candidate in candidates:
            # Try to prove the improvement
            proof = await self.theorem_prover.prove_improvement(
                self.current_strategy,
                candidate,
                market_state,
                recent_performance
            )
            
            if proof and proof.is_valid:
                expected_utility = proof.expected_utility
                
                if expected_utility > best_expected_utility * self.improvement_threshold:
                    best_improvement = candidate
                    best_expected_utility = expected_utility
                    
                    logger.info(f"DGM: Found provable improvement with {expected_utility:.2f} utility")
                    
        if best_improvement:
            # Apply the improvement
            old_strategy = self.current_strategy
            self.current_strategy = best_improvement
            self.current_utility = best_expected_utility
            
            self.improvement_history.append({
                "timestamp": datetime.now(),
                "old_strategy": old_strategy,
                "new_strategy": best_improvement,
                "expected_utility": best_expected_utility,
                "market_conditions": market_state
            })
            
            logger.info("DGM: Applied strategy improvement")
            
        return best_improvement
        
    async def _generate_candidates(self, market_state: MarketState) -> List[TradingStrategy]:
        """Generate candidate strategy improvements"""
        candidates = []
        
        # Gradient-based modifications
        for param in ["risk_tolerance", "position_sizing", "stop_loss", "take_profit"]:
            for delta in [-0.1, -0.05, 0.05, 0.1]:
                new_strategy = self._modify_strategy(param, delta)
                if self._is_valid_strategy(new_strategy):
                    candidates.append(new_strategy)
                    
        # Meta-learned modifications
        ml_candidates = await self.meta_learner.suggest_improvements(
            self.current_strategy,
            market_state
        )
        candidates.extend(ml_candidates)
        
        # Random exploration
        for _ in range(5):
            random_strategy = self._random_valid_strategy()
            candidates.append(random_strategy)
            
        return candidates[:20]  # Limit candidates
        
    def _modify_strategy(self, param: str, delta: float) -> TradingStrategy:
        """Modify a single strategy parameter"""
        strategy_dict = self.current_strategy.__dict__.copy()
        if param in strategy_dict:
            strategy_dict[param] = max(0.001, min(1.0, strategy_dict[param] + delta))
        return TradingStrategy(**strategy_dict)
        
    def _is_valid_strategy(self, strategy: TradingStrategy) -> bool:
        """Check if strategy parameters are valid"""
        return (
            0 < strategy.risk_tolerance <= 1 and
            0 < strategy.position_sizing <= 0.2 and
            0 < strategy.stop_loss <= 0.5 and
            0 < strategy.take_profit <= 1.0 and
            1 <= strategy.max_positions <= 50
        )
        
    def _random_valid_strategy(self) -> TradingStrategy:
        """Generate a random valid strategy"""
        return TradingStrategy(
            risk_tolerance=random.uniform(0.1, 0.9),
            position_sizing=random.uniform(0.01, 0.15),
            stop_loss=random.uniform(0.01, 0.2),
            take_profit=random.uniform(0.05, 0.5),
            max_positions=random.randint(5, 20)
        )


class TheoremProver:
    """Proves that strategy improvements are beneficial"""
    
    def __init__(self):
        self.proof_cache = {}
        
    async def prove_improvement(self,
                              old_strategy: TradingStrategy,
                              new_strategy: TradingStrategy,
                              market_state: MarketState,
                              performance_history: List[float]) -> Optional['Proof']:
        """
        Attempt to prove that new_strategy improves upon old_strategy
        """
        # Check cache
        cache_key = self._get_cache_key(old_strategy, new_strategy, market_state)
        if cache_key in self.proof_cache:
            return self.proof_cache[cache_key]
            
        # Simulate both strategies
        old_utility = await self._estimate_utility(old_strategy, market_state, performance_history)
        new_utility = await self._estimate_utility(new_strategy, market_state, performance_history)
        
        # Statistical significance test
        if new_utility > old_utility:
            confidence = self._calculate_confidence(old_utility, new_utility, len(performance_history))
            
            if confidence > 0.95:  # 95% confidence
                proof = Proof(
                    is_valid=True,
                    expected_utility=new_utility,
                    confidence=confidence,
                    reasoning=[
                        f"Old utility: {old_utility:.4f}",
                        f"New utility: {new_utility:.4f}",
                        f"Improvement: {(new_utility/old_utility - 1)*100:.2f}%",
                        f"Confidence: {confidence*100:.1f}%"
                    ]
                )
                
                self.proof_cache[cache_key] = proof
                return proof
                
        return None
        
    async def _estimate_utility(self,
                              strategy: TradingStrategy,
                              market_state: MarketState,
                              performance_history: List[float]) -> float:
        """Estimate expected utility of a strategy"""
        # Sharpe ratio based utility
        if not performance_history:
            return 0.0
            
        returns = np.array(performance_history)
        
        # Adjust for strategy parameters
        adjusted_returns = returns * strategy.position_sizing
        adjusted_returns = np.clip(
            adjusted_returns,
            -strategy.stop_loss,
            strategy.take_profit
        )
        
        # Account for market conditions
        volatility_penalty = market_state.volatility * strategy.risk_tolerance
        
        # Calculate Sharpe ratio
        mean_return = np.mean(adjusted_returns)
        std_return = np.std(adjusted_returns) + 1e-6
        sharpe = (mean_return - 0.02) / std_return  # 2% risk-free rate
        
        # Utility combines Sharpe ratio with risk adjustments
        utility = sharpe - volatility_penalty
        
        return float(utility)
        
    def _calculate_confidence(self, old_utility: float, new_utility: float, n_samples: int) -> float:
        """Calculate statistical confidence in improvement"""
        # Simplified confidence calculation
        improvement = new_utility - old_utility
        std_error = 1.0 / np.sqrt(max(n_samples, 1))
        z_score = improvement / std_error
        
        # Convert to probability
        from scipy.stats import norm
        confidence = norm.cdf(z_score)
        
        return float(confidence)
        
    def _get_cache_key(self, old: TradingStrategy, new: TradingStrategy, market: MarketState) -> str:
        """Generate cache key for proof"""
        data = f"{old.__dict__}_{new.__dict__}_{market.volatility}_{market.trend_strength}"
        return hashlib.md5(data.encode()).hexdigest()


@dataclass
class Proof:
    """Proof of strategy improvement"""
    is_valid: bool
    expected_utility: float
    confidence: float
    reasoning: List[str]


class StrategyEvaluator:
    """Evaluates trading strategies in different market conditions"""
    
    def __init__(self):
        self.evaluation_cache = {}
        
    async def evaluate(self,
                      strategy: TradingStrategy,
                      market_conditions: List[MarketState],
                      historical_data: pd.DataFrame) -> Dict[str, float]:
        """Comprehensive strategy evaluation"""
        
        metrics = {
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "expected_return": 0.0,
            "risk_adjusted_return": 0.0
        }
        
        # Backtest the strategy
        backtest_results = await self._backtest(strategy, historical_data)
        
        # Calculate metrics
        returns = backtest_results["returns"]
        if len(returns) > 0:
            metrics["sharpe_ratio"] = self._calculate_sharpe(returns)
            metrics["max_drawdown"] = self._calculate_max_drawdown(returns)
            metrics["win_rate"] = sum(1 for r in returns if r > 0) / len(returns)
            
            profits = [r for r in returns if r > 0]
            losses = [-r for r in returns if r < 0]
            
            if losses:
                metrics["profit_factor"] = sum(profits) / sum(losses)
            else:
                metrics["profit_factor"] = float('inf') if profits else 0.0
                
            metrics["expected_return"] = np.mean(returns)
            metrics["risk_adjusted_return"] = metrics["expected_return"] / (np.std(returns) + 1e-6)
            
        return metrics
        
    async def _backtest(self,
                       strategy: TradingStrategy,
                       historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Run backtest simulation"""
        # Simplified backtest
        returns = []
        positions = []
        
        for i in range(1, len(historical_data)):
            # Generate signal based on strategy
            signal = self._generate_signal(strategy, historical_data.iloc[:i])
            
            if signal > 0:  # Buy signal
                position_size = min(strategy.position_sizing, 1.0 / strategy.max_positions)
                entry_price = historical_data.iloc[i]["close"]
                
                # Simulate position
                exit_price = historical_data.iloc[min(i+10, len(historical_data)-1)]["close"]
                return_pct = (exit_price - entry_price) / entry_price
                
                # Apply stop loss and take profit
                return_pct = max(-strategy.stop_loss, min(strategy.take_profit, return_pct))
                
                returns.append(return_pct * position_size)
                positions.append({
                    "entry": i,
                    "exit": min(i+10, len(historical_data)-1),
                    "return": return_pct
                })
                
        return {
            "returns": returns,
            "positions": positions,
            "total_return": sum(returns),
            "n_trades": len(positions)
        }
        
    def _generate_signal(self, strategy: TradingStrategy, data: pd.DataFrame) -> float:
        """Generate trading signal based on strategy"""
        if len(data) < 20:
            return 0.0
            
        # Simple momentum signal
        returns = data["close"].pct_change().dropna()
        momentum = returns.tail(10).mean()
        volatility = returns.tail(20).std()
        
        # Risk-adjusted signal
        if volatility > 0:
            signal = momentum / volatility * strategy.risk_tolerance
        else:
            signal = 0.0
            
        return np.clip(signal, -1.0, 1.0)
        
    def _calculate_sharpe(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
            
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free
        mean_excess = np.mean(excess_returns)
        std_returns = np.std(returns)
        
        if std_returns > 0:
            return mean_excess / std_returns * np.sqrt(252)  # Annualized
        return 0.0
        
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
            
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return float(np.min(drawdown))


class MetaLearner(nn.Module):
    """Neural network that learns to suggest strategy improvements"""
    
    def __init__(self, input_dim: int = 11, hidden_dim: int = 64, output_dim: int = 7):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Linear(hidden_dim, output_dim),
            nn.Tanh()  # Output in [-1, 1]
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        self.memory_buffer = deque(maxlen=10000)
        
    async def suggest_improvements(self,
                                 current_strategy: TradingStrategy,
                                 market_state: MarketState) -> List[TradingStrategy]:
        """Suggest strategy improvements using learned patterns"""
        
        # Prepare input
        strategy_tensor = current_strategy.to_tensor()
        market_tensor = market_state.to_tensor()
        
        # Pad market tensor if needed
        if market_tensor.shape[0] < 4:
            market_tensor = torch.cat([
                market_tensor,
                torch.zeros(4 - market_tensor.shape[0])
            ])
        
        input_tensor = torch.cat([strategy_tensor, market_tensor[:4]]).unsqueeze(0)
        
        # Get suggestions
        with torch.no_grad():
            adjustments = self.network(input_tensor).squeeze()
            
        # Create new strategies
        suggestions = []
        
        # Apply learned adjustments
        base_dict = current_strategy.__dict__.copy()
        
        # Small adjustments
        small_adjust = adjustments * 0.1
        base_dict["risk_tolerance"] = np.clip(
            base_dict["risk_tolerance"] + small_adjust[0].item(), 0.1, 0.9
        )
        base_dict["position_sizing"] = np.clip(
            base_dict["position_sizing"] + small_adjust[1].item() * 0.05, 0.01, 0.2
        )
        suggestions.append(TradingStrategy(**base_dict))
        
        # Medium adjustments
        medium_adjust = adjustments * 0.2
        base_dict = current_strategy.__dict__.copy()
        base_dict["stop_loss"] = np.clip(
            base_dict["stop_loss"] + medium_adjust[2].item() * 0.1, 0.01, 0.5
        )
        base_dict["take_profit"] = np.clip(
            base_dict["take_profit"] + medium_adjust[3].item() * 0.2, 0.05, 1.0
        )
        suggestions.append(TradingStrategy(**base_dict))
        
        return suggestions
        
    def learn_from_experience(self, experience: Dict[str, Any]):
        """Learn from trading experience"""
        self.memory_buffer.append(experience)
        
        if len(self.memory_buffer) >= 32:
            # Sample batch and train
            batch = random.sample(self.memory_buffer, 32)
            self._train_on_batch(batch)
            
    def _train_on_batch(self, batch: List[Dict[str, Any]]):
        """Train on a batch of experiences"""
        # Extract data
        inputs = []
        targets = []
        
        for exp in batch:
            strategy = exp["strategy"]
            market = exp["market_state"]
            improvement = exp["improvement_delta"]
            
            input_tensor = torch.cat([
                strategy.to_tensor(),
                market.to_tensor()[:4]
            ])
            
            inputs.append(input_tensor)
            targets.append(torch.tensor(improvement))
            
        inputs = torch.stack(inputs)
        targets = torch.stack(targets)
        
        # Train step
        self.optimizer.zero_grad()
        predictions = self.network(inputs)
        loss = nn.MSELoss()(predictions, targets)
        loss.backward()
        self.optimizer.step()


class ReinforcementLearningTrader:
    """RL-based trading agent using PPO"""
    
    def __init__(self, state_dim: int = 20, action_dim: int = 3):
        self.policy_net = PolicyNetwork(state_dim, action_dim)
        self.value_net = ValueNetwork(state_dim)
        self.optimizer = optim.Adam(
            list(self.policy_net.parameters()) + list(self.value_net.parameters()),
            lr=3e-4
        )
        
        self.memory = []
        self.gamma = 0.99
        self.eps_clip = 0.2
        self.k_epochs = 4
        
    async def decide(self,
                    market_state: torch.Tensor,
                    current_position: float) -> TradeSignal:
        """Make trading decision using RL policy"""
        
        with torch.no_grad():
            action_probs = self.policy_net(market_state)
            value = self.value_net(market_state)
            
        # Sample action
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample()
        
        # Convert to trade signal
        action_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
        
        return TradeSignal(
            action=action_map[action.item()],
            token="SOL",  # Default
            confidence=float(action_probs.max()),
            size=0.1,  # Default size
            reasoning=[f"RL Policy decision with {float(action_probs.max()):.2%} confidence"],
            strategy_used="PPO_RL",
            expected_return=float(value),
            risk_score=1.0 - float(action_probs.max())
        )
        
    def store_transition(self, state, action, reward, next_state, done):
        """Store experience for training"""
        self.memory.append((state, action, reward, next_state, done))
        
    async def train(self):
        """Train the RL agent using PPO"""
        if len(self.memory) < 64:
            return
            
        # Convert memory to tensors
        states = torch.stack([m[0] for m in self.memory])
        actions = torch.tensor([m[1] for m in self.memory])
        rewards = torch.tensor([m[2] for m in self.memory])
        next_states = torch.stack([m[3] for m in self.memory])
        dones = torch.tensor([m[4] for m in self.memory])
        
        # Calculate returns
        returns = self._calculate_returns(rewards, dones)
        
        # Normalize returns
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Get old action probabilities
        with torch.no_grad():
            old_probs = self.policy_net(states).gather(1, actions.unsqueeze(1))
            
        # PPO update
        for _ in range(self.k_epochs):
            # Get current action probabilities and values
            action_probs = self.policy_net(states)
            curr_probs = action_probs.gather(1, actions.unsqueeze(1))
            values = self.value_net(states).squeeze()
            
            # Calculate advantages
            advantages = returns - values.detach()
            
            # PPO loss
            ratio = curr_probs / old_probs
            surr1 = ratio * advantages.unsqueeze(1)
            surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantages.unsqueeze(1)
            
            policy_loss = -torch.min(surr1, surr2).mean()
            value_loss = nn.MSELoss()(values, returns)
            
            total_loss = policy_loss + 0.5 * value_loss
            
            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()
            
        # Clear memory
        self.memory = []
        
    def _calculate_returns(self, rewards: torch.Tensor, dones: torch.Tensor) -> torch.Tensor:
        """Calculate discounted returns"""
        returns = torch.zeros_like(rewards)
        running_return = 0
        
        for t in reversed(range(len(rewards))):
            running_return = rewards[t] + self.gamma * running_return * (1 - dones[t])
            returns[t] = running_return
            
        return returns


class PolicyNetwork(nn.Module):
    """Policy network for RL agent"""
    
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class ValueNetwork(nn.Module):
    """Value network for RL agent"""
    
    def __init__(self, state_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class UnifiedTradingAlgorithmEngine:
    """Unified engine combining all trading algorithms"""
    
    def __init__(self):
        # Initialize all components
        initial_strategy = TradingStrategy()
        
        self.dgm = DynamicGodelMachine(initial_strategy)
        self.rl_trader = ReinforcementLearningTrader()
        
        # Data storage
        self.checkpoint_dir = Path("/mnt/c/Workspace/MCPVotsAGI/checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Performance tracking
        self.performance_history = deque(maxlen=10000)
        self.algorithm_weights = {
            "dgm": 0.4,
            "rl": 0.3,
            "tradingagents": 0.3
        }
        
    async def generate_trading_signal(self,
                                    market_data: Dict[str, Any],
                                    token: str = "SOL") -> TradeSignal:
        """Generate unified trading signal combining all algorithms"""
        
        # Convert market data to appropriate formats
        market_state = MarketState(
            timestamp=datetime.now(),
            volatility=market_data.get("volatility", 0.2),
            trend_strength=market_data.get("trend", 0.5),
            volume_profile=market_data.get("volume", 1.0),
            sentiment_score=market_data.get("sentiment", 0.5)
        )
        
        # Get DGM strategy
        dgm_strategy = self.dgm.current_strategy
        
        # Check for DGM improvements
        if len(self.performance_history) > 100:
            recent_perf = [p["return"] for p in list(self.performance_history)[-100:]]
            await self.dgm.search_for_improvement(market_state, recent_perf)
        
        # Get RL decision
        state_tensor = self._prepare_state_tensor(market_data)
        rl_signal = await self.rl_trader.decide(state_tensor, 0.0)
        
        # Combine signals
        combined_signal = self._combine_signals(
            dgm_strategy,
            rl_signal,
            market_state
        )
        
        return combined_signal
        
    def _prepare_state_tensor(self, market_data: Dict[str, Any]) -> torch.Tensor:
        """Prepare state tensor for RL"""
        features = []
        
        # Price features
        features.extend([
            market_data.get("price", 0),
            market_data.get("price_change_24h", 0),
            market_data.get("high_24h", 0),
            market_data.get("low_24h", 0)
        ])
        
        # Volume features
        features.extend([
            market_data.get("volume_24h", 0),
            market_data.get("volume_change_24h", 0)
        ])
        
        # Technical indicators
        features.extend([
            market_data.get("rsi", 50),
            market_data.get("macd", 0),
            market_data.get("bb_position", 0.5)
        ])
        
        # Market features
        features.extend([
            market_data.get("volatility", 0.2),
            market_data.get("trend", 0),
            market_data.get("sentiment", 0.5)
        ])
        
        # Pad to expected dimension
        while len(features) < 20:
            features.append(0.0)
            
        return torch.tensor(features[:20], dtype=torch.float32)
        
    def _combine_signals(self,
                        dgm_strategy: TradingStrategy,
                        rl_signal: TradeSignal,
                        market_state: MarketState) -> TradeSignal:
        """Combine signals from different algorithms"""
        
        # Base decision on weighted voting
        action_scores = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        # DGM contribution
        if market_state.trend_strength > 0.6 and dgm_strategy.risk_tolerance > 0.5:
            action_scores["BUY"] += self.algorithm_weights["dgm"]
        elif market_state.trend_strength < -0.6:
            action_scores["SELL"] += self.algorithm_weights["dgm"]
        else:
            action_scores["HOLD"] += self.algorithm_weights["dgm"]
            
        # RL contribution
        action_scores[rl_signal.action] += self.algorithm_weights["rl"] * rl_signal.confidence
        
        # Determine final action
        final_action = max(action_scores, key=action_scores.get)
        confidence = action_scores[final_action] / sum(self.algorithm_weights.values())
        
        # Calculate position size based on DGM strategy
        position_size = dgm_strategy.position_sizing * confidence
        
        return TradeSignal(
            action=final_action,
            token="SOL",
            confidence=confidence,
            size=position_size,
            reasoning=[
                f"DGM strategy: risk_tolerance={dgm_strategy.risk_tolerance:.2f}",
                f"RL signal: {rl_signal.action} with {rl_signal.confidence:.2%} confidence",
                f"Market trend: {market_state.trend_strength:.2f}",
                f"Combined confidence: {confidence:.2%}"
            ],
            strategy_used="Unified (DGM + RL)",
            expected_return=rl_signal.expected_return * confidence,
            risk_score=1.0 - confidence
        )
        
    async def learn_from_trade_result(self, signal: TradeSignal, actual_return: float):
        """Update algorithms based on trade results"""
        
        # Store in performance history
        self.performance_history.append({
            "signal": signal,
            "return": actual_return,
            "timestamp": datetime.now()
        })
        
        # Update RL agent
        # In production, would need proper state transitions
        reward = actual_return * 100  # Scale reward
        self.rl_trader.store_transition(
            torch.zeros(20),  # Placeholder state
            {"BUY": 2, "HOLD": 1, "SELL": 0}[signal.action],
            reward,
            torch.zeros(20),  # Placeholder next state
            False
        )
        
        # Train RL periodically
        if len(self.performance_history) % 64 == 0:
            await self.rl_trader.train()
            
    def save_checkpoint(self, name: str = "latest"):
        """Save algorithm states"""
        checkpoint = {
            "dgm_strategy": self.dgm.current_strategy,
            "dgm_history": self.dgm.improvement_history,
            "rl_policy_state": self.rl_trader.policy_net.state_dict(),
            "rl_value_state": self.rl_trader.value_net.state_dict(),
            "algorithm_weights": self.algorithm_weights,
            "timestamp": datetime.now().isoformat()
        }
        
        path = self.checkpoint_dir / f"checkpoint_{name}.pkl"
        with open(path, 'wb') as f:
            pickle.dump(checkpoint, f)
            
        logger.info(f"Saved checkpoint to {path}")
        
    def load_checkpoint(self, name: str = "latest"):
        """Load algorithm states"""
        path = self.checkpoint_dir / f"checkpoint_{name}.pkl"
        
        if path.exists():
            with open(path, 'rb') as f:
                checkpoint = pickle.load(f)
                
            self.dgm.current_strategy = checkpoint["dgm_strategy"]
            self.dgm.improvement_history = checkpoint["dgm_history"]
            self.rl_trader.policy_net.load_state_dict(checkpoint["rl_policy_state"])
            self.rl_trader.value_net.load_state_dict(checkpoint["rl_value_state"])
            self.algorithm_weights = checkpoint["algorithm_weights"]
            
            logger.info(f"Loaded checkpoint from {path}")
        else:
            logger.warning(f"No checkpoint found at {path}")


# Export main components
__all__ = [
    "DynamicGodelMachine",
    "ReinforcementLearningTrader", 
    "UnifiedTradingAlgorithmEngine",
    "TradingStrategy",
    "MarketState",
    "TradeSignal"
]