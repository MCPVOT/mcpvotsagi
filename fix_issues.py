#!/usr/bin/env python3
"""
Fix immediate issues with the MCPVotsAGI system
"""
import os
import sys
import subprocess
from pathlib import Path

def fix_encoding_issue():
    """Fix the Unicode encoding issue in organize_project_structure.py"""
    print("Fixing Unicode encoding issue...")
    
    file_path = Path("organize_project_structure.py")
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emoji characters with text
        replacements = {
            '\U0001f680': '[ROCKET]',  # 🚀
            '\U0001f4e6': '[PACKAGE]',  # 📦
            '\U0001f4c1': '[FOLDER]',   # 📁
            '\U0001f310': '[GLOBE]',    # 🌐
            '\U0001f4dd': '[MEMO]',     # 📝
            '\U0001f527': '[WRENCH]',   # 🔧
            '\U0001f6a8': '[ALERT]',    # 🚨
            '✅': '[OK]',
            '❌': '[FAIL]',
            '⚠️': '[WARN]',
            '📋': '[CLIPBOARD]',
            '🔍': '[SEARCH]',
            '💻': '[COMPUTER]',
            '📤': '[OUTBOX]',
            '🗂️': '[FOLDER]',
            '⚡': '[LIGHTNING]',
            '🧪': '[TEST]'
        }
        
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
        
        # Save with explicit UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] Fixed Unicode encoding issues")
    else:
        print("[WARN] organize_project_structure.py not found")

def fix_git_ownership():
    """Fix Git repository ownership issue"""
    print("\nFixing Git ownership issue...")
    
    try:
        # Add safe directory
        cmd = ['git', 'config', '--global', '--add', 'safe.directory', 'C:/Workspace/MCPVotsAGI']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Added repository to Git safe directories")
        else:
            print(f"[FAIL] Error: {result.stderr}")
            
        # Also try to fix ownership if running as admin
        if os.name == 'nt':  # Windows
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                print("Running as administrator - attempting to fix ownership...")
                # This would need icacls or takeown commands
    except Exception as e:
        print(f"[FAIL] Error fixing Git: {e}")

def create_simple_backup():
    """Create a simple backup without emojis"""
    print("\nCreating simple backup...")
    
    backup_script = '''#!/usr/bin/env python3
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
'''
    
    with open("simple_backup.py", "w", encoding='utf-8') as f:
        f.write(backup_script)
    
    print("[OK] Created simple_backup.py")
    
    # Run the backup
    try:
        result = subprocess.run([sys.executable, "simple_backup.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Backup completed successfully")
            print(result.stdout)
        else:
            print(f"[FAIL] Backup error: {result.stderr}")
    except Exception as e:
        print(f"[FAIL] Error running backup: {e}")

def test_services():
    """Test that services are still running"""
    print("\nTesting services...")
    
    services = [
        ("Unified Dashboard", "http://localhost:8900/api/status"),
        ("Backend System", "http://localhost:8889/"),
        ("MCP Status", "http://localhost:8900/api/mcp-status")
    ]
    
    try:
        import requests
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] {name} is running")
                else:
                    print(f"[WARN] {name} returned status {response.status_code}")
            except Exception as e:
                print(f"[FAIL] {name} not accessible: {e}")
    except ImportError:
        print("[WARN] requests module not available, skipping service tests")

def main():
    print("=" * 60)
    print("MCPVotsAGI ISSUE FIXER")
    print("=" * 60)
    
    # Fix issues
    fix_encoding_issue()
    fix_git_ownership()
    create_simple_backup()
    test_services()
    
    print("\n" + "=" * 60)
    print("FIXES COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python simple_backup.py")
    print("2. Run: git add .")
    print("3. Run: git commit -m 'feat: Major MCPVotsAGI reorganization and async enhancement'")
    print("4. Run: git push origin main")
    print("\nIf git still has issues, run as Administrator or use:")
    print("   git config --global --add safe.directory C:/Workspace/MCPVotsAGI")

if __name__ == "__main__":
    main()