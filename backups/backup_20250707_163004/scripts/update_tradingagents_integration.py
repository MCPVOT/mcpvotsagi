#!/usr/bin/env python3
"""
Update TradingAgents Integration
================================
Updates integration code when TradingAgents is synced
"""

import os
import re
import json
from pathlib import Path


def update_integration_files():
    """Update integration files after TradingAgents sync"""
    
    print("Updating TradingAgents integration files...")
    
    # Check if TradingAgents exists
    ta_path = Path("TradingAgents")
    if not ta_path.exists():
        print("TradingAgents directory not found")
        return
        
    # Update import paths in integration files
    integration_files = [
        "tradingagents_deepseek_integration.py",
        "unified_trading_backend.py"
    ]
    
    for file in integration_files:
        file_path = Path(file)
        if file_path.exists():
            content = file_path.read_text()
            
            # Update import paths
            content = re.sub(
                r'sys\.path\.append\([^)]+\)',
                'sys.path.append(str(Path(__file__).parent / "TradingAgents"))',
                content
            )
            
            file_path.write_text(content)
            print(f"Updated {file}")
            
    # Check for new required dependencies
    ta_requirements = ta_path / "requirements.txt"
    if ta_requirements.exists():
        with open(ta_requirements) as f:
            ta_deps = f.read().strip().split('\n')
            
        with open("requirements.txt") as f:
            our_deps = f.read().strip().split('\n')
            
        new_deps = set(ta_deps) - set(our_deps)
        if new_deps:
            print(f"New dependencies found: {new_deps}")
            with open("requirements.txt", 'a') as f:
                for dep in new_deps:
                    f.write(f"\n{dep}")
                    
    print("Integration update complete")


if __name__ == "__main__":
    update_integration_files()