#!/usr/bin/env python3
"""
DGM Trading Algorithms V2
=========================
Refactored with improved modularity, performance, and extensibility
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable, Protocol
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
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
from enum import Enum
import numba
from concurrent.futures import ThreadPoolExecutor
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DGMTradingV2")


class StrategyParameter(Enum):
    """Enumeration of strategy parameters"""
    RISK_TOLERANCE = "risk_tolerance"
    POSITION_SIZING = "position_sizing"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    MAX_POSITIONS = "max_positions"
    REBALANCE_THRESHOLD = "rebalance_threshold"
    SLIPPAGE_TOLERANCE = "slippage_tolerance"
    ENTRY_THRESHOLD = "entry_threshold"
    EXIT_THRESHOLD = "exit_threshold"
    CORRELATION_LIMIT = "correlation_limit"


@dataclass
class TradingStrategyV2:
    """Enhanced trading strategy with validation and bounds"""
    risk_tolerance: float = field(default=0.5, metadata={"min": 0.0, "max": 1.0})
    position_sizing: float = field(default=0.05, metadata={"min": 0.01, "max": 0.2})
    stop_loss: float = field(default=0.03, metadata={"min": 0.01, "max": 0.5})
    take_profit: float = field(default=0.10, metadata={"min": 0.02, "max": 1.0})
    max_positions: int = field(default=10, metadata={"min": 1, "max": 50})
    rebalance_threshold: float = field(default=0.1, metadata={"min": 0.01, "max": 0.5})
    slippage_tolerance: float = field(default=0.01, metadata={"min": 0.001, "max": 0.05})
    entry_threshold: float = field(default=0.6, metadata={"min": 0.5, "max": 0.9})
    exit_threshold: float = field(default=0.4, metadata={"min": 0.1, "max": 0.5})
    correlation_limit: float = field(default=0.7, metadata={"min": 0.3, "max": 0.9})
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        self._validate()
        
    def _validate(self):
        """Validate all parameters are within bounds"""
        for field_name, field_value in asdict(self).items():
            field_obj = self.__dataclass_fields__[field_name]
            metadata = field_obj.metadata
            
            if "min" in metadata and "max" in metadata:
                min_val = metadata["min"]
                max_val = metadata["max"]
                
                if not min_val <= field_value <= max_val:
                    raise ValueError(
                        f"{field_name} must be between {min_val} and {max_val}, got {field_value}"
                    )
                    
    def mutate(self, parameter: StrategyParameter, delta: float) -> 'TradingStrategyV2':
        """Create mutated version with bounds checking"""
        new_params = asdict(self)
        param_name = parameter.value
        
        if param_name in new_params:
            field_obj = self.__dataclass_fields__[param_name]
            metadata = field_obj.metadata
            
            # Apply mutation with bounds
            new_value = new_params[param_name] + delta
            
            if "min" in metadata and "max" in metadata:
                new_value = np.clip(new_value, metadata["min"], metadata["max"])
                
            new_params[param_name] = new_value
            
        return TradingStrategyV2(**new_params)
        
    def to_tensor(self) -> torch.Tensor:
        """Convert to normalized tensor for neural networks"""
        values = []
        
        for field_name, field_value in asdict(self).items():
            field_obj = self.__dataclass_fields__[field_name]
            metadata = field_obj.metadata
            
            # Normalize to [0, 1]
            if "min" in metadata and "max" in metadata:
                normalized = (field_value - metadata["min"]) / (metadata["max"] - metadata["min"])
                values.append(normalized)
            else:
                values.append(field_value)
                
        return torch.tensor(values, dtype=torch.float32)
        
    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> 'TradingStrategyV2':
        """Create strategy from normalized tensor"""
        values = tensor.detach().cpu().numpy()
        params = {}
        
        for i, (field_name, field_obj) in enumerate(cls.__dataclass_fields__.items()):
            metadata = field_obj.metadata
            
            if i < len(values):
                # Denormalize from [0, 1]
                if "min" in metadata and "max" in metadata:
                    denormalized = values[i] * (metadata["max"] - metadata["min"]) + metadata["min"]
                    
                    # Handle integer fields
                    if field_obj.type == int:
                        denormalized = int(round(denormalized))
                        
                    params[field_name] = denormalized
                else:
                    params[field_name] = values[i]
                    
        return cls(**params)


class ProofProtocol(Protocol):
    """Protocol for strategy improvement proofs"""
    
    @property
    def is_valid(self) -> bool: ...
    
    @property
    def expected_improvement(self) -> float: ...
    
    @property
    def confidence(self) -> float: ...
    
    @property
    def reasoning(self) -> List[str]: ...


@dataclass
class ProofV2:
    """Enhanced proof with statistical validation"""
    is_valid: bool
    expected_improvement: float
    confidence: float
    reasoning: List[str]
    statistical_significance: float = 0.0
    sample_size: int = 0
    
    def meets_threshold(self, min_confidence: float = 0.95, min_improvement: float = 0.05) -> bool:
        """Check if proof meets minimum thresholds"""
        return (self.is_valid and 
                self.confidence >= min_confidence and 
                self.expected_improvement >= min_improvement)


class ImprovedTheoremProver:
    """Enhanced theorem prover with Monte Carlo validation"""
    
    def __init__(self, 
                 simulations: int = 1000,
                 confidence_level: float = 0.95,
                 parallel_workers: int = 4):
        self.simulations = simulations
        self.confidence_level = confidence_level
        self.executor = ThreadPoolExecutor(max_workers=parallel_workers)
        self.proof_cache = {}
        
    async def prove_improvement(self,
                              old_strategy: TradingStrategyV2,
                              new_strategy: TradingStrategyV2,
                              market_conditions: pd.DataFrame,
                              historical_returns: np.ndarray) -> ProofV2:
        """Prove strategy improvement using Monte Carlo simulation"""
        
        # Generate cache key
        cache_key = self._get_cache_key(old_strategy, new_strategy, market_conditions)
        if cache_key in self.proof_cache:
            return self.proof_cache[cache_key]
            
        # Run parallel simulations
        loop = asyncio.get_event_loop()
        
        old_results = await loop.run_in_executor(
            self.executor,
            self._run_strategy_simulations,
            old_strategy,
            market_conditions,
            historical_returns
        )
        
        new_results = await loop.run_in_executor(
            self.executor,
            self._run_strategy_simulations,
            new_strategy,
            market_conditions,
            historical_returns
        )
        
        # Statistical analysis
        improvement = self._analyze_results(old_results, new_results)
        
        # Create proof
        proof = ProofV2(
            is_valid=improvement["significant"],
            expected_improvement=improvement["mean_improvement"],
            confidence=improvement["confidence"],
            reasoning=improvement["reasoning"],
            statistical_significance=improvement["p_value"],
            sample_size=self.simulations
        )
        
        # Cache result
        self.proof_cache[cache_key] = proof
        
        return proof
        
    def _run_strategy_simulations(self,
                                strategy: TradingStrategyV2,
                                market_conditions: pd.DataFrame,
                                historical_returns: np.ndarray) -> np.ndarray:
        """Run Monte Carlo simulations for a strategy"""
        results = np.zeros(self.simulations)
        
        for i in range(self.simulations):
            # Bootstrap sample from historical data
            sample_indices = np.random.choice(
                len(historical_returns),
                size=len(historical_returns),
                replace=True
            )
            
            sample_returns = historical_returns[sample_indices]
            
            # Simulate strategy performance
            portfolio_value = 1.0
            positions = 0
            
            for j, ret in enumerate(sample_returns):
                # Entry signal (simplified)
                if np.random.random() < strategy.entry_threshold:
                    if positions < strategy.max_positions:
                        position_size = min(
                            strategy.position_sizing,
                            1.0 / strategy.max_positions
                        )
                        positions += 1
                        
                        # Apply return with stop loss and take profit
                        position_return = np.clip(
                            ret * (1 - strategy.slippage_tolerance),
                            -strategy.stop_loss,
                            strategy.take_profit
                        )
                        
                        portfolio_value *= (1 + position_return * position_size)
                        
                # Exit signal
                elif np.random.random() < strategy.exit_threshold and positions > 0:
                    positions -= 1
                    
            results[i] = portfolio_value - 1.0  # Return
            
        return results
        
    def _analyze_results(self, 
                        old_results: np.ndarray,
                        new_results: np.ndarray) -> Dict[str, Any]:
        """Analyze simulation results statistically"""
        
        # Calculate improvements
        mean_old = np.mean(old_results)
        mean_new = np.mean(new_results)
        mean_improvement = (mean_new - mean_old) / (abs(mean_old) + 1e-6)
        
        # Welch's t-test for unequal variances
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(new_results, old_results, equal_var=False)
        
        # Bootstrap confidence interval
        improvements = []
        for _ in range(1000):
            sample_old = np.random.choice(old_results, size=len(old_results), replace=True)
            sample_new = np.random.choice(new_results, size=len(new_results), replace=True)
            improvements.append(np.mean(sample_new) - np.mean(sample_old))
            
        ci_lower = np.percentile(improvements, (1 - self.confidence_level) * 100 / 2)
        ci_upper = np.percentile(improvements, (1 + self.confidence_level) * 100 / 2)
        
        # Build reasoning
        reasoning = [
            f"Mean return old: {mean_old:.4f}",
            f"Mean return new: {mean_new:.4f}",
            f"Improvement: {mean_improvement:.2%}",
            f"Statistical significance: p={p_value:.4f}",
            f"Confidence interval: [{ci_lower:.4f}, {ci_upper:.4f}]"
        ]
        
        return {
            "significant": p_value < (1 - self.confidence_level) and ci_lower > 0,
            "mean_improvement": mean_improvement,
            "confidence": self.confidence_level if p_value < 0.05 else p_value,
            "p_value": p_value,
            "reasoning": reasoning
        }
        
    def _get_cache_key(self, old: TradingStrategyV2, new: TradingStrategyV2, 
                      market: pd.DataFrame) -> str:
        """Generate cache key for proof"""
        data = f"{asdict(old)}_{asdict(new)}_{market.shape}_{market.iloc[0].to_dict()}"
        return hashlib.md5(data.encode()).hexdigest()


class AdvancedMetaLearner(nn.Module):
    """Advanced meta-learner with attention mechanism"""
    
    def __init__(self, 
                 strategy_dim: int = 10,
                 market_dim: int = 20,
                 hidden_dim: int = 128,
                 num_heads: int = 4):
        super().__init__()
        
        # Input encoding
        self.strategy_encoder = nn.Sequential(
            nn.Linear(strategy_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        self.market_encoder = nn.Sequential(
            nn.Linear(market_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # Multi-head attention
        self.attention = nn.MultiheadAttention(
            hidden_dim,
            num_heads,
            dropout=0.1,
            batch_first=True
        )
        
        # Strategy improvement predictor
        self.improvement_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, strategy_dim),
            nn.Tanh()  # Output improvements in [-1, 1]
        )
        
        # Value predictor (expected improvement)
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Output in [0, 1]
        )
        
        self.optimizer = optim.AdamW(self.parameters(), lr=1e-4, weight_decay=1e-5)
        self.memory_buffer = deque(maxlen=50000)
        
    def forward(self, strategy: torch.Tensor, market: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass returning strategy improvements and expected value"""
        
        # Encode inputs
        strategy_encoded = self.strategy_encoder(strategy)
        market_encoded = self.market_encoder(market)
        
        # Combine for attention
        combined = torch.stack([strategy_encoded, market_encoded], dim=1)
        
        # Self-attention
        attended, _ = self.attention(combined, combined, combined)
        
        # Global features
        global_features = torch.cat([
            attended[:, 0, :],  # Strategy attention
            attended[:, 1, :]   # Market attention
        ], dim=-1)
        
        # Predict improvements and value
        improvements = self.improvement_head(global_features)
        value = self.value_head(global_features)
        
        return improvements, value
        
    async def suggest_improvements(self,
                                 current_strategy: TradingStrategyV2,
                                 market_conditions: Dict[str, float],
                                 top_k: int = 5) -> List[TradingStrategyV2]:
        """Suggest top-k strategy improvements"""
        
        # Prepare inputs
        strategy_tensor = current_strategy.to_tensor().unsqueeze(0)
        market_tensor = self._prepare_market_tensor(market_conditions).unsqueeze(0)
        
        # Get predictions
        with torch.no_grad():
            improvements, expected_value = self(strategy_tensor, market_tensor)
            
        # Generate candidate strategies
        candidates = []
        
        # Base improvement
        base_improved = self._apply_improvements(current_strategy, improvements[0])
        candidates.append((base_improved, expected_value.item()))
        
        # Generate variations
        for i in range(top_k - 1):
            # Add noise for diversity
            noise = torch.randn_like(improvements) * 0.1
            noisy_improvements = improvements + noise
            
            strategy = self._apply_improvements(current_strategy, noisy_improvements[0])
            candidates.append((strategy, expected_value.item() * (1 - 0.1 * i)))
            
        # Sort by expected value
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [strategy for strategy, _ in candidates[:top_k]]
        
    def _prepare_market_tensor(self, market_conditions: Dict[str, float]) -> torch.Tensor:
        """Prepare market conditions as tensor"""
        # Standard market features
        features = [
            market_conditions.get("volatility", 0.2),
            market_conditions.get("trend", 0.0),
            market_conditions.get("volume", 1.0),
            market_conditions.get("sentiment", 0.5),
            market_conditions.get("correlation", 0.5),
            market_conditions.get("momentum", 0.0),
            market_conditions.get("rsi", 50.0) / 100.0,
            market_conditions.get("macd", 0.0),
            market_conditions.get("bb_position", 0.5),
            market_conditions.get("vix", 20.0) / 100.0
        ]
        
        # Pad to expected dimension
        while len(features) < 20:
            features.append(0.0)
            
        return torch.tensor(features[:20], dtype=torch.float32)
        
    def _apply_improvements(self, 
                          strategy: TradingStrategyV2,
                          improvements: torch.Tensor) -> TradingStrategyV2:
        """Apply predicted improvements to strategy"""
        
        # Get current values as tensor
        current_tensor = strategy.to_tensor()
        
        # Apply improvements (scaled by 0.1 for stability)
        improved_tensor = current_tensor + improvements * 0.1
        
        # Ensure values stay in [0, 1] range
        improved_tensor = torch.clamp(improved_tensor, 0.0, 1.0)
        
        # Convert back to strategy
        return TradingStrategyV2.from_tensor(improved_tensor)
        
    def train_on_experience(self, experiences: List[Dict[str, Any]]):
        """Train on collected experiences"""
        
        if len(self.memory_buffer) < 1000:
            return  # Need minimum data
            
        # Sample batch
        batch_size = min(64, len(self.memory_buffer))
        batch = random.sample(self.memory_buffer, batch_size)
        
        # Prepare batch tensors
        strategies = torch.stack([exp["strategy_tensor"] for exp in batch])
        markets = torch.stack([exp["market_tensor"] for exp in batch])
        improvements = torch.stack([exp["improvement_tensor"] for exp in batch])
        values = torch.tensor([exp["actual_improvement"] for exp in batch])
        
        # Forward pass
        pred_improvements, pred_values = self(strategies, markets)
        
        # Calculate losses
        improvement_loss = F.mse_loss(pred_improvements, improvements)
        value_loss = F.mse_loss(pred_values.squeeze(), values)
        
        total_loss = improvement_loss + value_loss
        
        # Backward pass
        self.optimizer.zero_grad()
        total_loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        
        return {
            "improvement_loss": improvement_loss.item(),
            "value_loss": value_loss.item(),
            "total_loss": total_loss.item()
        }


