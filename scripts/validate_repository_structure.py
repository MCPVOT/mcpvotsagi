#!/usr/bin/env python3
"""
Post-Organization Repository Structure Validator
==============================================

Validates that the repository reorganization was successful and all
key files are in their correct locations with proper references.

Author: MCPVotsAGI Team
Date: January 2025
Version: 1.0.0
"""

import json
import os
import re
from pathlib import Path
from typing import Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RepositoryStructureValidator:
    """Validates repository structure after organization"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.expected_structure = {
            "services/": [
                "dgm_evolution_connector.py",
                "dgm_integration_manager.py",
                "dgm_integration_manager_v2.py",
                "ecosystem_manager.py",
                "ultimate_agi_launcher_v3.py"
            ],
            "src/trading/": [
                "dgm_trading_algorithms_v2.py",
                "dgm_trading_algorithms.py",
                "unified_trading_backend.py"
            ],
            "scripts/": [
                "launch_ecosystem_simple.py",
                "launch_with_deepseek.py",
                "check_ecosystem_status.py"
            ],
            "config/": [
                "ecosystem_config.yaml"
            ],
            "docs/": [
                "ARCHITECTURE.md",
                "README_v2.md"
            ],
            "tests/": [
                "test_dgm_health.py"
            ],
            "tools/": [
                "service_deduplicator.py",
                "claudia_ollama_dgm_helper.py"
            ],
            "core/": [],  # Check if exists
            "reports/": [],  # Check if exists
            "logs/": [],  # Check if exists
            "data/": [],  # Check if exists
        }

        self.validation_results = {
            "structure_validation": {},
            "file_existence": {},
            "import_references": {},
            "port_configuration": {},
            "summary": {}
        }

    def validate_directory_structure(self) -> dict[str, bool]:
        """Validate that expected directories exist"""
        logger.info("🔍 Validating directory structure...")

        structure_results = {}
        for directory in self.expected_structure.keys():
            dir_path = self.project_root / directory
            exists = dir_path.exists() and dir_path.is_dir()
            structure_results[directory] = exists

            if exists:
                logger.info(f"✅ Directory exists: {directory}")
            else:
                logger.warning(f"❌ Directory missing: {directory}")

        return structure_results

    def validate_file_existence(self) -> dict[str, Dict[str, bool]]:
        """Validate that expected files exist in correct directories"""
        logger.info("🔍 Validating file existence...")

        file_results = {}
        for directory, files in self.expected_structure.items():
            file_results[directory] = {}

            for filename in files:
                file_path = self.project_root / directory / filename
                exists = file_path.exists() and file_path.is_file()
                file_results[directory][filename] = exists

                if exists:
                    logger.info(f"✅ File exists: {directory}{filename}")
                else:
                    logger.warning(f"❌ File missing: {directory}{filename}")

        return file_results

    def validate_import_references(self) -> dict[str, List[str]]:
        """Check for broken import references after reorganization"""
        logger.info("🔍 Validating import references...")

        import_issues = {}
        python_files = list(self.project_root.glob("**/*.py"))

        # Common problematic import patterns
        problematic_patterns = [
            r"from dgm_trading_algorithms",
            r"import dgm_trading_algorithms",
            r"from dgm_evolution_connector",
            r"import dgm_evolution_connector",
            r"from ecosystem_manager",
            r"import ecosystem_manager"
        ]

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_issues = []
                for pattern in problematic_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        file_issues.extend(matches)

                if file_issues:
                    relative_path = py_file.relative_to(self.project_root)
                    import_issues[str(relative_path)] = file_issues

            except Exception as e:
                logger.error(f"❌ Error reading {py_file}: {e}")

        return import_issues

    def validate_port_configuration(self) -> dict[str, Dict]:
        """Validate port configurations are consistent"""
        logger.info("🔍 Validating port configurations...")

        port_config = {}
        expected_ports = {
            "dgm_evolution": 8003,
            "dgm_trading_v2": 8004,
            "dgm_trading_legacy": 8005,
            "ecosystem_manager": 8001,
            "ultimate_agi": 8002
        }

        # Check port references in key files
        key_files = [
            "README.md",
            "services/dgm_integration_manager.py",
            "tests/test_dgm_health.py"
        ]

        for filename in key_files:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_ports = {}
                    for service, expected_port in expected_ports.items():
                        # Look for port references
                        port_pattern = rf"{expected_port}"
                        if re.search(port_pattern, content):
                            file_ports[service] = expected_port

                    port_config[filename] = file_ports

                except Exception as e:
                    logger.error(f"❌ Error reading {filename}: {e}")

        return port_config

    def check_critical_files(self) -> dict[str, bool]:
        """Check that critical files are present and valid"""
        logger.info("🔍 Checking critical files...")

        critical_files = {
            "README.md": self.project_root / "README.md",
            "package.json": self.project_root / "package.json",
            ".env": self.project_root / ".env",
            ".gitignore": self.project_root / ".gitignore",
            "LICENSE": self.project_root / "LICENSE"
        }

        critical_results = {}
        for name, path in critical_files.items():
            exists = path.exists()
            critical_results[name] = exists

            if exists:
                logger.info(f"✅ Critical file exists: {name}")
            else:
                logger.warning(f"❌ Critical file missing: {name}")

        return critical_results

    def count_files_by_category(self) -> dict[str, int]:
        """Count files in each organized directory"""
        logger.info("📊 Counting files by category...")

        file_counts = {}
        for directory in self.expected_structure.keys():
            dir_path = self.project_root / directory
            if dir_path.exists():
                # Count Python files
                py_files = list(dir_path.glob("**/*.py"))
                file_counts[f"{directory}python_files"] = len(py_files)

                # Count all files
                all_files = list(dir_path.glob("**/*"))
                all_files = [f for f in all_files if f.is_file()]
                file_counts[f"{directory}total_files"] = len(all_files)

        return file_counts

    def generate_validation_report(self) -> dict:
        """Generate comprehensive validation report"""
        logger.info("📊 Generating validation report...")

        # Run all validations
        self.validation_results["structure_validation"] = self.validate_directory_structure()
        self.validation_results["file_existence"] = self.validate_file_existence()
        self.validation_results["import_references"] = self.validate_import_references()
        self.validation_results["port_configuration"] = self.validate_port_configuration()
        self.validation_results["critical_files"] = self.check_critical_files()
        self.validation_results["file_counts"] = self.count_files_by_category()

        # Generate summary
        total_directories = len(self.expected_structure)
        valid_directories = sum(self.validation_results["structure_validation"].values())

        total_critical_files = len(self.validation_results["critical_files"])
        valid_critical_files = sum(self.validation_results["critical_files"].values())

        import_issues_count = len(self.validation_results["import_references"])

        self.validation_results["summary"] = {
            "validation_timestamp": f"{os.path.getmtime(__file__)}",
            "total_directories": total_directories,
            "valid_directories": valid_directories,
            "directory_success_rate": (valid_directories / total_directories * 100) if total_directories > 0 else 0,
            "total_critical_files": total_critical_files,
            "valid_critical_files": valid_critical_files,
            "critical_files_success_rate": (valid_critical_files / total_critical_files * 100) if total_critical_files > 0 else 0,
            "import_issues_count": import_issues_count,
            "overall_status": "SUCCESS" if (valid_directories == total_directories and
                                          valid_critical_files == total_critical_files and
                                          import_issues_count == 0) else "NEEDS_ATTENTION"
        }

        return self.validation_results

    def save_report(self, report: Dict):
        """Save validation report to file"""
        report_path = self.project_root / "reports" / "REPOSITORY_STRUCTURE_VALIDATION.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Validation report saved to: {report_path}")

    def print_summary(self, report: Dict):
        """Print validation summary"""
        summary = report["summary"]

        print("\n" + "="*60)
        print("🎯 REPOSITORY STRUCTURE VALIDATION SUMMARY")
        print("="*60)
        print(f"Directory Structure: {summary['valid_directories']}/{summary['total_directories']} ({summary['directory_success_rate']:.1f}%)")
        print(f"Critical Files: {summary['valid_critical_files']}/{summary['total_critical_files']} ({summary['critical_files_success_rate']:.1f}%)")
        print(f"Import Issues Found: {summary['import_issues_count']}")
        print(f"Overall Status: {summary['overall_status']}")

        if summary['overall_status'] == "SUCCESS":
            print("🎉 REPOSITORY STRUCTURE VALIDATION: SUCCESS!")
        else:
            print("⚠️  REPOSITORY STRUCTURE VALIDATION: NEEDS ATTENTION")

        # Print file counts
        print("\n📊 File Distribution:")
        for key, count in report["file_counts"].items():
            if "python_files" in key:
                directory = key.replace("python_files", "")
                print(f"  {directory}: {count} Python files")

        print("="*60)

def main():
    """Main validation function"""
    logger.info("🚀 Starting Repository Structure Validation")

    validator = RepositoryStructureValidator()
    report = validator.generate_validation_report()
    validator.save_report(report)
    validator.print_summary(report)

    return report["summary"]["overall_status"] == "SUCCESS"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
