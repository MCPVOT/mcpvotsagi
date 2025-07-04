
import sys
sys.path.insert(0, "/mnt/c/Workspace/MCPVotsAGI")
from oracle_agi_ultimate_unified_v2 import OracleAGIUnifiedDashboard

dashboard = OracleAGIUnifiedDashboard()
dashboard.run(port=3011)