class EnhancedDynamicGodelMachine:
    """Enhanced DGM with parallel proof search and meta-learning"""
    
    def __init__(self, 
                 initial_strategy: TradingStrategyV2,
                 max_parallel_proofs: int = 10,
                 improvement_threshold: float = 1.05):
        
        self.current_strategy = initial_strategy
        self.improvement_threshold = improvement_threshold
        self.max_parallel_proofs = max_parallel_proofs
        
        # Components
        self.theorem_prover = ImprovedTheoremProver()
        self.meta_learner = AdvancedMetaLearner()
        
        # History tracking
        self.improvement_history = deque(maxlen=1000)
        self.performance_metrics = {
            "total_improvements": 0,
            "successful_improvements": 0,
            "average_improvement": 0.0,
            "best_improvement": 0.0
        }
        
        # Proof search control
        self.proof_search_active = True
        self._search_semaphore = asyncio.Semaphore(max_parallel_proofs)
        
    async def search_for_improvement(self,
                                   market_conditions: pd.DataFrame,
                                   recent_returns: np.ndarray) -> Optional[TradingStrategyV2]:
        """Enhanced proof search with parallel evaluation"""
        
        if not self.proof_search_active:
            return None
            
        logger.info("Starting enhanced proof search")
        
        # Generate diverse candidates
        candidates = await self._generate_diverse_candidates(market_conditions)
        
        # Parallel proof evaluation
        proof_tasks = []
        async with asyncio.TaskGroup() as tg:
            for candidate in candidates[:self.max_parallel_proofs]:
                task = tg.create_task(
                    self._evaluate_candidate(candidate, market_conditions, recent_returns)
                )
                proof_tasks.append((candidate, task))
                
        # Collect results
        valid_improvements = []
        
        for candidate, task in proof_tasks:
            try:
                proof = await task
                if proof.meets_threshold(min_improvement=self.improvement_threshold - 1.0):
                    valid_improvements.append((candidate, proof))
            except Exception as e:
                logger.error(f"Proof evaluation failed: {e}")
                
        # Select best improvement
        if valid_improvements:
            best_candidate, best_proof = max(
                valid_improvements,
                key=lambda x: x[1].expected_improvement * x[1].confidence
            )
            
            # Apply improvement
            await self._apply_improvement(best_candidate, best_proof, market_conditions)
            
            return best_candidate
            
        return None
        
    async def _generate_diverse_candidates(self, 
                                         market_conditions: pd.DataFrame) -> List[TradingStrategyV2]:
        """Generate diverse candidate strategies"""
        
        candidates = []
        
        # Convert market conditions to dict
        market_dict = {
            "volatility": market_conditions["volatility"].iloc[-1] if "volatility" in market_conditions else 0.2,
            "trend": market_conditions["trend"].iloc[-1] if "trend" in market_conditions else 0.0,
            "volume": market_conditions["volume"].iloc[-1] if "volume" in market_conditions else 1.0
        }
        
        # 1. Meta-learner suggestions
        ml_candidates = await self.meta_learner.suggest_improvements(
            self.current_strategy,
            market_dict,
            top_k=5
        )
        candidates.extend(ml_candidates)
        
        # 2. Gradient-based mutations
        for param in StrategyParameter:
            for delta in [-0.2, -0.1, -0.05, 0.05, 0.1, 0.2]:
                try:
                    mutated = self.current_strategy.mutate(param, delta)
                    candidates.append(mutated)
                except ValueError:
                    continue
                    
        # 3. Random exploration
        for _ in range(5):
            random_params = {}
            for field_name, field_obj in TradingStrategyV2.__dataclass_fields__.items():
                metadata = field_obj.metadata
                if "min" in metadata and "max" in metadata:
                    if field_obj.type == int:
                        value = random.randint(metadata["min"], metadata["max"])
                    else:
                        value = random.uniform(metadata["min"], metadata["max"])
                    random_params[field_name] = value
                    
            candidates.append(TradingStrategyV2(**random_params))
            
        # 4. Crossover strategies
        if len(self.improvement_history) > 2:
            # Get two successful past strategies
            past_strategies = random.sample(
                [h["strategy"] for h in list(self.improvement_history)[-20:]],
                min(2, len(self.improvement_history))
            )
            
            if len(past_strategies) >= 2:
                # Create crossover
                crossover_params = {}
                for field_name in TradingStrategyV2.__dataclass_fields__:
                    if random.random() < 0.5:
                        crossover_params[field_name] = getattr(past_strategies[0], field_name)
                    else:
                        crossover_params[field_name] = getattr(past_strategies[1], field_name)
                        
                candidates.append(TradingStrategyV2(**crossover_params))
                
        return candidates
        
    async def _evaluate_candidate(self,
                                candidate: TradingStrategyV2,
                                market_conditions: pd.DataFrame,
                                recent_returns: np.ndarray) -> ProofV2:
        """Evaluate a candidate strategy"""
        
        async with self._search_semaphore:
            proof = await self.theorem_prover.prove_improvement(
                self.current_strategy,
                candidate,
                market_conditions,
                recent_returns
            )
            
        return proof
        
    async def _apply_improvement(self,
                               new_strategy: TradingStrategyV2,
                               proof: ProofV2,
                               market_conditions: pd.DataFrame):
        """Apply strategy improvement and update history"""
        
        old_strategy = self.current_strategy
        self.current_strategy = new_strategy
        
        # Update history
        improvement_record = {
            "timestamp": datetime.now(),
            "old_strategy": old_strategy,
            "strategy": new_strategy,
            "proof": proof,
            "market_conditions": market_conditions.iloc[-1].to_dict() if len(market_conditions) > 0 else {},
            "improvement": proof.expected_improvement
        }
        
        self.improvement_history.append(improvement_record)
        
        # Update metrics
        self.performance_metrics["total_improvements"] += 1
        self.performance_metrics["successful_improvements"] += 1
        
        improvements = [h["improvement"] for h in self.improvement_history]
        self.performance_metrics["average_improvement"] = np.mean(improvements)
        self.performance_metrics["best_improvement"] = max(improvements)
        
        # Train meta-learner
        self._update_meta_learner(old_strategy, new_strategy, market_conditions, proof)
        
        logger.info(f"Applied improvement: {proof.expected_improvement:.2%} "
                   f"(Total improvements: {self.performance_metrics['total_improvements']})")
                   
    def _update_meta_learner(self,
                           old_strategy: TradingStrategyV2,
                           new_strategy: TradingStrategyV2,
                           market_conditions: pd.DataFrame,
                           proof: ProofV2):
        """Update meta-learner with successful improvement"""
        
        # Prepare experience
        experience = {
            "strategy_tensor": old_strategy.to_tensor(),
            "market_tensor": self.meta_learner._prepare_market_tensor(
                market_conditions.iloc[-1].to_dict() if len(market_conditions) > 0 else {}
            ),
            "improvement_tensor": new_strategy.to_tensor() - old_strategy.to_tensor(),
            "actual_improvement": proof.expected_improvement
        }
        
        self.meta_learner.memory_buffer.append(experience)
        
        # Train periodically
        if len(self.meta_learner.memory_buffer) % 100 == 0:
            loss_info = self.meta_learner.train_on_experience([experience])
            if loss_info:
                logger.info(f"Meta-learner training loss: {loss_info['total_loss']:.4f}")


# Numba-optimized functions for performance
@numba.jit(nopython=True)
def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
    """Numba-optimized Sharpe ratio calculation"""
    if len(returns) == 0:
        return 0.0
        
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    mean_excess = np.mean(excess_returns)
    std_returns = np.std(returns)
    
    if std_returns > 0:
        return mean_excess / std_returns * np.sqrt(252)  # Annualized
    return 0.0


@numba.jit(nopython=True)
def calculate_max_drawdown(returns: np.ndarray) -> float:
    """Numba-optimized maximum drawdown calculation"""
    if len(returns) == 0:
        return 0.0
        
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    
    return float(np.min(drawdown))


# Export enhanced components
__all__ = [
    "TradingStrategyV2",
    "EnhancedDynamicGodelMachine",
    "AdvancedMetaLearner",
    "ImprovedTheoremProver",
    "ProofV2",
    "StrategyParameter"
]