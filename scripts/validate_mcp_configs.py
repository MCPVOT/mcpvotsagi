#!/usr/bin/env python3
"""
Validate MCP Configurations
===========================
Ensures all MCP servers are properly configured
"""

import json
import yaml
from pathlib import Path


def validate_mcp_configs():
    """Validate all MCP configuration files"""
    
    print("Validating MCP configurations...")
    
    errors = []
    warnings = []
    
    # Check ecosystem config
    ecosystem_config = Path("ecosystem_config.yaml")
    if ecosystem_config.exists():
        with open(ecosystem_config) as f:
            config = yaml.safe_load(f)
            
        # Validate required services
        required_services = [
            "memory_mcp", "github_mcp", "solana_mcp", 
            "browser_tools_mcp", "oracle_agi"
        ]
        
        for service in required_services:
            if service not in config.get("services", {}):
                errors.append(f"Missing service: {service}")
            else:
                service_config = config["services"][service]
                if not service_config.get("port"):
                    errors.append(f"No port configured for {service}")
    else:
        errors.append("ecosystem_config.yaml not found")
        
    # Check Claudia agent configs
    claudia_dir = Path("claudia/cc_agents")
    if claudia_dir.exists():
        for agent_file in claudia_dir.glob("*.json"):
            try:
                with open(agent_file) as f:
                    agent_config = json.load(f)
                    
                if not agent_config.get("name"):
                    warnings.append(f"Agent {agent_file.name} missing name")
                    
                if not agent_config.get("systemPrompt"):
                    warnings.append(f"Agent {agent_file.name} missing systemPrompt")
                    
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON in {agent_file.name}")
    else:
        warnings.append("Claudia agents directory not found")
        
    # Report results
    print(f"\nValidation complete:")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  - {error}")
            
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
            
    return len(errors) == 0


if __name__ == "__main__":
    success = validate_mcp_configs()
    exit(0 if success else 1)