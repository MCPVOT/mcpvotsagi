#!/usr/bin/env python3
"""
Configure F:\ Drive for MCPVotsAGI Data Infrastructure
=====================================================
Utilizes 853 GB for RL training, market data, and ecosystem storage
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StorageConfig")

class FDriveStorageManager:
    def __init__(self):
        # F:\ drive path (Windows format)
        self.f_drive = Path("F:/")
        self.mcpvotsagi_data = self.f_drive / "MCPVotsAGI_Data"
        
        # Storage allocation (853 GB total)
        self.storage_allocation = {
            "rl_training": 200,      # 200 GB for RL training data
            "market_data": 150,      # 150 GB for historical market data
            "model_checkpoints": 100, # 100 GB for model checkpoints
            "memory_store": 100,     # 100 GB for knowledge graph
            "trading_logs": 50,      # 50 GB for trading logs
            "security_data": 50,     # 50 GB for security/threat data
            "ipfs_storage": 100,     # 100 GB for IPFS distributed storage
            "backup_archive": 50,    # 50 GB for backups
            "temp_workspace": 53     # 53 GB for temporary processing
        }
        
        # Directory structure
        self.directories = {
            "rl_training": {
                "experience_replay": self.mcpvotsagi_data / "rl_training" / "experience_replay",
                "training_data": self.mcpvotsagi_data / "rl_training" / "training_data",
                "model_checkpoints": self.mcpvotsagi_data / "rl_training" / "checkpoints",
                "tensorboard_logs": self.mcpvotsagi_data / "rl_training" / "tensorboard"
            },
            "market_data": {
                "price_history": self.mcpvotsagi_data / "market_data" / "price_history",
                "order_books": self.mcpvotsagi_data / "market_data" / "order_books",
                "tick_data": self.mcpvotsagi_data / "market_data" / "tick_data",
                "indicators": self.mcpvotsagi_data / "market_data" / "indicators",
                "news_sentiment": self.mcpvotsagi_data / "market_data" / "news_sentiment"
            },
            "models": {
                "deepseek": self.mcpvotsagi_data / "models" / "deepseek",
                "trading_agents": self.mcpvotsagi_data / "models" / "trading_agents",
                "ensemble": self.mcpvotsagi_data / "models" / "ensemble",
                "fine_tuned": self.mcpvotsagi_data / "models" / "fine_tuned"
            },
            "memory": {
                "knowledge_graph": self.mcpvotsagi_data / "memory" / "knowledge_graph",
                "embeddings": self.mcpvotsagi_data / "memory" / "embeddings",
                "vector_db": self.mcpvotsagi_data / "memory" / "vector_db",
                "reasoning_cache": self.mcpvotsagi_data / "memory" / "reasoning_cache"
            },
            "trading": {
                "live_positions": self.mcpvotsagi_data / "trading" / "live_positions",
                "trade_history": self.mcpvotsagi_data / "trading" / "history",
                "performance_metrics": self.mcpvotsagi_data / "trading" / "metrics",
                "backtests": self.mcpvotsagi_data / "trading" / "backtests"
            },
            "security": {
                "threat_intel": self.mcpvotsagi_data / "security" / "threat_intel",
                "ioc_database": self.mcpvotsagi_data / "security" / "ioc",
                "audit_logs": self.mcpvotsagi_data / "security" / "audit",
                "incident_reports": self.mcpvotsagi_data / "security" / "incidents"
            },
            "ipfs": {
                "blocks": self.mcpvotsagi_data / "ipfs" / "blocks",
                "datastore": self.mcpvotsagi_data / "ipfs" / "datastore",
                "pins": self.mcpvotsagi_data / "ipfs" / "pins"
            },
            "backups": {
                "daily": self.mcpvotsagi_data / "backups" / "daily",
                "weekly": self.mcpvotsagi_data / "backups" / "weekly",
                "snapshots": self.mcpvotsagi_data / "backups" / "snapshots"
            }
        }
        
    def check_f_drive(self):
        """Check if F:\ drive exists and has sufficient space"""
        if not self.f_drive.exists():
            logger.error("F:\ drive not found!")
            return False
            
        # Get drive space (Windows specific)
        try:
            import psutil
            disk = psutil.disk_usage(str(self.f_drive))
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            
            logger.info(f"F:\ Drive Status:")
            logger.info(f"  Total: {total_gb:.2f} GB")
            logger.info(f"  Free: {free_gb:.2f} GB")
            logger.info(f"  Used: {(disk.used / (1024**3)):.2f} GB ({disk.percent}%)")
            
            if free_gb < 800:
                logger.warning(f"Only {free_gb:.2f} GB free. Recommended: 800+ GB")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            return False
            
    def create_directory_structure(self):
        """Create the complete directory structure on F:\ drive"""
        logger.info("Creating MCPVotsAGI data infrastructure on F:\\ drive...")
        
        # Create main directory
        self.mcpvotsagi_data.mkdir(exist_ok=True)
        
        # Create all subdirectories
        created_dirs = 0
        for category, paths in self.directories.items():
            for name, path in paths.items():
                path.mkdir(parents=True, exist_ok=True)
                created_dirs += 1
                
        logger.info(f"✓ Created {created_dirs} directories")
        
        # Create README files
        self._create_readme_files()
        
        # Create configuration file
        self._create_config_file()
        
    def _create_readme_files(self):
        """Create README files in each major directory"""
        readmes = {
            self.mcpvotsagi_data: """# MCPVotsAGI Data Infrastructure

