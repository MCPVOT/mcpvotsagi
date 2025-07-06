#!/usr/bin/env python3
"""
View Memory Contents from F: Drive and SQLite
=============================================
Shows what's stored in the AGI memory systems
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def view_f_drive_memory():
    """View memory contents from F: drive"""
    print("\n🗄️ F: Drive Memory Contents")
    print("=" * 50)
    
    f_drive_paths = {
        "Memory Store": "F:/MCPVotsAGI_Data/memory_store",
        "Chat Memory": "F:/MCPVotsAGI_Data/chat_memory", 
        "Knowledge Graph": "F:/MCPVotsAGI_Data/memory_store/knowledge_graph",
        "Context Cache": "F:/MCPVotsAGI_Data/context_cache"
    }
    
    for name, path in f_drive_paths.items():
        p = Path(path)
        if p.exists():
            print(f"\n📁 {name} ({path}):")
            
            # Count files
            json_files = list(p.rglob("*.json"))
            txt_files = list(p.rglob("*.txt"))
            db_files = list(p.rglob("*.db"))
            
            if json_files:
                print(f"  - {len(json_files)} JSON files")
                for f in json_files[:3]:  # Show first 3
                    print(f"    • {f.name}")
                if len(json_files) > 3:
                    print(f"    ... and {len(json_files) - 3} more")
                    
            if txt_files:
                print(f"  - {len(txt_files)} text files")
                
            if db_files:
                print(f"  - {len(db_files)} database files")
                for f in db_files:
                    print(f"    • {f.name}")
                    
            # Check subdirectories
            subdirs = [d for d in p.iterdir() if d.is_dir()]
            if subdirs:
                print(f"  - {len(subdirs)} subdirectories:")
                for d in subdirs[:5]:
                    print(f"    📂 {d.name}")
        else:
            print(f"\n❌ {name} not found at {path}")

def view_sqlite_memory():
    """View SQLite memory database contents"""
    print("\n\n💾 SQLite Memory Database")
    print("=" * 50)
    
    db_path = Path("C:/Workspace/MCPVotsAGI/data/agi_memory.db")
    
    if not db_path.exists():
        print("❌ SQLite memory database not found")
        print(f"   Expected at: {db_path}")
        return
        
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        
        for table_name, in tables:
            print(f"\n📋 Table: {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                print(f"   Columns: {', '.join(columns)}")
                print("   Sample data:")
                
                for row in rows:
                    print(f"     {row}")
                    
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading SQLite database: {e}")

def view_storage_config():
    """View storage configuration"""
    print("\n\n⚙️ Storage Configuration")
    print("=" * 50)
    
    config_path = Path("F:/MCPVotsAGI_Data/storage_config.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            print(f"📄 Configuration from {config_path}:")
            print(f"   Created: {config.get('created', 'Unknown')}")
            print(f"   Platform: {config.get('platform', 'Unknown')}")
            print(f"   Base Path: {config.get('base_path', 'Unknown')}")
            print(f"   F: Drive Available: {config.get('f_drive_available', False)}")
            print(f"   Total Allocated: {config.get('total_allocated_gb', 0)}GB")
            
            if 'categories' in config:
                print("\n   Storage Categories:")
                for cat, info in config['categories'].items():
                    print(f"     • {cat}: {info.get('size_gb', 0)}GB - {info.get('description', '')}")
                    
        except Exception as e:
            print(f"❌ Error reading config: {e}")
    else:
        print("❌ Storage config not found")

def main():
    print("🧠 ULTIMATE AGI Memory Viewer")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # View F: drive memory
    view_f_drive_memory()
    
    # View SQLite memory
    view_sqlite_memory()
    
    # View storage config
    view_storage_config()
    
    print("\n" + "=" * 70)
    print("✅ Memory scan complete!")

if __name__ == "__main__":
    main()