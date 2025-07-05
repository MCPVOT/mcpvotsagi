#!/usr/bin/env python3
"""
F: Drive Storage Configuration for ULTIMATE AGI SYSTEM
======================================================
Configures the 800GB F: drive for large-scale data storage including:
- RL trading data and models
- Chat memory and conversation history
- Context management and caching
- Knowledge graph persistence
- IPFS distributed storage
"""

import os
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FDriveStorageManager:
    """Manages F: drive storage for ULTIMATE AGI system"""

    def __init__(self, base_path: str = "F:/ULTIMATE_AGI_DATA"):
        self.base_path = Path(base_path)
        self.storage_config = {
            "rl_trading": {
                "path": self.base_path / "RL_TRADING",
                "max_size": "200GB",
                "description": "Reinforcement learning trading data, models, and training history"
            },
            "chat_memory": {
                "path": self.base_path / "CHAT_MEMORY",
                "max_size": "100GB",
                "description": "Conversation history, context, and chat-based learning"
            },
            "knowledge_graph": {
                "path": self.base_path / "KNOWLEDGE_GRAPH",
                "max_size": "100GB",
                "description": "Persistent knowledge graph data and backups"
            },
            "context_cache": {
                "path": self.base_path / "CONTEXT_CACHE",
                "max_size": "150GB",
                "description": "Large context management and 1M token caching"
            },
            "model_weights": {
                "path": self.base_path / "MODEL_WEIGHTS",
                "max_size": "150GB",
                "description": "AI model weights, fine-tuned models, and training checkpoints"
            },
            "ipfs_storage": {
                "path": self.base_path / "IPFS_STORAGE",
                "max_size": "100GB",
                "description": "IPFS content addressing and distributed storage"
            }
        }

    def initialize_storage(self):
        """Initialize all F: drive storage directories"""
        logger.info("🗄️ Initializing F: drive storage for ULTIMATE AGI system...")

        try:
            # Check if F: drive exists
            if not Path("F:/").exists():
                logger.error("❌ F: drive not accessible")
                return False

            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created base directory: {self.base_path}")

            # Create all storage directories
            for storage_type, config in self.storage_config.items():
                storage_path = config["path"]
                storage_path.mkdir(parents=True, exist_ok=True)

                # Create README for each directory
                readme_path = storage_path / "README.md"
                readme_content = f"""# {storage_type.upper()} Storage

**Description**: {config['description']}
**Max Size**: {config['max_size']}
**Created**: {datetime.now().isoformat()}

This directory is managed by the ULTIMATE AGI SYSTEM for {config['description']}.
"""
                readme_path.write_text(readme_content)
                logger.info(f"✅ Created storage: {storage_path}")

            # Create main config file
            config_file = self.base_path / "storage_config.json"
            with open(config_file, 'w') as f:
                json.dump({
                    "created": datetime.now().isoformat(),
                    "total_capacity": "800GB",
                    "storage_types": {k: {
                        "path": str(v["path"]),
                        "max_size": v["max_size"],
                        "description": v["description"]
                    } for k, v in self.storage_config.items()}
                }, f, indent=2)

            logger.info("✅ F: drive storage initialization complete!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize F: drive storage: {e}")
            return False

    def get_storage_stats(self):
        """Get current storage usage statistics"""
        stats = {}

        for storage_type, config in self.storage_config.items():
            storage_path = config["path"]
            if storage_path.exists():
                # Calculate directory size
                total_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())
                stats[storage_type] = {
                    "path": str(storage_path),
                    "size_bytes": total_size,
                    "size_mb": round(total_size / (1024 * 1024), 2),
                    "files_count": len(list(storage_path.rglob('*')))
                }
            else:
                stats[storage_type] = {"error": "Directory not found"}

        return stats

    def get_storage_path(self, storage_type: str) -> Path:
        """Get the path for a specific storage type"""
        if storage_type in self.storage_config:
            return self.storage_config[storage_type]["path"]
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

    def ensure_storage_available(self, storage_type: str) -> bool:
        """Ensure a specific storage type is available"""
        try:
            storage_path = self.get_storage_path(storage_type)
            storage_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to ensure storage {storage_type}: {e}")
            return False


# Global instance for easy access
f_drive_manager = FDriveStorageManager()

async def initialize_f_drive_storage():
    """Initialize F: drive storage for the AGI system"""
    return f_drive_manager.initialize_storage()

def get_f_drive_stats():
    """Get F: drive storage statistics"""
    return f_drive_manager.get_storage_stats()

def get_f_drive_path(storage_type: str):
    """Get F: drive path for specific storage type"""
    return f_drive_manager.get_storage_path(storage_type)


if __name__ == "__main__":
    # Test the storage manager
    logging.basicConfig(level=logging.INFO)

    storage_manager = FDriveStorageManager()

    if storage_manager.initialize_storage():
        print("✅ F: drive storage initialized successfully!")

        stats = storage_manager.get_storage_stats()
        print("\n📊 Storage Statistics:")
        for storage_type, data in stats.items():
            if "error" not in data:
                print(f"  {storage_type}: {data['size_mb']} MB ({data['files_count']} files)")
            else:
                print(f"  {storage_type}: {data['error']}")
    else:
        print("❌ Failed to initialize F: drive storage")
