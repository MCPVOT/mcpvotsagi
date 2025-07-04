#!/usr/bin/env python3
"""
Real RL Training Monitor
=======================
Monitors actual RL training progress from checkpoint files
"""

import json
import time
import sqlite3
from pathlib import Path
import h5py
import torch
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RLTrainingMonitor")

class RealRLTrainingMonitor:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.rl_path = self.f_drive_root / "rl_training"
        self.metrics_db = self.f_drive_root / "metrics" / "rl_metrics.db"
        
        self._init_database()
        
    def _init_database(self):
        """Initialize RL metrics database"""
        self.metrics_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rl_training_metrics (
                timestamp REAL PRIMARY KEY,
                episode INTEGER,
                total_reward REAL,
                avg_reward REAL,
                min_reward REAL,
                max_reward REAL,
                epsilon REAL,
                loss REAL,
                q_value_mean REAL,
                q_value_std REAL,
                buffer_size INTEGER,
                training_time_ms REAL,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                trades_per_episode INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        
    def read_latest_checkpoint(self):
        """Read latest RL checkpoint"""
        checkpoint_dir = self.rl_path / "checkpoints"
        if not checkpoint_dir.exists():
            return None
            
        # Find latest checkpoint
        checkpoints = list(checkpoint_dir.glob("checkpoint_*.pt"))
        if not checkpoints:
            return None
            
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        
        try:
            checkpoint = torch.load(latest_checkpoint, map_location='cpu')
            return checkpoint
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
            
    def read_experience_buffer_stats(self):
        """Read experience replay buffer statistics"""
        buffer_file = self.rl_path / "experience_replay" / "buffer.hdf5"
        
        if not buffer_file.exists():
            return {'size': 0, 'capacity': 0}
            
        try:
            with h5py.File(buffer_file, 'r') as f:
                size = f.attrs.get('size', 0)
                capacity = f.attrs.get('capacity', 10000000)
                
                # Calculate reward statistics if available
                if 'rewards' in f:
                    rewards = f['rewards'][:size]
                    return {
                        'size': size,
                        'capacity': capacity,
                        'avg_reward': float(rewards.mean()),
                        'min_reward': float(rewards.min()),
                        'max_reward': float(rewards.max())
                    }
                    
            return {'size': size, 'capacity': capacity}
            
        except Exception as e:
            logger.error(f"Failed to read buffer stats: {e}")
            return {'size': 0, 'capacity': 0}
            
    def read_tensorboard_logs(self):
        """Read latest metrics from TensorBoard logs"""
        tb_dir = self.rl_path / "tensorboard"
        
        try:
            from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
            
            # Find latest run
            runs = list(tb_dir.glob("*/events.out.tfevents.*"))
            if not runs:
                return {}
                
            latest_run = max(runs, key=lambda p: p.stat().st_mtime)
            
            # Load events
            ea = EventAccumulator(str(latest_run.parent))
            ea.Reload()
            
            metrics = {}
            
            # Extract scalar metrics
            for tag in ea.Tags()['scalars']:
                events = ea.Scalars(tag)
                if events:
                    latest = events[-1]
                    metrics[tag] = latest.value
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to read TensorBoard logs: {e}")
            return {}
            
    def calculate_trading_metrics(self):
        """Calculate trading performance metrics"""
        trades_db = self.f_drive_root / "trading" / "trades.db"
        
        if not trades_db.exists():
            return {}
            
        try:
            conn = sqlite3.connect(trades_db)
            
            # Get recent trades (last 100)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entry_price, exit_price, pnl, duration_seconds
                FROM trades
                ORDER BY exit_time DESC
                LIMIT 100
            """)
            
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return {}
                
            # Calculate metrics
            pnls = [t[2] for t in trades]
            returns = [(t[1] - t[0]) / t[0] for t in trades]
            
            win_rate = sum(1 for p in pnls if p > 0) / len(pnls)
            
            # Sharpe ratio (annualized)
            if len(returns) > 1:
                import numpy as np
                returns_array = np.array(returns)
                sharpe = np.sqrt(252) * returns_array.mean() / returns_array.std()
            else:
                sharpe = 0
                
            # Max drawdown
            cumulative = np.cumsum(pnls)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'win_rate': win_rate,
                'sharpe_ratio': sharpe,
                'max_drawdown': abs(max_drawdown),
                'total_trades': len(trades)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate trading metrics: {e}")
            return {}
            
    async def collect_and_store_metrics(self):
        """Collect all RL metrics and store them"""
        # Read checkpoint
        checkpoint = self.read_latest_checkpoint()
        
        # Read buffer stats
        buffer_stats = self.read_experience_buffer_stats()
        
        # Read TensorBoard logs
        tb_metrics = self.read_tensorboard_logs()
        
        # Calculate trading metrics
        trading_metrics = self.calculate_trading_metrics()
        
        # Combine all metrics
        metrics = {
            'timestamp': time.time(),
            'episode': 0,
            'total_reward': 0,
            'avg_reward': buffer_stats.get('avg_reward', 0),
            'min_reward': buffer_stats.get('min_reward', 0),
            'max_reward': buffer_stats.get('max_reward', 0),
            'epsilon': 1.0,
            'loss': 0,
            'q_value_mean': 0,
            'q_value_std': 0,
            'buffer_size': buffer_stats.get('size', 0),
            'training_time_ms': 0,
            'win_rate': trading_metrics.get('win_rate', 0),
            'sharpe_ratio': trading_metrics.get('sharpe_ratio', 0),
            'max_drawdown': trading_metrics.get('max_drawdown', 0),
            'trades_per_episode': trading_metrics.get('total_trades', 0)
        }
        
        # Update from checkpoint if available
        if checkpoint:
            metrics.update({
                'episode': checkpoint.get('episode', 0),
                'epsilon': checkpoint.get('epsilon', 1.0),
                'loss': checkpoint.get('loss', 0),
                'q_value_mean': checkpoint.get('q_values', {}).get('mean', 0),
                'q_value_std': checkpoint.get('q_values', {}).get('std', 0)
            })
            
        # Update from TensorBoard
        if tb_metrics:
            metrics.update({
                'total_reward': tb_metrics.get('episode_reward', 0),
                'loss': tb_metrics.get('loss', metrics['loss']),
                'training_time_ms': tb_metrics.get('training_time', 0) * 1000
            })
            
        # Store in database
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO rl_training_metrics VALUES (
                :timestamp, :episode, :total_reward, :avg_reward,
                :min_reward, :max_reward, :epsilon, :loss,
                :q_value_mean, :q_value_std, :buffer_size,
                :training_time_ms, :win_rate, :sharpe_ratio,
                :max_drawdown, :trades_per_episode
            )
        """, metrics)
        
        conn.commit()
        conn.close()
        
        # Save to JSON for quick access
        json_file = self.f_drive_root / "metrics" / "latest_rl_metrics.json"
        json_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_file, 'w') as f:
            json.dump(metrics, f, indent=2)
            
        logger.info(f"RL Metrics - Episode: {metrics['episode']}, "
                   f"Buffer: {metrics['buffer_size']:,}, "
                   f"Win Rate: {metrics['win_rate']:.2%}")
                   
        return metrics
        
    async def run_continuous_monitoring(self):
        """Run continuous RL monitoring"""
        logger.info("Starting real RL training monitoring...")
        
        while True:
            try:
                await self.collect_and_store_metrics()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"RL monitoring error: {e}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    import asyncio
    monitor = RealRLTrainingMonitor()
    asyncio.run(monitor.run_continuous_monitoring())