This directory contains all data for the MCPVotsAGI ecosystem.
Total allocated space: 853 GB

## Directory Structure
- `rl_training/`: Reinforcement learning training data (200 GB)
- `market_data/`: Historical market data and indicators (150 GB)
- `models/`: Model checkpoints and weights (100 GB)
- `memory/`: Knowledge graph and embeddings (100 GB)
- `trading/`: Trading logs and performance data (50 GB)
- `security/`: Security and threat intelligence (50 GB)
- `ipfs/`: IPFS distributed storage (100 GB)
- `backups/`: System backups and snapshots (50 GB)
""",
            self.directories["rl_training"]["experience_replay"]: """# Experience Replay Buffer

Stores state-action-reward-next_state tuples for RL training.
- Format: Pickle files with numpy arrays
- Rotation: Oldest files deleted when space exceeds limit
- Max size: 50 GB
""",
            self.directories["market_data"]["price_history"]: """# Price History Data

Historical OHLCV data for all tracked assets.
- Format: Parquet files for efficient storage
- Timeframes: 1m, 5m, 15m, 1h, 4h, 1d
- Retention: 5 years
"""
        }
        
        for path, content in readmes.items():
            readme_path = path / "README.md"
            readme_path.write_text(content)
            
    def _create_config_file(self):
        """Create storage configuration file"""
        config = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "storage_root": str(self.mcpvotsagi_data),
            "allocation_gb": self.storage_allocation,
            "paths": {
                category: {name: str(path) for name, path in paths.items()}
                for category, paths in self.directories.items()
            },
            "settings": {
                "auto_cleanup": True,
                "cleanup_threshold_gb": 750,
                "compression_enabled": True,
                "backup_retention_days": 30,
                "rl_buffer_size_gb": 50,
                "max_model_versions": 100
            }
        }
        
        config_path = self.mcpvotsagi_data / "storage_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"✓ Created storage configuration: {config_path}")
        
    def setup_symbolic_links(self):
        """Create symbolic links from MCPVotsAGI workspace to F:\ storage"""
        workspace = Path("/mnt/c/Workspace/MCPVotsAGI")
        
        links = {
            workspace / "data": self.mcpvotsagi_data,
            workspace / "models": self.directories["models"]["trading_agents"],
            workspace / "trading_data": self.directories["trading"]["trade_history"],
            workspace / "knowledge_base": self.directories["memory"]["knowledge_graph"]
        }
        
        for link_path, target_path in links.items():
            try:
                # Remove existing link if present
                if link_path.exists() and link_path.is_symlink():
                    link_path.unlink()
                    
                # Create symbolic link (Windows mklink)
                if sys.platform == "win32":
                    import subprocess
                    cmd = f'mklink /D "{link_path}" "{target_path}"'
                    subprocess.run(cmd, shell=True, check=True)
                else:
                    link_path.symlink_to(target_path)
                    
                logger.info(f"✓ Created symlink: {link_path} -> {target_path}")
                
            except Exception as e:
                logger.warning(f"Failed to create symlink {link_path}: {e}")
                
    def initialize_databases(self):
        """Initialize SQLite databases on F:\ drive"""
        import sqlite3
        
        databases = {
            "rl_training.db": self.directories["rl_training"]["training_data"],
            "market_data.db": self.directories["market_data"]["price_history"],
            "trading_journal.db": self.directories["trading"]["trade_history"],
            "knowledge_graph.db": self.directories["memory"]["knowledge_graph"],
            "security_events.db": self.directories["security"]["audit_logs"]
        }
        
        for db_name, db_dir in databases.items():
            db_path = db_dir / db_name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create base tables based on database type
            if "rl_training" in db_name:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS training_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        start_time REAL,
                        end_time REAL,
                        total_episodes INTEGER,
                        avg_reward REAL,
                        model_version TEXT,
                        hyperparameters TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS episodes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        episode_num INTEGER,
                        total_reward REAL,
                        steps INTEGER,
                        epsilon REAL,
                        loss REAL,
                        timestamp REAL
                    )
                """)
                
            elif "market_data" in db_name:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_candles (
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
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_time ON price_candles(symbol, timestamp)")
                
            elif "trading_journal" in db_name:
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
            
            logger.info(f"✓ Initialized database: {db_path}")
            
    def create_rl_config(self):
        """Create RL training configuration that uses F:\ storage"""
        rl_config = {
            "training": {
                "data_path": str(self.directories["rl_training"]["training_data"]),
                "checkpoint_path": str(self.directories["rl_training"]["model_checkpoints"]),
                "tensorboard_path": str(self.directories["rl_training"]["tensorboard_logs"]),
                "experience_replay_path": str(self.directories["rl_training"]["experience_replay"]),
                "buffer_size": 10_000_000,  # 10M experiences
                "save_frequency": 1000,      # Save every 1000 episodes
                "checkpoint_keep": 50        # Keep last 50 checkpoints
            },
            "market_data": {
                "historical_path": str(self.directories["market_data"]["price_history"]),
                "tick_data_path": str(self.directories["market_data"]["tick_data"]),
                "indicators_path": str(self.directories["market_data"]["indicators"]),
                "download_years": 5,
                "update_frequency": "1h"
            },
            "memory": {
                "knowledge_graph_path": str(self.directories["memory"]["knowledge_graph"]),
                "embeddings_path": str(self.directories["memory"]["embeddings"]),
                "vector_db_path": str(self.directories["memory"]["vector_db"]),
                "max_embeddings": 100_000_000,  # 100M embeddings
                "embedding_dim": 768
            }
        }
        
        config_path = Path("/mnt/c/Workspace/MCPVotsAGI/f_drive_storage_config.json")
        with open(config_path, 'w') as f:
            json.dump(rl_config, f, indent=2)
            
        logger.info(f"✓ Created RL configuration: {config_path}")
        
    def setup_environment_variables(self):
        """Create environment variable setup script"""
        env_vars = f"""# MCPVotsAGI F:\\ Drive Storage Configuration
export MCPVOTSAGI_DATA_ROOT="{self.mcpvotsagi_data}"
export MCPVOTSAGI_RL_DATA="{self.directories['rl_training']['training_data']}"
export MCPVOTSAGI_MARKET_DATA="{self.directories['market_data']['price_history']}"
export MCPVOTSAGI_MODEL_PATH="{self.directories['models']['trading_agents']}"
export MCPVOTSAGI_MEMORY_PATH="{self.directories['memory']['knowledge_graph']}"
export MCPVOTSAGI_TRADING_LOGS="{self.directories['trading']['trade_history']}"
export MCPVOTSAGI_BACKUP_PATH="{self.directories['backups']['daily']}"

# Performance settings for large storage
export MCPVOTSAGI_CACHE_SIZE="10GB"
export MCPVOTSAGI_BUFFER_SIZE="1GB"
export MCPVOTSAGI_MAX_MEMORY="32GB"
"""
        
        # Windows batch file
        bat_content = env_vars.replace("export ", "set ").replace("=", "=").replace("/", "\\")
        
        env_sh_path = Path("/mnt/c/Workspace/MCPVotsAGI/set_f_drive_env.sh")
        env_bat_path = Path("/mnt/c/Workspace/MCPVotsAGI/set_f_drive_env.bat")
        
        env_sh_path.write_text(env_vars)
        env_bat_path.write_text(bat_content)
        
        logger.info("✓ Created environment variable scripts")
        
    def create_data_manager_script(self):
        """Create script to manage F:\ drive data"""
        script_content = '''#!/usr/bin/env python3
"""
F:\\ Drive Data Manager for MCPVotsAGI
"""

import os
import sys
import json
import shutil
import psutil
from pathlib import Path
from datetime import datetime, timedelta

class DataManager:
    def __init__(self):
        self.config_path = Path("f_drive_storage_config.json")
        with open(self.config_path) as f:
            self.config = json.load(f)
            
    def check_usage(self):
        """Check storage usage"""
        f_drive = Path("F:/")
        disk = psutil.disk_usage(str(f_drive))
        
        print(f"F:\\ Drive Usage:")
        print(f"  Total: {disk.total / (1024**3):.2f} GB")
        print(f"  Used: {disk.used / (1024**3):.2f} GB ({disk.percent}%)")
        print(f"  Free: {disk.free / (1024**3):.2f} GB")
        
        # Check each category
        data_root = Path("F:/MCPVotsAGI_Data")
        for category in data_root.iterdir():
            if category.is_dir():
                size = sum(f.stat().st_size for f in category.rglob("*") if f.is_file())
                print(f"  {category.name}: {size / (1024**3):.2f} GB")
                
    def cleanup_old_data(self, days=30):
        """Clean up data older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Clean old RL checkpoints
        rl_path = Path(self.config["training"]["checkpoint_path"])
        for checkpoint in rl_path.glob("*.pkl"):
            if datetime.fromtimestamp(checkpoint.stat().st_mtime) < cutoff:
                checkpoint.unlink()
                print(f"Deleted old checkpoint: {checkpoint.name}")
                
        # Clean old market data
        market_path = Path(self.config["market_data"]["historical_path"])
        for data_file in market_path.glob("*.parquet"):
            if datetime.fromtimestamp(data_file.stat().st_mtime) < cutoff:
                data_file.unlink()
                print(f"Deleted old market data: {data_file.name}")
                
    def optimize_storage(self):
        """Optimize storage by compressing old data"""
        import gzip
        
        # Compress old logs
        log_dirs = [
            Path(self.config["training"]["tensorboard_path"]),
            Path(self.config["market_data"]["indicators_path"])
        ]
        
        for log_dir in log_dirs:
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                    compressed = log_file.with_suffix(".log.gz")
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    log_file.unlink()
                    print(f"Compressed: {log_file.name}")

if __name__ == "__main__":
    dm = DataManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "usage":
            dm.check_usage()
        elif sys.argv[1] == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            dm.cleanup_old_data(days)
        elif sys.argv[1] == "optimize":
            dm.optimize_storage()
    else:
        dm.check_usage()
'''
        
        script_path = Path("/mnt/c/Workspace/MCPVotsAGI/manage_f_drive_data.py")
        script_path.write_text(script_content)
        
        logger.info(f"✓ Created data management script: {script_path}")
        
    def run_setup(self):
        """Run complete F:\ drive setup"""
        print("=" * 60)
        print("  MCPVotsAGI F:\\ Drive Storage Setup")
        print("  Configuring 853 GB for RL & Ecosystem Data")
        print("=" * 60)
        print()
        
        # Check F:\ drive
        if not self.check_f_drive():
            return False
            
        # Create directory structure
        self.create_directory_structure()
        
        # Initialize databases
        self.initialize_databases()
        
        # Create configuration files
        self.create_rl_config()
        
        # Setup environment variables
        self.setup_environment_variables()
        
        # Create management script
        self.create_data_manager_script()
        
        # Try to create symbolic links
        try:
            self.setup_symbolic_links()
        except:
            logger.warning("Symbolic links creation failed. Run as Administrator for symlinks.")
            
        print()
        print("=" * 60)
        print("✅ F:\\ Drive Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run 'set_f_drive_env.bat' to set environment variables")
        print("2. Restart MCPVotsAGI to use new storage paths")
        print("3. Use 'manage_f_drive_data.py' to monitor usage")
        print()
        print(f"Storage root: {self.mcpvotsagi_data}")
        
        return True

def main():
    manager = FDriveStorageManager()
    manager.run_setup()

if __name__ == "__main__":
    main()