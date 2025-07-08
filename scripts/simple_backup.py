#!/usr/bin/env python3
"""Simple backup script without Unicode issues"""
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_system():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Directories to backup
    dirs_to_backup = [
        "claudia",
        "components",
        "scripts",
        "config"
    ]
    
    # Files to backup
    files_to_backup = [
        "analyze_backend.py",
        "ultimate_agi_dashboard.py",
        "test_all_mcp_servers.py",
        "README.md"
    ]
    
    print(f"[BACKUP] Creating backup in {backup_dir}")
    
    # Backup directories
    for dir_name in dirs_to_backup:
        if Path(dir_name).exists():
            dest = backup_dir / dir_name
            shutil.copytree(dir_name, dest, dirs_exist_ok=True)
            print(f"[OK] Backed up {dir_name}")
    
    # Backup files
    for file_name in files_to_backup:
        if Path(file_name).exists():
            dest = backup_dir / file_name
            shutil.copy2(file_name, dest)
            print(f"[OK] Backed up {file_name}")
    
    print(f"[COMPLETE] Backup saved to {backup_dir}")
    return str(backup_dir)

if __name__ == "__main__":
    backup_system()
