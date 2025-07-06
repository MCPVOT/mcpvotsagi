#!/usr/bin/env python3
"""
Configure MCP Memory Server for Claude CLI
==========================================
Sets up the same memory context that VS Code is using
"""

import os
import json
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Config")

class MCPMemoryConfigurator:
    def __init__(self):
        self.workspace_path = Path("C:/Workspace/MCPVotsAGI")
        self.data_path = self.workspace_path / "data"
        self.memory_db_path = self.data_path / "agi_memory.db"
        self.f_drive_memory = Path("F:/MCPVotsAGI_Data/memory_store")
        
    def setup_memory_database(self):
        """Initialize SQLite memory database if it doesn't exist"""
        logger.info(f"Setting up memory database at: {self.memory_db_path}")
        
        # Create data directory if it doesn't exist
        self.data_path.mkdir(exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect(str(self.memory_db_path))
        cursor = conn.cursor()
        
        # Create memory tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add some initial memories
        initial_memories = [
            ("system_name", "ULTIMATE AGI SYSTEM V3", "system"),
            ("version", "3.0.0-PRODUCTION", "system"),
            ("f_drive_path", "F:/MCPVotsAGI_Data", "config"),
            ("storage_capacity", "853GB", "config"),
            ("primary_model", "DeepSeek-R1", "model"),
            ("context_window", "1000000", "model")
        ]
        
        for key, value, category in initial_memories:
            cursor.execute("""
                INSERT OR IGNORE INTO memories (key, value, category)
                VALUES (?, ?, ?)
            """, (key, value, category))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Memory database initialized")
        
    def create_mcp_config(self):
        """Create MCP configuration for Claude CLI"""
        # Windows paths for Claude configuration
        claude_paths = [
            Path(os.environ.get('APPDATA', '')) / 'Claude',
            Path(os.environ.get('USERPROFILE', '')) / '.claude',
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Claude'
        ]
        
        mcp_config = {
            "mcpServers": {
                "memory": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "env": {
                        "MEMORY_BACKEND": "sqlite",
                        "MEMORY_FILE": str(self.memory_db_path).replace('\\', '\\\\')
                    }
                },
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "@modelcontextprotocol/server-filesystem",
                        str(self.workspace_path).replace('\\', '\\\\')
                    ],
                    "env": {}
                },
                "f-drive": {
                    "command": "npx",
                    "args": [
                        "@modelcontextprotocol/server-filesystem",
                        "F:\\\\MCPVotsAGI_Data"
                    ],
                    "env": {}
                }
            }
        }
        
        # Save configuration in multiple locations
        config_saved = False
        for claude_path in claude_paths:
            try:
                claude_path.mkdir(parents=True, exist_ok=True)
                config_file = claude_path / "claude_code_settings.json"
                
                with open(config_file, 'w') as f:
                    json.dump(mcp_config, f, indent=2)
                    
                logger.info(f"✅ MCP config saved to: {config_file}")
                config_saved = True
                
            except Exception as e:
                logger.warning(f"Could not save to {claude_path}: {e}")
                
        if not config_saved:
            # Save to current directory as fallback
            fallback_config = Path("claude_code_settings.json")
            with open(fallback_config, 'w') as f:
                json.dump(mcp_config, f, indent=2)
            logger.info(f"✅ MCP config saved to: {fallback_config}")
            
        return mcp_config
        
    def test_memory_access(self):
        """Test memory database access"""
        try:
            conn = sqlite3.connect(str(self.memory_db_path))
            cursor = conn.cursor()
            
            # Query memories
            cursor.execute("SELECT key, value, category FROM memories")
            memories = cursor.fetchall()
            
            logger.info("\n📚 Current Memories:")
            for key, value, category in memories:
                logger.info(f"  [{category}] {key}: {value}")
                
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to access memory: {e}")
            return False
            
    def run(self):
        """Run the complete configuration"""
        logger.info("🚀 Configuring MCP Memory for Claude CLI...")
        
        # Setup database
        self.setup_memory_database()
        
        # Create configuration
        config = self.create_mcp_config()
        
        # Test access
        if self.test_memory_access():
            logger.info("\n✅ MCP Memory configuration complete!")
            logger.info("\nTo use MCP in Claude CLI:")
            logger.info("1. Restart Claude CLI")
            logger.info("2. Run: claude mcp")
            logger.info("3. You should see the memory server listed")
            logger.info("\nMemory database location: " + str(self.memory_db_path))
            logger.info("F: Drive memory location: " + str(self.f_drive_memory))
        else:
            logger.error("\n❌ Memory configuration failed")


if __name__ == "__main__":
    configurator = MCPMemoryConfigurator()
    configurator.run()