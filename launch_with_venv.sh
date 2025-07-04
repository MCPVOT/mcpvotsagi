#!/bin/bash
# MCPVotsAGI Ecosystem Launcher with Virtual Environment

echo "==============================================="
echo "   MCPVotsAGI Ecosystem Launcher"
echo "==============================================="

# Activate virtual environment
source "/mnt/c/Workspace/MCPVotsAGI/venv/bin/activate"

# Set environment variables
export PYTHONPATH="$PYTHONPATH:/mnt/c/Workspace/MCPVotsAGI:/mnt/c/Workspace/MCPVots"

# Check if ecosystem manager exists
if [ ! -f "/mnt/c/Workspace/MCPVotsAGI/ecosystem_manager.py" ]; then
    echo "Error: ecosystem_manager.py not found!"
    echo "Starting dashboard directly..."
    python "/mnt/c/Workspace/MCPVotsAGI/oracle_agi_ultimate_unified_v2.py"
else
    # Launch ecosystem manager
    echo ""
    echo "Starting Ecosystem Manager..."
    python "/mnt/c/Workspace/MCPVotsAGI/ecosystem_manager.py" start
fi