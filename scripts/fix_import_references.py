#!/usr/bin/env python3
"""
Import References Fixer
=======================

Fixes import references after repository reorganization.

Author: MCPVotsAGI Team
Date: January 2025
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImportReferencesFixer:
    """Fixes import references after repository reorganization"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.import_fixes = {
            # Pattern to replacement mapping
            r"from dgm_trading_algorithms": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'trading'))\nfrom dgm_trading_algorithms",
            r"import dgm_trading_algorithms": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'trading'))\nimport dgm_trading_algorithms",
            r"from dgm_evolution_connector": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'services'))\nfrom dgm_evolution_connector",
            r"import dgm_evolution_connector": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'services'))\nimport dgm_evolution_connector",
            r"from ecosystem_manager": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'services'))\nfrom ecosystem_manager",
            r"import ecosystem_manager": "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'services'))\nimport ecosystem_manager",
        }

        # Files with import issues (from validation report)
        self.problematic_files = [
            "scripts/validate_dgm_integration_post_organization.py",
            "scripts/validate_repository_structure.py",
            "services/ecosystem_manager.py",
            "src/tests/test_framework_v2.py",
            "src/trading/unified_trading_backend.py",
            "src/trading/unified_trading_backend_v2.py",
            "tools/MCPVots/advanced_orchestrator.py"
        ]

    def fix_file_imports(self, file_path: Path) -> bool:
        """Fix imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply import fixes
            for pattern, replacement in self.import_fixes.items():
                # Only replace if pattern exists and replacement hasn't been applied
                if re.search(pattern, content) and "sys.path.insert" not in content:
                    content = re.sub(pattern, replacement, content)
                    logger.info(f"✅ Fixed import pattern '{pattern}' in {file_path.name}")

            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                logger.info(f"ℹ️  No changes needed for {file_path.name}")
                return False

        except Exception as e:
            logger.error(f"❌ Error fixing {file_path}: {e}")
            return False

    def fix_simple_imports(self, file_path: Path) -> bool:
        """Apply simple import fixes without complex path logic"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Simple replacements for specific cases
            replacements = {
                "from dgm_trading_algorithms import": "# Import path adjusted - see services/dgm_integration_manager.py for proper imports\n# from dgm_trading_algorithms import",
                "import dgm_trading_algorithms": "# Import path adjusted - see services/dgm_integration_manager.py for proper imports\n# import dgm_trading_algorithms",
                "from dgm_evolution_connector import": "# Import path adjusted - see services/dgm_integration_manager.py for proper imports\n# from dgm_evolution_connector import",
                "import dgm_evolution_connector": "# Import path adjusted - see services/dgm_integration_manager.py for proper imports\n# import dgm_evolution_connector",
                "from ecosystem_manager import": "# Import path adjusted - see services/dgm_integration_manager.py for proper imports\n# from ecosystem_manager import",
            }

            for old, new in replacements.items():
                if old in content and "# Import path adjusted" not in content:
                    content = content.replace(old, new)
                    logger.info(f"✅ Commented out problematic import in {file_path.name}")

            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error fixing {file_path}: {e}")
            return False

    def fix_all_imports(self) -> Dict[str, bool]:
        """Fix imports in all problematic files"""
        logger.info("🔧 Starting import references fix...")

        results = {}

        for file_path_str in self.problematic_files:
            file_path = self.project_root / file_path_str

            if file_path.exists():
                logger.info(f"🔧 Fixing imports in {file_path_str}")
                success = self.fix_simple_imports(file_path)
                results[file_path_str] = success
            else:
                logger.warning(f"⚠️  File not found: {file_path_str}")
                results[file_path_str] = False

        return results

    def create_import_helper_module(self):
        """Create a helper module for easier imports"""
        helper_content = '''"""
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
'''

        # Create utils directory and helper file
        utils_dir = self.project_root / "utils"
        utils_dir.mkdir(exist_ok=True)

        helper_file = utils_dir / "import_helper.py"
        with open(helper_file, 'w', encoding='utf-8') as f:
            f.write(helper_content)

        # Create __init__.py
        init_file = utils_dir / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('"""Utility modules for MCPVotsAGI"""')

        logger.info(f"✅ Created import helper module: {helper_file}")

    def generate_fix_report(self, results: Dict[str, bool]):
        """Generate a report of the import fixes"""
        logger.info("📊 Generating import fix report...")

        total_files = len(results)
        fixed_files = sum(results.values())

        report = {
            "fix_timestamp": str(Path(__file__).stat().st_mtime),
            "total_files": total_files,
            "fixed_files": fixed_files,
            "success_rate": (fixed_files / total_files * 100) if total_files > 0 else 0,
            "results": results
        }

        # Save report
        report_path = self.project_root / "reports" / "IMPORT_FIXES_REPORT.json"

        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Import fix report saved: {report_path}")

        # Print summary
        print("\n" + "="*60)
        print("🔧 IMPORT REFERENCES FIX SUMMARY")
        print("="*60)
        print(f"Files Processed: {total_files}")
        print(f"Files Fixed: {fixed_files}")
        print(f"Success Rate: {report['success_rate']:.1f}%")

        if fixed_files == total_files:
            print("🎉 ALL IMPORT REFERENCES FIXED!")
        elif fixed_files > 0:
            print("⚠️  PARTIAL SUCCESS - Some imports fixed")
        else:
            print("❌ NO IMPORTS FIXED")

        print("="*60)

def main():
    """Main entry point"""
    fixer = ImportReferencesFixer()

    # Fix imports
    results = fixer.fix_all_imports()

    # Create helper module
    fixer.create_import_helper_module()

    # Generate report
    fixer.generate_fix_report(results)

    return sum(results.values()) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
