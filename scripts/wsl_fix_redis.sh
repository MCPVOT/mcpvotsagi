#!/bin/bash
# Redis Configuration Script for MCPVotsAGI A2A System
# Run this script in WSL2 Ubuntu to configure Redis properly

echo "🚀 MCPVotsAGI Redis Configuration for WSL2"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Stop Redis service
echo "🔧 Stopping Redis service..."
systemctl stop redis-server

# Backup original config
echo "💾 Backing up original Redis configuration..."
cp /etc/redis/redis.conf /etc/redis/redis.conf.backup.$(date +%Y%m%d_%H%M%S)

# Configure Redis for WSL2 + Windows access
echo "⚙️ Configuring Redis for cross-platform access..."

# Fix bind address - allow all interfaces
sed -i 's/^bind 127.0.0.1.*$/bind 0.0.0.0/' /etc/redis/redis.conf

# Disable protected mode for local development
sed -i 's/^protected-mode yes$/protected-mode no/' /etc/redis/redis.conf

# Set password for security
sed -i 's/^# requirepass foobared$/requirepass mcpvotsagi2025/' /etc/redis/redis.conf

# Configure memory management
sed -i 's/^# maxmemory <bytes>$/maxmemory 256mb/' /etc/redis/redis.conf
sed -i 's/^# maxmemory-policy noeviction$/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

# Enable logging
sed -i 's/^logfile ""$/logfile \/var\/log\/redis\/redis-server.log/' /etc/redis/redis.conf

# Create log directory if it doesn't exist
mkdir -p /var/log/redis
chown redis:redis /var/log/redis

# Start Redis service
echo "🚀 Starting Redis service..."
systemctl start redis-server

# Enable Redis to start on boot
echo "🔄 Enabling Redis auto-start..."
systemctl enable redis-server

# Wait for Redis to start
sleep 3

# Check Redis status
echo "🔍 Checking Redis status..."
if systemctl is-active --quiet redis-server; then
    echo "✅ Redis service is running"
else
    echo "❌ Redis service failed to start"
    systemctl status redis-server
    exit 1
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli -a mcpvotsagi2025 ping > /dev/null 2>&1; then
    echo "✅ Redis connection test passed"
else
    echo "❌ Redis connection test failed"
    exit 1
fi

# Get IP addresses
echo "📍 Network Information:"
echo "   WSL2 IP: $(hostname -I | awk '{print $1}')"
echo "   Redis Port: 6379"
echo "   Password: mcpvotsagi2025"

# Test from different interfaces
WSL_IP=$(hostname -I | awk '{print $1}')
echo "🔗 Testing connectivity from different interfaces..."

# Test localhost
if redis-cli -h localhost -a mcpvotsagi2025 ping > /dev/null 2>&1; then
    echo "✅ localhost:6379 - WORKING"
else
    echo "❌ localhost:6379 - FAILED"
fi

# Test WSL IP
if redis-cli -h $WSL_IP -a mcpvotsagi2025 ping > /dev/null 2>&1; then
    echo "✅ $WSL_IP:6379 - WORKING"
else
    echo "❌ $WSL_IP:6379 - FAILED"
fi

# Show Redis configuration summary
echo ""
echo "📊 REDIS CONFIGURATION SUMMARY"
echo "================================"
echo "✅ Redis Service: $(systemctl is-active redis-server)"
echo "✅ Auto-start: $(systemctl is-enabled redis-server)"
echo "✅ Bind Address: 0.0.0.0 (all interfaces)"
echo "✅ Protected Mode: disabled"
echo "✅ Password: mcpvotsagi2025"
echo "✅ Max Memory: 256mb"
echo "✅ Log File: /var/log/redis/redis-server.log"

echo ""
echo "🎉 Redis configuration completed successfully!"
echo "💡 You can now connect from Windows using:"
echo "   redis://localhost:6379 (password: mcpvotsagi2025)"
echo "   redis://$WSL_IP:6379 (password: mcpvotsagi2025)"
echo ""
echo "🔧 To view Redis logs: sudo tail -f /var/log/redis/redis-server.log"
echo "🔧 To restart Redis: sudo systemctl restart redis-server"
