import sys
import os
from pathlib import Path

print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())
print("Script location:", __file__)
print("Platform:", sys.platform)

# Test paths
workspace = Path("C:/Workspace") if sys.platform == "win32" else Path("/mnt/c/Workspace")
print("\nWorkspace path:", workspace)
print("Workspace exists:", workspace.exists())

mcpvots_agi = workspace / "MCPVotsAGI"
print("\nMCPVotsAGI path:", mcpvots_agi)
print("MCPVotsAGI exists:", mcpvots_agi.exists())

# List files
if mcpvots_agi.exists():
    print("\nFiles in MCPVotsAGI:")
    for f in list(mcpvots_agi.iterdir())[:10]:
        print(f" - {f.name}")