#!/usr/bin/env python3
"""
Fix Mock Data and Upgrade Dashboard
===================================
Replaces all mock/random data with real implementations
"""

import os
import shutil
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FixMockData")

class MockDataFixer:
    def __init__(self):
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        self.fixes_applied = []
        
    def fix_realtime_dashboard_prices(self):
        """Fix mock price data in the realtime dashboard"""
        dashboard_file = self.workspace / "oracle_agi_v6_realtime_dashboard.py"
        
        if not dashboard_file.exists():
            logger.error("Dashboard file not found")
            return False
            
        content = dashboard_file.read_text()
        
        # Replace mock price generation with real data fetching
        old_price_code = """                for symbol in symbols:
                    # Simulate real-time price (in production, use actual API)
                    price = 100 + np.random.randn() * 2
                    volume = np.random.randint(1000000, 5000000)
                    spread = 0.01 + np.random.random() * 0.04"""
                    
        new_price_code = """                for symbol in symbols:
                    # Fetch real price data
                    price_data = await self._fetch_real_price(symbol)
                    if not price_data:
                        continue
                        
                    price = price_data['price']
                    volume = price_data['volume']
                    spread = price_data['spread']"""
                    
        if old_price_code in content:
            content = content.replace(old_price_code, new_price_code)
            
            # Add the real price fetching method
            fetch_method = '''
    async def _fetch_real_price(self, symbol: str) -> Optional[Dict]:
        """Fetch real price data from market data API or stored data"""
        try:
            # Try to get from stored market data first
            market_data_file = self.market_data_path / "price_history" / f"{symbol}_latest.json"
            
            if market_data_file.exists():
                # Use stored data if fresh (< 1 minute old)
                if (time.time() - market_data_file.stat().st_mtime) < 60:
                    with open(market_data_file, 'r') as f:
                        return json.load(f)
                        
            # Otherwise fetch from Yahoo Finance API
            async with aiohttp.ClientSession() as session:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {
                    'interval': '1m',
                    'range': '1d',
                    'includePrePost': 'false'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data['chart']['result'][0]
                        quote = result['indicators']['quote'][0]
                        
                        # Get latest values
                        latest_idx = -1
                        while latest_idx >= -len(quote['close']) and quote['close'][latest_idx] is None:
                            latest_idx -= 1
                            
                        price_data = {
                            'symbol': symbol,
                            'price': quote['close'][latest_idx],
                            'volume': quote['volume'][latest_idx],
                            'high': quote['high'][latest_idx],
                            'low': quote['low'][latest_idx],
                            'open': quote['open'][latest_idx],
                            'spread': (quote['high'][latest_idx] - quote['low'][latest_idx]) / quote['close'][latest_idx],
                            'timestamp': result['timestamp'][latest_idx]
                        }
                        
                        # Cache the data
                        market_data_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(market_data_file, 'w') as f:
                            json.dump(price_data, f)
                            
                        return price_data
                        
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            
            # Fallback to last known price from database
            try:
                conn = sqlite3.connect(self.metrics_path / 'realtime_metrics.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT price, volume, spread "
                    "FROM realtime_prices "
                    "WHERE symbol = ? "
                    "ORDER BY timestamp DESC "
                    "LIMIT 1",
                    (symbol,)
                )
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        'symbol': symbol,
                        'price': row[0],
                        'volume': row[1],
                        'spread': row[2]
                    }
                    
            except Exception as db_error:
                logger.error(f"Database fallback failed: {db_error}")
                
        return None
'''
            # Insert the method after _collect_price_data
            insert_pos = content.find("    async def _monitor_rl_training(self):")
            if insert_pos > 0:
                content = content[:insert_pos] + fetch_method + "\n" + content[insert_pos:]
                
            dashboard_file.write_text(content)
            self.fixes_applied.append("Fixed mock price data in realtime dashboard")
            logger.info("✓ Fixed mock price data in dashboard")
            return True
            
        return False
        
    def create_real_data_collectors(self):
        """Create real data collection services"""
        
        # Create market data collector
        market_collector_content = '''#!/usr/bin/env python3
"""
Real-Time Market Data Collector
==============================
Collects real market data from multiple sources
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketDataCollector")

class RealTimeMarketDataCollector:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.market_data_path = self.f_drive_root / "market_data"
        self.market_data_path.mkdir(parents=True, exist_ok=True)
        
        # Precious metals ETFs
        self.symbols = {
            'precious_metals': ['GLD', 'SLV', 'PPLT', 'PALL'],
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
            'indices': ['^GSPC', '^DJI', '^IXIC', '^VIX']
        }
        
        # Data sources
        self.sources = {
            'yahoo': self._fetch_yahoo_data,
            'alphavantage': self._fetch_alphavantage_data,
            'cryptocompare': self._fetch_crypto_data
        }
        
    async def _fetch_yahoo_data(self, symbol: str) -> Dict:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get real-time quote
            info = ticker.info
            history = ticker.history(period="1d", interval="1m")
            
            if not history.empty:
                latest = history.iloc[-1]
                
                return {
                    'symbol': symbol,
                    'price': float(latest['Close']),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'volume': int(latest['Volume']),
                    'timestamp': history.index[-1].timestamp(),
                    'bid': info.get('bid', latest['Close']),
                    'ask': info.get('ask', latest['Close']),
                    'spread': info.get('ask', latest['Close']) - info.get('bid', latest['Close']),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'day_high': info.get('dayHigh', latest['High']),
                    'day_low': info.get('dayLow', latest['Low']),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0)
                }
                
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            
        return None
        
    async def _fetch_alphavantage_data(self, symbol: str) -> Dict:
        """Fetch data from Alpha Vantage API"""
        # Requires API key - implement if available
        api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
        if not api_key:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get('Global Quote', {})
                        
                        if quote:
                            return {
                                'symbol': symbol,
                                'price': float(quote['05. price']),
                                'open': float(quote['02. open']),
                                'high': float(quote['03. high']),
                                'low': float(quote['04. low']),
                                'volume': int(quote['06. volume']),
                                'change_percent': float(quote['10. change percent'].rstrip('%')),
                                'timestamp': time.time()
                            }
                            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            
        return None
        
    async def _fetch_crypto_data(self, symbol: str) -> Dict:
        """Fetch cryptocurrency data"""
        if not symbol.endswith('-USD'):
            return None
            
        crypto_symbol = symbol.replace('-USD', '')
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coinbase.com/v2/exchange-rates?currency={crypto_symbol}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data['data']['rates']
                        
                        return {
                            'symbol': symbol,
                            'price': float(rates['USD']),
                            'timestamp': time.time()
                        }
                        
        except Exception as e:
            logger.error(f"Crypto data error for {symbol}: {e}")
            
        return None
        
    async def collect_all_data(self):
        """Collect data for all symbols"""
        all_symbols = []
        for category, symbols in self.symbols.items():
            all_symbols.extend(symbols)
            
        results = []
        
        for symbol in all_symbols:
            # Try Yahoo Finance first
            data = await self._fetch_yahoo_data(symbol)
            
            # Fallback to other sources if needed
            if not data and symbol.endswith('-USD'):
                data = await self._fetch_crypto_data(symbol)
                
            if data:
                results.append(data)
                
                # Store individual symbol data
                symbol_file = self.market_data_path / "realtime" / f"{symbol}.json"
                symbol_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(symbol_file, 'w') as f:
                    json.dump(data, f)
                    
                logger.info(f"Collected data for {symbol}: ${data['price']:.2f}")
                
        # Store aggregated data
        if results:
            aggregate_file = self.market_data_path / "realtime" / "latest_all.json"
            with open(aggregate_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'data': results
                }, f)
                
        return results
        
    async def run_continuous_collection(self):
        """Run continuous data collection"""
        logger.info("Starting real-time market data collection...")
        
        while True:
            try:
                await self.collect_all_data()
                
                # During market hours, collect every 30 seconds
                # Outside market hours, collect every 5 minutes
                now = datetime.now()
                if 9 <= now.hour < 16 and now.weekday() < 5:  # Market hours
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(300)
                    
            except Exception as e:
                logger.error(f"Collection cycle error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    collector = RealTimeMarketDataCollector()
    asyncio.run(collector.run_continuous_collection())
'''
        
        collector_path = self.workspace / "realtime_market_data_collector.py"
        collector_path.write_text(market_collector_content)
        self.fixes_applied.append("Created real-time market data collector")
        logger.info("✓ Created real-time market data collector")
        
        # Create system metrics collector
        metrics_collector_content = '''#!/usr/bin/env python3
"""
Real System Metrics Collector
============================
Collects actual system performance metrics
"""

import asyncio
import psutil
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemMetricsCollector")

class RealSystemMetricsCollector:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.metrics_path = self.f_drive_root / "metrics"
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.metrics_path / "system_metrics.db"
        self._init_database()
        
        # Track service processes
        self.service_pids = {}
        
    def _init_database(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL PRIMARY KEY,
                cpu_percent REAL,
                cpu_per_core TEXT,
                memory_percent REAL,
                memory_available_mb REAL,
                memory_used_mb REAL,
                swap_percent REAL,
                disk_usage_percent REAL,
                disk_free_gb REAL,
                disk_read_mb REAL,
                disk_write_mb REAL,
                network_sent_mb REAL,
                network_recv_mb REAL,
                process_count INTEGER,
                thread_count INTEGER,
                handle_count INTEGER,
                gpu_percent REAL,
                gpu_memory_mb REAL,
                temperature_cpu REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_metrics (
                timestamp REAL,
                service_name TEXT,
                pid INTEGER,
                cpu_percent REAL,
                memory_mb REAL,
                threads INTEGER,
                connections INTEGER,
                status TEXT,
                uptime_seconds REAL,
                PRIMARY KEY (timestamp, service_name)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def find_service_processes(self):
        """Find MCPVotsAGI service processes"""
        services = {
            'deepseek_mcp': ['python', 'deepseek_ollama_mcp_server.py'],
            'deepseek_trading': ['python', 'deepseek_trading_agent'],
            'memory_mcp': ['python', 'memory_mcp_server.py'],
            'solana_mcp': ['python', 'solana_mcp.py'],
            'opencti_mcp': ['python', 'opencti_mcp_server.py'],
            'ollama': ['ollama', 'serve']
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] or []
                cmdline_str = ' '.join(cmdline)
                
                for service_name, patterns in services.items():
                    if all(pattern in cmdline_str for pattern in patterns):
                        self.service_pids[service_name] = proc.info['pid']
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def collect_system_metrics(self):
        """Collect system-wide metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(percpu=True)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        net_io = psutil.net_io_counters()
        
        # Process metrics
        process_count = len(psutil.pids())
        
        # GPU metrics (if available)
        gpu_percent = 0
        gpu_memory_mb = 0
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_percent = gpu_info.gpu
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_mb = mem_info.used / (1024**2)
        except:
            pass
            
        # Temperature (if available)
        temp_cpu = 0
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp_cpu = temps['coretemp'][0].current
        except:
            pass
            
        return {
            'timestamp': time.time(),
            'cpu_percent': cpu_percent,
            'cpu_per_core': json.dumps(cpu_per_core),
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024**2),
            'memory_used_mb': memory.used / (1024**2),
            'swap_percent': swap.percent,
            'disk_usage_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3),
            'disk_read_mb': disk_io.read_bytes / (1024**2),
            'disk_write_mb': disk_io.write_bytes / (1024**2),
            'network_sent_mb': net_io.bytes_sent / (1024**2),
            'network_recv_mb': net_io.bytes_recv / (1024**2),
            'process_count': process_count,
            'thread_count': sum(p.num_threads() for p in psutil.process_iter()),
            'handle_count': sum(p.num_handles() for p in psutil.process_iter() if hasattr(p, 'num_handles')),
            'gpu_percent': gpu_percent,
            'gpu_memory_mb': gpu_memory_mb,
            'temperature_cpu': temp_cpu
        }
        
    def collect_service_metrics(self):
        """Collect metrics for individual services"""
        service_metrics = []
        
        for service_name, pid in self.service_pids.items():
            try:
                proc = psutil.Process(pid)
                
                # Get process info
                with proc.oneshot():
                    cpu_percent = proc.cpu_percent()
                    memory_info = proc.memory_info()
                    connections = len(proc.connections())
                    create_time = proc.create_time()
                    
                metrics = {
                    'timestamp': time.time(),
                    'service_name': service_name,
                    'pid': pid,
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_info.rss / (1024**2),
                    'threads': proc.num_threads(),
                    'connections': connections,
                    'status': proc.status(),
                    'uptime_seconds': time.time() - create_time
                }
                
                service_metrics.append(metrics)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists
                del self.service_pids[service_name]
                
        return service_metrics
        
    async def store_metrics(self, system_metrics, service_metrics):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store system metrics
        cursor.execute("""
            INSERT INTO system_metrics VALUES (
                :timestamp, :cpu_percent, :cpu_per_core, :memory_percent,
                :memory_available_mb, :memory_used_mb, :swap_percent,
                :disk_usage_percent, :disk_free_gb, :disk_read_mb,
                :disk_write_mb, :network_sent_mb, :network_recv_mb,
                :process_count, :thread_count, :handle_count,
                :gpu_percent, :gpu_memory_mb, :temperature_cpu
            )
        """, system_metrics)
        
        # Store service metrics
        for metrics in service_metrics:
            cursor.execute("""
                INSERT INTO service_metrics VALUES (
                    :timestamp, :service_name, :pid, :cpu_percent,
                    :memory_mb, :threads, :connections, :status,
                    :uptime_seconds
                )
            """, metrics)
            
        conn.commit()
        conn.close()
        
        # Also save latest to JSON for quick access
        latest_file = self.metrics_path / "latest_metrics.json"
        with open(latest_file, 'w') as f:
            json.dump({
                'system': system_metrics,
                'services': service_metrics
            }, f)
            
    async def run_continuous_collection(self):
        """Run continuous metrics collection"""
        logger.info("Starting real system metrics collection...")
        
        while True:
            try:
                # Find service processes
                self.find_service_processes()
                
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                service_metrics = self.collect_service_metrics()
                
                # Store metrics
                await self.store_metrics(system_metrics, service_metrics)
                
                logger.info(f"Collected metrics - CPU: {system_metrics['cpu_percent']:.1f}%, "
                          f"Memory: {system_metrics['memory_percent']:.1f}%, "
                          f"Services: {len(service_metrics)}")
                
                # Collect every 10 seconds
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    collector = RealSystemMetricsCollector()
    asyncio.run(collector.run_continuous_collection())
'''
        
        metrics_path = self.workspace / "real_system_metrics_collector.py"
        metrics_path.write_text(metrics_collector_content)
        self.fixes_applied.append("Created real system metrics collector")
        logger.info("✓ Created real system metrics collector")
        
    def fix_rl_mock_data(self):
        """Fix mock RL training data"""
        rl_monitor_content = '''#!/usr/bin/env python3
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
'''
        
        rl_monitor_path = self.workspace / "real_rl_training_monitor.py"
        rl_monitor_path.write_text(rl_monitor_content)
        self.fixes_applied.append("Created real RL training monitor")
        logger.info("✓ Created real RL training monitor")
        
    def create_startup_script(self):
        """Create script to start all real data collectors"""
        startup_content = '''#!/usr/bin/env python3
"""
Start Real Data Collectors
=========================
Launches all real-time data collection services
"""

import subprocess
import time
import sys
from pathlib import Path

def start_collectors():
    """Start all data collection services"""
    print("🚀 Starting Real Data Collection Services...")
    
    collectors = [
        ("Market Data Collector", "python realtime_market_data_collector.py"),
        ("System Metrics Collector", "python real_system_metrics_collector.py"),
        ("RL Training Monitor", "python real_rl_training_monitor.py")
    ]
    
    processes = []
    
    for name, command in collectors:
        print(f"Starting {name}...")
        try:
            proc = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append((name, proc))
            print(f"✓ {name} started (PID: {proc.pid})")
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            
    print("\\n✅ All collectors started!")
    print("\\nPress Ctrl+C to stop all collectors...")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\\n⚠️ {name} has stopped!")
                    
    except KeyboardInterrupt:
        print("\\n🛑 Stopping all collectors...")
        
        for name, proc in processes:
            proc.terminate()
            proc.wait()
            print(f"✓ {name} stopped")
            
        print("\\n✅ All collectors stopped")

if __name__ == "__main__":
    start_collectors()
'''
        
        startup_path = self.workspace / "start_real_data_collectors.py"
        startup_path.write_text(startup_content)
        startup_path.chmod(0o755)
        
        self.fixes_applied.append("Created startup script for real data collectors")
        logger.info("✓ Created startup script")
        
    def create_requirements_file(self):
        """Create requirements.txt for new dependencies"""
        requirements = """# Real Data Collection Requirements
yfinance>=0.2.18
pandas>=2.0.0
numpy>=1.24.0
aiohttp>=3.8.0
aiofiles>=23.0.0
psutil>=5.9.0
h5py>=3.8.0
torch>=2.0.0
tensorboard>=2.12.0
pynvml>=11.5.0
sqlite3
"""
        
        req_path = self.workspace / "requirements_real_data.txt"
        req_path.write_text(requirements)
        
        self.fixes_applied.append("Created requirements file for real data dependencies")
        logger.info("✓ Created requirements file")
        
    def run_all_fixes(self):
        """Run all fixes"""
        print("=" * 60)
        print("  FIXING MOCK DATA AND UPGRADING DASHBOARD")
        print("=" * 60)
        print()
        
        # Apply fixes
        self.fix_realtime_dashboard_prices()
        self.create_real_data_collectors()
        self.fix_rl_mock_data()
        self.create_startup_script()
        self.create_requirements_file()
        
        print()
        print("=" * 60)
        print(f"  ✅ FIXES COMPLETE! Applied {len(self.fixes_applied)} fixes")
        print("=" * 60)
        print()
        
        print("Fixes applied:")
        for fix in self.fixes_applied:
            print(f"  • {fix}")
            
        print()
        print("Next steps:")
        print("1. Install new dependencies:")
        print("   pip install -r requirements_real_data.txt")
        print()
        print("2. Start real data collectors:")
        print("   python start_real_data_collectors.py")
        print()
        print("3. Restart the dashboard:")
        print("   python oracle_agi_v6_realtime_dashboard.py")
        print()
        print("The dashboard will now use real market data instead of mock data!")

def main():
    fixer = MockDataFixer()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()