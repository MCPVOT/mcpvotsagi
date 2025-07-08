#!/usr/bin/env python3
"""
Security Fix Script - Remove hardcoded credentials
"""

import os
import re
from pathlib import Path

def fix_redis_passwords():
    """Replace hardcoded Redis passwords with environment variables"""
    
    files_to_fix = [
        "production_launcher.py",
        "production_launcher_v2.py",
        "core/enhanced_mcp_memory_server.py",
        "services/master_service_launcher.py",
        # Add more files as needed
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace hardcoded passwords
            content = re.sub(
                r'password\s*=\s*["\']mcpvotsagi2025["\']',
                'password=os.environ.get("REDIS_PASSWORD", "redis")',
                content
            )
            content = re.sub(
                r'password\s*=\s*["\']MCPVotsAGI2025!["\']',
                'password=os.environ.get("REDIS_PASSWORD", "redis")',
                content
            )
            
            # Add import if needed
            if 'os.environ' in content and 'import os' not in content:
                content = 'import os\n' + content
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed: {file_path}")

def create_env_template():
    """Create .env.example file"""
    env_template = """# MCPVotsAGI Environment Variables
# Copy this to .env and fill in your values

# Redis Configuration
REDIS_PASSWORD=your_secure_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys (if any)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Security
SECRET_KEY=generate_a_random_secret_key
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.example template")

def add_security_check():
    """Add pre-commit hook to check for secrets"""
    pre_commit = """#!/bin/bash
# Pre-commit hook to check for hardcoded secrets

# Check for common password patterns
if git diff --cached --name-only | xargs grep -E "(password|api_key|secret)\s*=\s*['\"][^'\"]+['\"]" 2>/dev/null; then
    echo "❌ ERROR: Hardcoded credentials detected!"
    echo "Use environment variables instead."
    exit 1
fi

exit 0
"""
    
    hook_path = Path('.git/hooks/pre-commit')
    hook_path.parent.mkdir(exist_ok=True)
    
    with open(hook_path, 'w') as f:
        f.write(pre_commit)
    
    os.chmod(hook_path, 0o755)
    print("✅ Added pre-commit security hook")

if __name__ == "__main__":
    print("🔒 MCPVotsAGI Security Fix Script")
    print("=" * 40)
    
    fix_redis_passwords()
    create_env_template()
    add_security_check()
    
    print("\n📋 Next Steps:")
    print("1. Create .env file with your secure passwords")
    print("2. Change all passwords in production")
    print("3. Test that everything still works")
    print("4. Commit these security fixes")
    print("\n⚠️  IMPORTANT: Never commit .env file!")