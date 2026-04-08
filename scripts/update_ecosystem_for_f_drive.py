#!/usr/bin/env python3
"""
Update MCPVotsAGI Ecosystem for F:\ Drive Integration
====================================================
Updates all components to use F:\ drive's 853 GB storage
"""

import json
import os
import sys
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcosystemUpdater")

class EcosystemFDriveUpdater:
    def __init__(self):
        self.workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        
    def update_ecosystem_manager(self):
        """Update ecosystem_manager.py to use F:\ drive"""
        ecosystem_file = self.workspace / "ecosystem_manager.py"
        
        if not ecosystem_file.exists():
            logger.error("ecosystem_manager.py not found")
            return False
            
        # Read current content
        content = ecosystem_file.read_text()
        
        # Add F:\ drive configuration at the top
        f_drive_config = '''
# F:\\ Drive Storage Configuration
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data") if platform.system() == "Windows" else Path("/mnt/f/MCPVotsAGI_Data")
F_DRIVE_ENABLED = F_DRIVE_ROOT.exists()

if F_DRIVE_ENABLED:
    # Use F:\\ drive for large data storage
    DATA_ROOT = F_DRIVE_ROOT
    RL_DATA_PATH = DATA_ROOT / "rl_training"
    MARKET_DATA_PATH = DATA_ROOT / "market_data"
    MODEL_PATH = DATA_ROOT / "models"
    MEMORY_PATH = DATA_ROOT / "memory"
    BACKUP_PATH = DATA_ROOT / "backups"
else:
    # Fallback to local storage
    DATA_ROOT = Path(__file__).parent / "data"
    RL_DATA_PATH = DATA_ROOT / "rl_training"
    MARKET_DATA_PATH = DATA_ROOT / "market_data"
    MODEL_PATH = DATA_ROOT / "models"
    MEMORY_PATH = DATA_ROOT / "memory"
    BACKUP_PATH = DATA_ROOT / "backups"
'''
        
        # Insert after imports
        import_end = content.find('logger = logging.getLogger("EcosystemManager")')
        if import_end > 0:
            content = content[:import_end] + f_drive_config + "\n" + content[import_end:]
            
        # Update database paths
        content = content.replace(
            'self.knowledge_db = self.mcpvotsagi_path / "ecosystem_knowledge.db"',
            'self.knowledge_db = MEMORY_PATH / "ecosystem_knowledge.db" if F_DRIVE_ENABLED else self.mcpvotsagi_path / "ecosystem_knowledge.db"'
        )
        
        # Add storage info to health check
        storage_check = '''
        # Check F:\\ drive storage
        if F_DRIVE_ENABLED:
            try:
                import psutil
                disk = psutil.disk_usage(str(F_DRIVE_ROOT))
                logger.info(f"F:\\\\ Drive Storage: {disk.free / (1024**3):.2f} GB free of {disk.total / (1024**3):.2f} GB")
            except Exception:
                pass
'''
        
        # Insert in check_hardware method
        hw_check_pos = content.find('def check_hardware(self):')
        if hw_check_pos > 0:
            method_end = content.find('return HardwareStatus(', hw_check_pos)
            if method_end > 0:
                content = content[:method_end] + storage_check + "\n        " + content[method_end:]
                
        # Save updated file
        backup_file = ecosystem_file.with_suffix('.py.bak')
        shutil.copy(ecosystem_file, backup_file)
        ecosystem_file.write_text(content)
        
        logger.info("✓ Updated ecosystem_manager.py")
        return True
        
    def update_deepseek_mcp_server(self):
        """Update DeepSeek MCP server for F:\ drive"""
        deepseek_file = self.workspace / "servers" / "deepseek_ollama_mcp_server.py"
        
        if not deepseek_file.exists():
            logger.warning("deepseek_ollama_mcp_server.py not found")
            return False
            
        content = deepseek_file.read_text()
        
        # Add F:\ drive imports
        f_drive_imports = '''
# F:\\ Drive Storage
F_DRIVE_ROOT = Path("F:/MCPVotsAGI_Data") if os.name == 'nt' else Path("/mnt/f/MCPVotsAGI_Data")
F_DRIVE_ENABLED = F_DRIVE_ROOT.exists()
MEMORY_PATH = F_DRIVE_ROOT / "memory" if F_DRIVE_ENABLED else Path(".")
'''
        
        # Insert after Path import
        path_import = content.find('from pathlib import Path')
        if path_import > 0:
            import_end = content.find('\n', path_import) + 1
            content = content[:import_end] + f_drive_imports + "\n" + content[import_end:]
            
        # Update cache path
        content = content.replace(
            'self.reasoning_cache = {}',
            f'''self.reasoning_cache = {{}}
        self.cache_db_path = MEMORY_PATH / "reasoning_cache.db" if F_DRIVE_ENABLED else None
        if self.cache_db_path:
            self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)'''
        )
        
        deepseek_file.write_text(content)
        logger.info("✓ Updated DeepSeek MCP server")
        return True
        
    def update_trading_agent(self):
        """Update trading agent to use enhanced version"""
        original_agent = self.workspace / "deepseek_trading_agent.py"
        enhanced_agent = self.workspace / "deepseek_trading_agent_enhanced.py"
        
        if enhanced_agent.exists():
            # Create symlink or copy
            if sys.platform == "win32":
                # Windows - create junction
                import subprocess
                try:
                    subprocess.run(
                        f'mklink /J "{original_agent}" "{enhanced_agent}"',
                        shell=True,
                        check=True
                    )
                except Exception:
                    # Fallback to copy
                    shutil.copy(enhanced_agent, original_agent)
            else:
                # Unix - create symlink
                if original_agent.exists():
                    original_agent.unlink()
                original_agent.symlink_to(enhanced_agent)
                
            logger.info("✓ Updated trading agent to enhanced version")
            return True
        return False
        
    def create_f_drive_config(self):
        """Create F:\ drive configuration file"""
        config = {
            "f_drive": {
                "enabled": True,
                "root": str(self.f_drive_root),
                "paths": {
                    "rl_training": str(self.f_drive_root / "rl_training"),
                    "market_data": str(self.f_drive_root / "market_data"),
                    "models": str(self.f_drive_root / "models"),
                    "memory": str(self.f_drive_root / "memory"),
                    "trading": str(self.f_drive_root / "trading"),
                    "security": str(self.f_drive_root / "security"),
                    "ipfs": str(self.f_drive_root / "ipfs"),
                    "backups": str(self.f_drive_root / "backups")
                },
                "settings": {
                    "cache_size_gb": 10,
                    "buffer_size_mb": 1024,
                    "compression": "snappy",
                    "auto_cleanup": True,
                    "cleanup_threshold_gb": 700
                }
            },
            "performance": {
                "experience_replay_size": 10000000,
                "batch_size": 256,
                "checkpoint_frequency": 1000,
                "max_checkpoints": 100,
                "parallel_workers": 4
            }
        }
        
        config_path = self.workspace / "f_drive_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"✓ Created F:\\ drive configuration: {config_path}")
        return True
        
    def update_launcher(self):
        """Update launcher to check F:\ drive"""
        launcher_file = self.workspace / "launcher.py"
        
        if not launcher_file.exists():
            logger.warning("launcher.py not found")
            return False
            
        content = launcher_file.read_text()
        
        # Add F:\ drive check
        f_drive_check = '''
    def check_f_drive(self):
        """Check F:\\\\ drive availability"""
        f_drive = Path("F:/MCPVotsAGI_Data")
        if f_drive.exists():
            try:
                import psutil
                disk = psutil.disk_usage(str(f_drive))
                self.console.print(f"[green]✓[/green] F:\\\\ Drive: {disk.free / (1024**3):.2f} GB free")
                return True
            except Exception:
                pass
        self.console.print("[yellow]![/yellow] F:\\\\ Drive not available (optional)")
        return False
'''
        
        # Insert in Launcher class
        class_pos = content.find('class Launcher:')
        if class_pos > 0:
            # Find a good insertion point
            init_end = content.find('def check_dependencies(self):', class_pos)
            if init_end > 0:
                content = content[:init_end] + f_drive_check + "\n    " + content[init_end:]
                
        # Add to doctor command
        doctor_pos = content.find('def doctor(self):')
        if doctor_pos > 0:
            method_body = content.find('# Check dependencies', doctor_pos)
            if method_body > 0:
                content = content[:method_body] + "        self.check_f_drive()\n        \n        " + content[method_body:]
                
        launcher_file.write_text(content)
        logger.info("✓ Updated launcher.py")
        return True
        
    def create_performance_monitor(self):
        """Create performance monitoring script"""
        monitor_content = '''#!/usr/bin/env python3
"""
MCPVotsAGI Performance Monitor
==============================
Real-time monitoring of F:\\ drive usage and system performance
"""

import asyncio
import json
import psutil
import sqlite3
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class PerformanceMonitor:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.metrics_db = self.f_drive_root / "monitoring" / "performance.db"
        self.metrics_db.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
    def _init_database(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL PRIMARY KEY,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage_gb REAL,
                disk_free_gb REAL,
                gpu_usage REAL,
                network_mbps REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_metrics (
                timestamp REAL PRIMARY KEY,
                active_positions INTEGER,
                total_trades INTEGER,
                win_rate REAL,
                current_pnl REAL,
                portfolio_value REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
    async def collect_metrics(self):
        """Collect system and trading metrics"""
        while True:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage(str(self.f_drive_root))
                
                # GPU metrics (if available)
                gpu_usage = 0
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_usage = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                except Exception:
                    pass
                    
                # Network metrics
                net_io = psutil.net_io_counters()
                network_mbps = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
                
                # Store metrics
                conn = sqlite3.connect(self.metrics_db)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_usage_gb, disk_free_gb, gpu_usage, network_mbps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().timestamp(),
                    cpu_percent,
                    memory.percent,
                    disk.used / (1024**3),
                    disk.free / (1024**3),
                    gpu_usage,
                    network_mbps
                ))
                
                # Get trading metrics
                trading_db = self.f_drive_root / "trading" / "trade_history" / "trades.db"
                if trading_db.exists():
                    trading_conn = sqlite3.connect(trading_db)
                    
                    # Get current metrics
                    total_trades = trading_conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
                    winning_trades = trading_conn.execute("SELECT COUNT(*) FROM trades WHERE pnl > 0").fetchone()[0]
                    win_rate = winning_trades / max(total_trades, 1)
                    current_pnl = trading_conn.execute("SELECT SUM(pnl) FROM trades").fetchone()[0] or 0
                    
                    cursor.execute("""
                        INSERT INTO trading_metrics
                        (timestamp, active_positions, total_trades, win_rate, current_pnl, portfolio_value)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().timestamp(),
                        0,  # Would need to query from portfolio
                        total_trades,
                        win_rate,
                        current_pnl,
                        100000 + current_pnl  # Starting capital + PnL
                    ))
                    
                    trading_conn.close()
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                print(f"Metrics collection error: {e}")
                
            await asyncio.sleep(30)  # Collect every 30 seconds
            
    def create_dashboard(self):
        """Create real-time dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('MCPVotsAGI Performance Dashboard', fontsize=16)
        
        def animate(frame):
            # Clear axes
            for ax in [ax1, ax2, ax3, ax4]:
                ax.clear()
                
            # Get recent data
            conn = sqlite3.connect(self.metrics_db)
            
            # System metrics
            system_df = pd.read_sql_query("""
                SELECT * FROM system_metrics 
                ORDER BY timestamp DESC 
                LIMIT 100
            """, conn)
            
            if not system_df.empty:
                system_df['time'] = pd.to_datetime(system_df['timestamp'], unit='s')
                
                # CPU & Memory
                ax1.plot(system_df['time'], system_df['cpu_percent'], label='CPU %', color='blue')
                ax1.plot(system_df['time'], system_df['memory_percent'], label='Memory %', color='red')
                ax1.set_ylabel('Usage %')
                ax1.set_title('System Resources')
                ax1.legend()
                ax1.grid(True)
                
                # Disk Usage
                ax2.plot(system_df['time'], system_df['disk_free_gb'], label='Free Space', color='green')
                ax2.set_ylabel('GB')
                ax2.set_title(f'F:\\\\ Drive Storage ({system_df["disk_free_gb"].iloc[0]:.1f} GB free)')
                ax2.grid(True)
                
            # Trading metrics
            trading_df = pd.read_sql_query("""
                SELECT * FROM trading_metrics 
                ORDER BY timestamp DESC 
                LIMIT 100
            """, conn)
            
            if not trading_df.empty:
                trading_df['time'] = pd.to_datetime(trading_df['timestamp'], unit='s')
                
                # Portfolio Value
                ax3.plot(trading_df['time'], trading_df['portfolio_value'], color='gold', linewidth=2)
                ax3.set_ylabel('Portfolio Value ($)')
                ax3.set_title('Portfolio Performance')
                ax3.grid(True)
                
                # Win Rate
                ax4.bar(['Win Rate'], [trading_df['win_rate'].iloc[0] * 100], color='lightgreen')
                ax4.set_ylim(0, 100)
                ax4.set_ylabel('Percentage')
                ax4.set_title(f'Trading Stats (Total: {trading_df["total_trades"].iloc[0]} trades)')
                
            conn.close()
            
            plt.tight_layout()
            
        ani = FuncAnimation(fig, animate, interval=5000)  # Update every 5 seconds
        plt.show()
        
    async def run(self):
        """Run performance monitor"""
        # Start metrics collection
        metrics_task = asyncio.create_task(self.collect_metrics())
        
        # Show dashboard in separate thread
        import threading
        dashboard_thread = threading.Thread(target=self.create_dashboard)
        dashboard_thread.start()
        
        await metrics_task

if __name__ == "__main__":
    import pandas as pd  # Import here to avoid issues if not installed
    
    monitor = PerformanceMonitor()
    asyncio.run(monitor.run())
'''
        
        monitor_path = self.workspace / "performance_monitor.py"
        monitor_path.write_text(monitor_content)
        
        logger.info(f"✓ Created performance monitor: {monitor_path}")
        return True
        
    def create_data_pipeline(self):
        """Create data pipeline for market data collection"""
        pipeline_content = '''#!/usr/bin/env python3
"""
Market Data Pipeline for F:\\ Drive
===================================
Collects and stores market data efficiently
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataPipeline")

class MarketDataPipeline:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.market_data_path = self.f_drive_root / "market_data"
        
        # Data sources
        self.sources = {
            "yahoo": "https://query1.finance.yahoo.com/v8/finance/chart/{}",
            "alphavantage": "https://www.alphavantage.co/query",
            "cryptocompare": "https://min-api.cryptocompare.com/data/v2/histoday"
        }
        
        # Assets to track
        self.assets = {
            "precious_metals": ["GLD", "SLV", "PPLT", "PALL"],
            "crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
            "indices": ["^GSPC", "^DJI", "^IXIC"]
        }
        
    async def fetch_yahoo_data(self, symbol: str, period: str = "1mo"):
        """Fetch data from Yahoo Finance"""
        url = self.sources["yahoo"].format(symbol)
        params = {
            "range": period,
            "interval": "1h",
            "includePrePost": "false"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_yahoo_data(data, symbol)
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                
        return None
        
    def _parse_yahoo_data(self, data: dict, symbol: str) -> pd.DataFrame:
        """Parse Yahoo Finance response"""
        try:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps, unit='s'),
                "open": quotes["open"],
                "high": quotes["high"],
                "low": quotes["low"],
                "close": quotes["close"],
                "volume": quotes["volume"],
                "symbol": symbol
            })
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Failed to parse data: {e}")
            return pd.DataFrame()
            
    async def collect_all_data(self):
        """Collect data for all assets"""
        tasks = []
        
        for category, symbols in self.assets.items():
            for symbol in symbols:
                tasks.append(self.fetch_yahoo_data(symbol))
                
        results = await asyncio.gather(*tasks)
        
        # Store data
        for df in results:
            if df is not None and not df.empty:
                await self.store_market_data(df)
                
    async def store_market_data(self, df: pd.DataFrame):
        """Store market data to F:\\ drive"""
        if df.empty:
            return
            
        symbol = df['symbol'].iloc[0]
        
        # Parquet file for this month
        month_str = datetime.now().strftime("%Y%m")
        parquet_path = self.market_data_path / "price_history" / f"{symbol}_{month_str}.parquet"
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append or create
        if parquet_path.exists():
            existing_df = pd.read_parquet(parquet_path)
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['timestamp'])
            
        df.to_parquet(parquet_path, compression='snappy')
        logger.info(f"Stored {len(df)} records for {symbol}")
        
    async def run_pipeline(self):
        """Run continuous data collection"""
        while True:
            try:
                logger.info("Starting data collection cycle...")
                await self.collect_all_data()
                logger.info("Data collection complete")
                
                # Run every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

if __name__ == "__main__":
    pipeline = MarketDataPipeline()
    asyncio.run(pipeline.run_pipeline())
'''
        
        pipeline_path = self.workspace / "market_data_pipeline.py"
        pipeline_path.write_text(pipeline_content)
        
        logger.info(f"✓ Created market data pipeline: {pipeline_path}")
        return True
        
    def run_updates(self):
        """Run all updates"""
        print("=" * 60)
        print("  MCPVotsAGI F:\\ Drive Integration Updater")
        print("=" * 60)
        print()
        
        # Check F:\ drive
        if not self.f_drive_root.exists():
            logger.error(f"F:\\ drive storage not found at {self.f_drive_root}")
            logger.info("Please run: python configure_f_drive_storage.py")
            return False
            
        # Run updates
        updates = [
            ("Updating ecosystem manager", self.update_ecosystem_manager),
            ("Updating DeepSeek MCP server", self.update_deepseek_mcp_server),
            ("Updating trading agent", self.update_trading_agent),
            ("Creating F:\\ drive config", self.create_f_drive_config),
            ("Updating launcher", self.update_launcher),
            ("Creating performance monitor", self.create_performance_monitor),
            ("Creating data pipeline", self.create_data_pipeline)
        ]
        
        success_count = 0
        for description, update_func in updates:
            logger.info(f"\n{description}...")
            try:
                if update_func():
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed: {e}")
                
        print()
        print("=" * 60)
        print(f"✅ Updates complete! {success_count}/{len(updates)} successful")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart MCPVotsAGI ecosystem: python launcher.py quickstart")
        print("2. Monitor performance: python performance_monitor.py")
        print("3. Start data pipeline: python market_data_pipeline.py")
        print()
        print("F:\\ drive integration is now active!")
        
        return True

def main():
    updater = EcosystemFDriveUpdater()
    updater.run_updates()

if __name__ == "__main__":
    main()