#\!/bin/bash
# MCPVotsAGI Quick Start Script

echo "🚀 MCPVotsAGI Ecosystem Launcher"
echo "================================"

# Check Python version
python_version=$(python3 -c "import sys; print(\".\".join(map(str, sys.version_info[:2])))")
if [[ $(echo "$python_version < 3.8"  < /dev/null |  bc) -eq 1 ]]; then
    echo "❌ Error: Python 3.8+ required (found $python_version)"
    exit 1
fi

# Check if virtual environment exists
if [ \! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run health check
echo "🏥 Running system health check..."
python launcher.py doctor

if [ $? -ne 0 ]; then
    echo "❌ Health check failed. Please fix issues before continuing."
    exit 1
fi

# Start ecosystem
echo ""
echo "✨ Starting MCPVotsAGI Ecosystem..."
echo ""

# Default to quickstart, but allow custom commands
if [ $# -eq 0 ]; then
    python launcher.py quickstart
else
    python launcher.py "$@"
fi
