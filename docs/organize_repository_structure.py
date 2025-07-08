#!/usr/bin/env python3
"""
Repository Organization Script
Moves files from root directory into proper folder structure
"""

import os
import shutil
from pathlib import Path
import json

def create_folder_structure():
    """Create proper folder structure"""
    base_path = Path.cwd()

    folders = {
        'scripts': 'All executable scripts and launchers',
        'config': 'Configuration files (JSON, YAML, etc.)',
        'docs': 'Documentation files (MD, reports, etc.)',
        'services': 'Service files and managers',
        'tests': 'Test files and validation scripts',
        'tools': 'Utility tools and helpers',
        'logs': 'Log files and output',
        'data': 'Data files and databases',
        'notebooks': 'Jupyter notebooks',
        'reports': 'Generated reports and analysis',
        'archive': 'Backup and archived files'
    }

    for folder, description in folders.items():
        folder_path = base_path / folder
        folder_path.mkdir(exist_ok=True)

        # Create README in each folder
        readme_path = folder_path / 'README.md'
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(f"# {folder.title()} Directory\n\n{description}\n")

    print("✅ Folder structure created")
    return folders

def organize_files():
    """Organize files into appropriate folders"""
    base_path = Path.cwd()

    # File organization rules
    organization_rules = {
        'scripts': {
            'patterns': ['launch_', 'run_', 'start_', 'execute_', 'fix_', 'check_', 'install_'],
            'extensions': ['.py'],
            'exceptions': ['dgm_integration_manager_v2.py', 'dgm_evolution_connector.py']
        },
        'config': {
            'patterns': ['config', 'settings'],
            'extensions': ['.json', '.yaml', '.yml', '.ini'],
            'specific_files': ['requirements.txt', 'package.json']
        },
        'docs': {
            'patterns': ['README', 'GUIDE', 'DOCS', 'ARCHITECTURE', 'OVERVIEW'],
            'extensions': ['.md'],
            'exceptions': ['GITHUB_UPDATE_SUMMARY.md']  # Keep this in root for now
        },
        'services': {
            'patterns': ['_service', '_server', '_manager', '_connector'],
            'extensions': ['.py'],
            'specific_files': ['dgm_integration_manager_v2.py', 'dgm_evolution_connector.py']
        },
        'tests': {
            'patterns': ['test_', 'verify_', 'validate_'],
            'extensions': ['.py']
        },
        'tools': {
            'patterns': ['tool', 'helper', 'analyzer', 'utility'],
            'extensions': ['.py', '.sh', '.ps1']
        },
        'notebooks': {
            'extensions': ['.ipynb']
        },
        'reports': {
            'patterns': ['REPORT', 'SUMMARY', 'ANALYSIS', 'SUCCESS'],
            'extensions': ['.md', '.json'],
            'exceptions': ['GITHUB_UPDATE_SUMMARY.md']
        },
        'data': {
            'extensions': ['.db', '.sqlite', '.csv'],
            'patterns': ['status', 'dashboard']
        }
    }

    moved_files = []

    for item in base_path.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            target_folder = determine_target_folder(item, organization_rules)

            if target_folder:
                target_path = base_path / target_folder / item.name

                # Check if file already exists
                if target_path.exists():
                    print(f"⚠️ File already exists: {target_path}")
                    continue

                try:
                    shutil.move(str(item), str(target_path))
                    moved_files.append({
                        'file': item.name,
                        'from': 'root',
                        'to': target_folder
                    })
                    print(f"📁 Moved: {item.name} → {target_folder}/")
                except Exception as e:
                    print(f"❌ Error moving {item.name}: {e}")

    return moved_files

def determine_target_folder(file_path, rules):
    """Determine which folder a file should go to"""
    file_name = file_path.name.lower()
    file_stem = file_path.stem.lower()
    file_suffix = file_path.suffix.lower()

    for folder, rule in rules.items():
        # Check exceptions first
        if 'exceptions' in rule and file_path.name in rule['exceptions']:
            continue

        # Check specific files
        if 'specific_files' in rule and file_path.name in rule['specific_files']:
            return folder

        # Check extensions
        if 'extensions' in rule and file_suffix in rule['extensions']:
            # Check patterns if they exist
            if 'patterns' in rule:
                if any(pattern in file_name for pattern in rule['patterns']):
                    return folder
            else:
                return folder

        # Check patterns only
        if 'patterns' in rule and 'extensions' not in rule:
            if any(pattern in file_name for pattern in rule['patterns']):
                return folder

    return None

def create_organization_report(moved_files):
    """Create a report of the organization"""
    report = {
        'timestamp': '2025-07-07',
        'total_files_moved': len(moved_files),
        'organization_summary': {},
        'moved_files': moved_files
    }

    # Count files by folder
    for file_info in moved_files:
        folder = file_info['to']
        if folder not in report['organization_summary']:
            report['organization_summary'][folder] = 0
        report['organization_summary'][folder] += 1

    # Save report
    with open('reports/REPOSITORY_ORGANIZATION_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Organization Summary:")
    print(f"Total files moved: {len(moved_files)}")
    for folder, count in report['organization_summary'].items():
        print(f"   {folder}: {count} files")

def main():
    """Main organization function"""
    print("🔧 Starting Repository Organization...")
    print("=" * 50)

    # Create folder structure
    folders = create_folder_structure()

    # Organize files
    print("\n📁 Moving files to appropriate folders...")
    moved_files = organize_files()

    # Create report
    print("\n📊 Creating organization report...")
    create_organization_report(moved_files)

    print("\n✅ Repository organization complete!")
    print("\n🎯 Next steps:")
    print("1. Review the moved files in each folder")
    print("2. Update any scripts that reference moved files")
    print("3. Test that services still work after reorganization")
    print("4. Commit the organized structure to Git")

if __name__ == "__main__":
    main()
