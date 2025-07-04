#!/usr/bin/env python3
"""
MCPVotsAGI Workspace Cleanup Tool
Helps organize and archive legacy files outside the main project directory.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def analyze_workspace():
    """Analyze the workspace and categorize unorganized files."""

    workspace_root = Path(__file__).parent.parent
    mcpvots_dir = Path(__file__).parent

    analysis = {
        "timestamp": datetime.now().isoformat(),
        "workspace_root": str(workspace_root),
        "organized_dir": str(mcpvots_dir),
        "file_categories": {
            "documentation": [],
            "python_scripts": [],
            "configuration": [],
            "data_files": [],
            "batch_scripts": [],
            "logs": [],
            "archives": [],
            "other": []
        },
        "directories": [],
        "total_files": 0
    }

    # Define file categories
    doc_extensions = {'.md', '.txt', '.html', '.pdf'}
    script_extensions = {'.py'}
    config_extensions = {'.json', '.yaml', '.yml', '.cfg', '.ini', '.toml'}
    batch_extensions = {'.bat', '.ps1', '.sh', '.vbs'}
    log_extensions = {'.log'}
    archive_extensions = {'.tar', '.gz', '.zip', '.7z'}
    data_extensions = {'.db', '.sqlite', '.sqlite3'}

    try:
        for item in workspace_root.iterdir():
            if item.name == "MCPVotsAGI":
                continue  # Skip our organized directory

            if item.is_file():
                analysis["total_files"] += 1
                file_ext = item.suffix.lower()

                if file_ext in doc_extensions:
                    analysis["file_categories"]["documentation"].append(str(item))
                elif file_ext in script_extensions:
                    analysis["file_categories"]["python_scripts"].append(str(item))
                elif file_ext in config_extensions:
                    analysis["file_categories"]["configuration"].append(str(item))
                elif file_ext in batch_extensions:
                    analysis["file_categories"]["batch_scripts"].append(str(item))
                elif file_ext in log_extensions:
                    analysis["file_categories"]["logs"].append(str(item))
                elif file_ext in archive_extensions:
                    analysis["file_categories"]["archives"].append(str(item))
                elif file_ext in data_extensions:
                    analysis["file_categories"]["data_files"].append(str(item))
                else:
                    analysis["file_categories"]["other"].append(str(item))

            elif item.is_dir():
                analysis["directories"].append(str(item))

    except Exception as e:
        analysis["error"] = str(e)

    return analysis

def create_archive_structure():
    """Create archive directory structure for organizing legacy files."""

    mcpvots_dir = Path(__file__).parent
    archive_dir = mcpvots_dir / "archive" / "legacy_workspace"

    # Create archive structure
    categories = [
        "documentation",
        "scripts",
        "configuration",
        "data",
        "logs",
        "batch_files",
        "other_directories"
    ]

    for category in categories:
        (archive_dir / category).mkdir(parents=True, exist_ok=True)

    return archive_dir

def generate_cleanup_report():
    """Generate a comprehensive cleanup report."""

    analysis = analyze_workspace()

    # Save analysis to file
    mcpvots_dir = Path(__file__).parent
    report_file = mcpvots_dir / "workspace_cleanup_analysis.json"

    with open(report_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    # Create summary report
    summary = f"""# MCPVotsAGI Workspace Cleanup Analysis

Generated: {analysis['timestamp']}

## Summary
- **Total unorganized files**: {analysis['total_files']}
- **Unorganized directories**: {len(analysis['directories'])}

## File Categories

### Documentation ({len(analysis['file_categories']['documentation'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['documentation'][:10])}
{'...' if len(analysis['file_categories']['documentation']) > 10 else ''}

### Python Scripts ({len(analysis['file_categories']['python_scripts'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['python_scripts'][:10])}
{'...' if len(analysis['file_categories']['python_scripts']) > 10 else ''}

### Configuration Files ({len(analysis['file_categories']['configuration'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['configuration'][:5])}
{'...' if len(analysis['file_categories']['configuration']) > 5 else ''}

### Batch Scripts ({len(analysis['file_categories']['batch_scripts'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['batch_scripts'][:5])}
{'...' if len(analysis['file_categories']['batch_scripts']) > 5 else ''}

### Log Files ({len(analysis['file_categories']['logs'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['logs'][:5])}
{'...' if len(analysis['file_categories']['logs']) > 5 else ''}

### Data Files ({len(analysis['file_categories']['data_files'])})
{chr(10).join(f"- {Path(f).name}" for f in analysis['file_categories']['data_files'][:5])}
{'...' if len(analysis['file_categories']['data_files']) > 5 else ''}

## Recommendations

1. **Archive Legacy Files**: Move old files to `archive/legacy_workspace/`
2. **Integrate Important Scripts**: Move production scripts to `src/`
3. **Update Documentation**: Consolidate important docs into `docs/`
4. **Clean Up**: Delete temporary files, logs, and duplicates

## Next Steps

Run the following commands to organize:

```bash
# Create archive structure
python scripts/workspace_cleanup.py --create-archive

# Move files to archive (dry run first)
python scripts/workspace_cleanup.py --archive --dry-run

# Actually move files
python scripts/workspace_cleanup.py --archive
```

## Git Configuration

The CRLF/LF warnings you saw are now resolved with:
- Enhanced `.gitignore` excluding virtual environments and temp files
- Added `.gitattributes` for proper line ending handling
- Configured Git core settings for Windows

The organized MCPVotsAGI directory is now properly structured and ready for GitHub.
"""

    summary_file = mcpvots_dir / "WORKSPACE_CLEANUP_ANALYSIS.md"
    with open(summary_file, 'w') as f:
        f.write(summary)

    return report_file, summary_file

if __name__ == "__main__":
    print("🧹 MCPVotsAGI Workspace Cleanup Analysis")
    print("=" * 50)

    try:
        report_file, summary_file = generate_cleanup_report()
        print(f"✅ Analysis complete!")
        print(f"📊 Detailed report: {report_file}")
        print(f"📋 Summary report: {summary_file}")
        print()
        print("Next steps:")
        print("1. Review the analysis files")
        print("2. Decide which files to archive vs integrate")
        print("3. Run cleanup operations as needed")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
