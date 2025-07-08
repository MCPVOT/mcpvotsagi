#!/usr/bin/env python3
"""
Phase 2 Repository Organization Script
Clean up remaining loose files in root directory
"""

import os
import shutil
from pathlib import Path
import json

def organize_remaining_files():
    """Organize remaining files from root directory"""
    base_path = Path.cwd()

    # Enhanced organization rules for remaining files
    organization_rules = {
        'scripts': [
            'launch_', 'start_', 'run_', 'execute_', 'deploy_', 'setup_',
            'check_', 'verify_', 'test_', 'stop_', 'fix_', 'configure_',
            'install_', 'build_', 'create_', 'update_', 'generate_',
            'quick_', 'demo_', 'implement_', 'initialize_', 'simple_'
        ],
        'config': [
            '.env', 'dockerfile', 'docker-compose', 'requirements', 'setup.py',
            'ecosystem_config', 'system_status', 'orchestrator_config',
            'launcher.py', '_config.', 'dashboard_metrics'
        ],
        'docs': [
            'readme', 'architecture', 'changelog', 'contributing', 'license',
            'security', 'mission_', 'complete_', 'comprehens', 'final_',
            'migration_', 'milestone_', 'organization_', 'project_',
            'deployment_', 'development_', 'external_', 'immediate_',
            'implement_', 'enhancement_', 'improvement_', 'integration_',
            'system_', 'windows_', 'mcpvotsagi_complete', 'ultimate_system',
            'repository_', 'claude_', 'claudia_', 'conversation_',
            'cloud_', 'jupiter_', 'unified_', 'f_drive_', 'deepseek_',
            'mock_removal', 'dgm_improvements', 'context7_'
        ],
        'reports': [
            'analysis_', 'report_', 'summary_', 'status_', 'dgm_analysis',
            'dgm_integration', 'github_update'
        ],
        'services': [
            '_service', '_server', '_manager', '_connector', '_integration',
            'ecosystem_', 'n8n_', 'opencti_', 'knowledge_', 'real_',
            'ultimate_', 'unified_', 'finnhub_', 'dashboard_'
        ],
        'tools': [
            '_analyzer', '_monitor', 'analyze_', 'cyberpunk_', 'hierarchical_',
            'organize_', 'health_', 'agents_', 'ai_tools_', 'ollama_',
            'solana_', 'watchyour', '_agi_', 'service_deduplicator'
        ],
        'data': [
            '.db', '.sqlite', 'status.json', 'metrics.db'
        ],
        'archive': [
            '_old', '_backup', '_temp', '_legacy', 'temp_', 'backup_',
            '_v1', '_v2', '_v3', '_v4', 'blobs', 'gvg'
        ]
    }

    moved_files = []

    for item in base_path.iterdir():
        if item.is_file() and not item.name.startswith('.git') and item.name not in ['.env', '.gitignore', '.gitattributes', '.gitmodules', 'README.md', 'LICENSE']:
            target_folder = determine_target_folder_v2(item, organization_rules)

            if target_folder:
                target_path = base_path / target_folder / item.name

                # Create target directory if it doesn't exist
                target_path.parent.mkdir(exist_ok=True)

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

def determine_target_folder_v2(file_path, rules):
    """Determine target folder for remaining files"""
    file_name = file_path.name.lower()
    file_stem = file_path.stem.lower()
    file_suffix = file_path.suffix.lower()

    for folder, patterns in rules.items():
        for pattern in patterns:
            if pattern in file_name:
                return folder

    # Default fallback
    if file_suffix in ['.py']:
        return 'scripts'
    elif file_suffix in ['.json', '.yaml', '.yml', '.toml']:
        return 'config'
    elif file_suffix in ['.md', '.txt', '.rst']:
        return 'docs'
    elif file_suffix in ['.sh', '.bat', '.ps1']:
        return 'scripts'
    else:
        return 'archive'  # Put unrecognized files in archive

def main():
    """Main phase 2 organization function"""
    print("🔧 Starting Phase 2 Repository Organization...")
    print("=" * 50)

    moved_files = organize_remaining_files()

    print(f"\n📊 Phase 2 Summary:")
    print(f"Total additional files moved: {len(moved_files)}")

    # Count by folder
    folder_counts = {}
    for file_info in moved_files:
        folder = file_info['to']
        folder_counts[folder] = folder_counts.get(folder, 0) + 1

    for folder, count in folder_counts.items():
        print(f"   {folder}: {count} files")

    print("\n✅ Phase 2 organization complete!")

if __name__ == "__main__":
    main()
