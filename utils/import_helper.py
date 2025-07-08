"""
Import Helper Module
==================

Provides easy imports for DGM services after repository reorganization.

Usage:
    from utils.import_helper import dgm_trading_v2, dgm_evolution, ecosystem_manager
"""

import sys
from pathlib import Path

# Add service directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "src" / "trading"))

# Import services
try:
    import dgm_trading_algorithms_v2 as dgm_trading_v2
except ImportError:
    dgm_trading_v2 = None

try:
    import dgm_trading_algorithms as dgm_trading_legacy
except ImportError:
    dgm_trading_legacy = None

try:
    import dgm_evolution_connector as dgm_evolution
except ImportError:
    dgm_evolution = None

try:
    import ecosystem_manager
except ImportError:
    ecosystem_manager = None

# Export for easy imports
__all__ = ['dgm_trading_v2', 'dgm_trading_legacy', 'dgm_evolution', 'ecosystem_manager']
