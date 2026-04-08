#!/usr/bin/env python3
"""
Fix Redis Configuration for WSL2 + Windows Integration
Automatically configures Redis to work with MCPVotsAGI A2A system
"""

import subprocess
import time
import redis
import json
from datetime import datetime

def run_wsl_command(command, description=""):
    """Run a command in WSL2 Ubuntu"""
    try:
        print(f"🔧 {description}")
        full_command = f'wsl -d Ubuntu {command}'
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout: {description}")
        return False
    except Exception as e:
        print(f"❌ Exception: {description} - {e}")
        return False

def fix_redis_configuration():
    """Fix Redis configuration for WSL2 access"""
    print("🚀 Fixing Redis Configuration for WSL2 + Windows Integration")
    print("=" * 70)

    # Stop Redis first
    run_wsl_command('sudo systemctl stop redis-server', "Stopping Redis service")

    # Backup original config
    run_wsl_command('sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup',
                   "Backing up original Redis config")

    # Fix bind address - allow all interfaces
    run_wsl_command("sudo sed -i 's/^bind 127.0.0.1.*/bind 0.0.0.0/' /etc/redis/redis.conf",
                   "Setting Redis to bind to all interfaces")

    # Disable protected mode for local development
    run_wsl_command("sudo sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis/redis.conf",
                   "Disabling Redis protected mode")

    # Set password for security (optional)
    run_wsl_command("sudo sed -i 's/^# requirepass foobared/requirepass os.environ.get('REDIS_PASSWORD', '')/' /etc/redis/redis.conf",
                   "Setting Redis password")

    # Start Redis service
    run_wsl_command('sudo systemctl start redis-server', "Starting Redis service")

    # Enable Redis to start on boot
    run_wsl_command('sudo systemctl enable redis-server', "Enabling Redis auto-start")

    # Check Redis status
    time.sleep(2)
    success = run_wsl_command('sudo systemctl is-active redis-server', "Checking Redis status")

    return success

def get_wsl_ip():
    """Get WSL2 IP address"""
    try:
        result = subprocess.run('wsl -d Ubuntu hostname -I', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            ip = result.stdout.strip().split()[0]  # Get first IP
            return ip
        return None
    except:
        return None

def test_redis_connection(host="localhost", port=6379, password=None):
    """Test Redis connection"""
    try:
        print(f"🔍 Testing Redis connection to {host}:{port}")

        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test ping
        result = r.ping()
        if result:
            print(f"✅ Redis PING successful on {host}:{port}")

            # Test set/get
            test_key = "mcpvotsagi:test"
            test_value = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "test": "Redis connection from Windows"
            })

            r.set(test_key, test_value, ex=60)
            retrieved = r.get(test_key)

            if retrieved:
                print(f"✅ Redis SET/GET successful")
                print(f"   Data: {retrieved}")

            r.close()
            return True

    except Exception as e:
        print(f"❌ Redis connection failed to {host}:{port} - {e}")
        return False

def main():
    """Main function"""
    print("🚀 MCPVotsAGI Redis Configuration Fixer")
    print("=" * 70)

    # Fix Redis configuration
    config_success = fix_redis_configuration()

    if not config_success:
        print("❌ Failed to configure Redis. Please check manually.")
        return False

    print("\n" + "=" * 70)
    print("🧪 Testing Redis Connections")
    print("=" * 70)

    # Get WSL IP
    wsl_ip = get_wsl_ip()
    if wsl_ip:
        print(f"📍 WSL2 IP Address: {wsl_ip}")
    else:
        print("⚠️ Could not determine WSL2 IP address")
        wsl_ip = "172.27.187.70"  # Fallback

    # Test connections
    localhost_success = test_redis_connection("localhost", 6379, "os.environ.get('REDIS_PASSWORD', '')")
    wsl_success = test_redis_connection(wsl_ip, 6379, "os.environ.get('REDIS_PASSWORD', '')")

    print("\n" + "=" * 70)
    print("📊 REDIS CONFIGURATION SUMMARY")
    print("=" * 70)
    print(f"✅ Configuration Applied: {'YES' if config_success else 'NO'}")
    print(f"✅ Localhost Access: {'WORKING' if localhost_success else 'FAILED'}")
    print(f"✅ WSL2 IP Access: {'WORKING' if wsl_success else 'FAILED'}")

    if localhost_success or wsl_success:
        print(f"\n🎉 SUCCESS! Redis is configured and accessible.")
        print(f"🔗 Connection Details:")
        if localhost_success:
            print(f"   - localhost:6379 (password: os.environ.get('REDIS_PASSWORD', ''))")
        if wsl_success:
            print(f"   - {wsl_ip}:6379 (password: os.environ.get('REDIS_PASSWORD', ''))")

        # Update test script with working configuration
        working_host = "localhost" if localhost_success else wsl_ip
        update_test_script(working_host, "os.environ.get('REDIS_PASSWORD', '')")

        return True
    else:
        print(f"\n❌ FAILED! Redis is not accessible. Manual intervention required.")
        return False

def update_test_script(host, password):
    """Update the Redis test script with working configuration"""
    try:
        config = {
            "redis_host": host,
            "redis_port": 6379,
            "redis_password": password,
            "updated": datetime.now().isoformat()
        }

        with open("redis_config.json", "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n📄 Redis configuration saved to: redis_config.json")

    except Exception as e:
        print(f"⚠️ Could not save Redis config: {e}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
