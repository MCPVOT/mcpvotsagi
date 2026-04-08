#!/usr/bin/env python3
"""
Unified F: Drive Storage System for ULTIMATE AGI
===============================================
Centralizes all F: drive storage operations with cross-platform support,
automatic fallback, and intelligent caching.
"""

import os
import json
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Union
import psutil

logger = logging.getLogger(__name__)

class UnifiedFDriveStorage:
    """Unified storage manager for F: drive with automatic fallback"""
    
    def __init__(self):
        # Detect platform and set base path accordingly
        self.platform = platform.system()
        self.f_drive_available = False
        
        # Set F: drive path based on platform
        if self.platform == "Windows":
            self.f_drive_base = Path("F:/MCPVotsAGI_Data")
            self.f_drive_root = Path("F:/")
        else:  # Linux/WSL
            self.f_drive_base = Path("/mnt/f/MCPVotsAGI_Data")
            self.f_drive_root = Path("/mnt/f")
            
        # Local fallback path
        self.local_base = Path.home() / "MCPVotsAGI_Data"
        
        # Check F: drive availability
        self._check_f_drive()
        
        # Set active base path
        self.base_path = self.f_drive_base if self.f_drive_available else self.local_base
        
        # Storage categories with sizes and paths
        self.storage_config = {
            "rl_trading": {
                "size_gb": 200,
                "description": "RL trading data, models, and training history",
                "subdirs": ["experience_replay", "checkpoints", "training_data", "tensorboard"]
            },
            "market_data": {
                "size_gb": 150,
                "description": "Historical market data, prices, order books",
                "subdirs": ["price_history", "order_books", "tick_data", "indicators", "news"]
            },
            "memory_store": {
                "size_gb": 100,
                "description": "Knowledge graph, embeddings, vector DB",
                "subdirs": ["knowledge_graph", "embeddings", "vector_db", "reasoning_cache"]
            },
            "chat_memory": {
                "size_gb": 100,
                "description": "Conversation history and context",
                "subdirs": ["conversations", "context", "summaries", "user_profiles"]
            },
            "model_weights": {
                "size_gb": 150,
                "description": "AI model weights and checkpoints",
                "subdirs": ["deepseek", "claude", "gpt", "fine_tuned", "ensemble"]
            },
            "context_cache": {
                "size_gb": 50,
                "description": "1M token context management",
                "subdirs": ["active", "compressed", "archived"]
            },
            "ipfs_storage": {
                "size_gb": 100,
                "description": "IPFS distributed storage",
                "subdirs": ["blocks", "datastore", "pins", "gateway_cache"]
            },
            "security_data": {
                "size_gb": 50,
                "description": "Security logs and threat intelligence",
                "subdirs": ["threat_intel", "ioc", "audit_logs", "incidents"]
            },
            "backups": {
                "size_gb": 53,
                "description": "System backups and snapshots",
                "subdirs": ["daily", "weekly", "monthly", "snapshots"]
            }
        }
        
        # Environment variables
        self._setup_environment_variables()
        
    def _check_f_drive(self):
        """Check if F: drive is available and has sufficient space"""
        try:
            if self.f_drive_root.exists():
                disk = psutil.disk_usage(str(self.f_drive_root))
                free_gb = disk.free / (1024**3)
                
                if free_gb >= 100:  # Minimum 100GB free
                    self.f_drive_available = True
                    logger.info(f"✅ F: drive available with {free_gb:.1f}GB free")
                else:
                    logger.warning(f"⚠️ F: drive has insufficient space: {free_gb:.1f}GB")
            else:
                logger.info("ℹ️ F: drive not found, using local storage")
                
        except Exception as e:
            logger.error(f"Error checking F: drive: {e}")
            self.f_drive_available = False
            
    def _setup_environment_variables(self):
        """Set up environment variables for storage paths"""
        os.environ['MCPVOTSAGI_STORAGE_BASE'] = str(self.base_path)
        os.environ['MCPVOTSAGI_F_DRIVE_AVAILABLE'] = str(self.f_drive_available)
        
        for category in self.storage_config:
            env_var = f'MCPVOTSAGI_{category.upper()}_PATH'
            os.environ[env_var] = str(self.get_path(category))
            
    def initialize_storage(self) -> bool:
        """Initialize all storage directories"""
        try:
            logger.info(f"🗄️ Initializing storage at: {self.base_path}")
            
            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Create all category directories
            for category, config in self.storage_config.items():
                category_path = self.base_path / category
                category_path.mkdir(parents=True, exist_ok=True)
                
                # Create subdirectories
                for subdir in config.get('subdirs', []):
                    subdir_path = category_path / subdir
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    
                # Create README
                readme_path = category_path / "README.md"
                readme_content = f"""# {category.replace('_', ' ').title()}

**Description**: {config['description']}
**Allocated Space**: {config['size_gb']} GB
**Created**: {datetime.now().isoformat()}
**Location**: {category_path}

## Subdirectories:
{chr(10).join(f"- `{subdir}/`" for subdir in config.get('subdirs', []))}

This directory is managed by the ULTIMATE AGI SYSTEM.
"""
                readme_path.write_text(readme_content)
                
            # Create master configuration file
            self._save_configuration()
            
            logger.info("✅ Storage initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize storage: {e}")
            return False
            
    def _save_configuration(self):
        """Save storage configuration to JSON"""
        config_file = self.base_path / "storage_config.json"
        config_data = {
            "created": datetime.now().isoformat(),
            "platform": self.platform,
            "base_path": str(self.base_path),
            "f_drive_available": self.f_drive_available,
            "total_allocated_gb": sum(c['size_gb'] for c in self.storage_config.values()),
            "categories": {
                name: {
                    "path": str(self.base_path / name),
                    "size_gb": config['size_gb'],
                    "description": config['description'],
                    "subdirs": config.get('subdirs', [])
                }
                for name, config in self.storage_config.items()
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def get_path(self, category: str, subdir: Optional[str] = None) -> Path:
        """Get path for a storage category with optional subdirectory"""
        if category not in self.storage_config:
            raise ValueError(f"Unknown storage category: {category}")
            
        path = self.base_path / category
        if subdir:
            path = path / subdir
            
        return path
        
    def ensure_path_exists(self, category: str, subdir: Optional[str] = None) -> Path:
        """Ensure a storage path exists and return it"""
        path = self.get_path(category, subdir)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def get_storage_stats(self) -> dict:
        """Get current storage usage statistics"""
        stats = {
            "base_path": str(self.base_path),
            "f_drive_available": self.f_drive_available,
            "categories": {}
        }
        
        # Overall disk usage
        try:
            disk = psutil.disk_usage(str(self.base_path.parent))
            stats["disk_usage"] = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
        except Exception:
            stats["disk_usage"] = {"error": "Unable to get disk usage"}
            
        # Per-category stats
        for category, config in self.storage_config.items():
            category_path = self.base_path / category
            if category_path.exists():
                try:
                    # Calculate directory size
                    total_size = sum(
                        f.stat().st_size for f in category_path.rglob('*') 
                        if f.is_file()
                    )
                    file_count = len(list(category_path.rglob('*')))
                    
                    stats["categories"][category] = {
                        "path": str(category_path),
                        "allocated_gb": config['size_gb'],
                        "used_bytes": total_size,
                        "used_mb": round(total_size / (1024**2), 2),
                        "used_gb": round(total_size / (1024**3), 2),
                        "file_count": file_count,
                        "usage_percent": round((total_size / (1024**3)) / config['size_gb'] * 100, 2)
                    }
                except Exception as e:
                    stats["categories"][category] = {"error": str(e)}
            else:
                stats["categories"][category] = {"status": "not_initialized"}
                
        return stats
        
    def migrate_to_f_drive(self) -> bool:
        """Migrate data from local to F: drive if it becomes available"""
        if not self.f_drive_available:
            logger.error("F: drive not available for migration")
            return False
            
        if self.base_path == self.f_drive_base:
            logger.info("Already using F: drive")
            return True
            
        try:
            logger.info("Starting migration to F: drive...")
            
            # Copy data from local to F: drive
            import shutil
            for category in self.storage_config:
                local_path = self.local_base / category
                f_drive_path = self.f_drive_base / category
                
                if local_path.exists():
                    logger.info(f"Migrating {category}...")
                    shutil.copytree(local_path, f_drive_path, dirs_exist_ok=True)
                    
            # Update base path
            self.base_path = self.f_drive_base
            self._setup_environment_variables()
            self._save_configuration()
            
            logger.info("✅ Migration to F: drive complete!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
            
    def cleanup_old_data(self, category: str, days: int = 30) -> int:
        """Clean up old data in a category"""
        import time
        
        category_path = self.get_path(category)
        if not category_path.exists():
            return 0
            
        current_time = time.time()
        deleted_count = 0
        
        for file_path in category_path.rglob('*'):
            if file_path.is_file():
                file_age_days = (current_time - file_path.stat().st_mtime) / (24 * 3600)
                if file_age_days > days:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        pass
                        
        logger.info(f"Cleaned up {deleted_count} old files from {category}")
        return deleted_count


# Global instance
storage_manager = UnifiedFDriveStorage()

# Convenience functions
def get_storage_path(category: str, subdir: Optional[str] = None) -> Path:
    """Get storage path for a category"""
    return storage_manager.get_path(category, subdir)

def ensure_storage_path(category: str, subdir: Optional[str] = None) -> Path:
    """Ensure storage path exists"""
    return storage_manager.ensure_path_exists(category, subdir)

def get_storage_stats() -> dict:
    """Get storage statistics"""
    return storage_manager.get_storage_stats()

def initialize_storage() -> bool:
    """Initialize storage system"""
    return storage_manager.initialize_storage()


if __name__ == "__main__":
    # Test the unified storage system
    logging.basicConfig(level=logging.INFO)
    
    # Initialize storage
    if initialize_storage():
        print("\n📊 Storage Statistics:")
        stats = get_storage_stats()
        
        if "disk_usage" in stats:
            disk = stats["disk_usage"]
            if "error" not in disk:
                print(f"\n💾 Disk Usage: {disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB ({disk['percent']:.1f}%)")
                
        print("\n📁 Category Usage:")
        for category, data in stats["categories"].items():
            if "error" not in data and "status" not in data:
                print(f"  {category}: {data['used_gb']:.2f}GB / {data['allocated_gb']}GB ({data['usage_percent']:.1f}%)")