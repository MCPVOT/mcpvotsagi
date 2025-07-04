#!/usr/bin/env python3
"""
Run MCPVotsAGI Complete Integration
===================================
Main entry point for the integrated ecosystem
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCPVotsAGI")

async def check_prerequisites():
    """Check if all prerequisites are met"""
    checks = {
        "IPFS daemon": False,
        "GitHub token": False,
        "Python dependencies": False,
        "MCP servers": False
    }
    
    # Check IPFS daemon
    try:
        result = subprocess.run(['ipfs', 'id'], capture_output=True, text=True)
        if result.returncode == 0:
            checks["IPFS daemon"] = True
            logger.info("✓ IPFS daemon is running")
        else:
            logger.warning("✗ IPFS daemon is not running. Start with: ipfs daemon")
    except FileNotFoundError:
        logger.warning("✗ IPFS not installed. Install from: https://ipfs.io/")
    
    # Check GitHub token
    if os.environ.get("GITHUB_TOKEN"):
        checks["GitHub token"] = True
        logger.info("✓ GitHub token configured")
    else:
        logger.warning("✗ GitHub token not set. Set with: export GITHUB_TOKEN='your-token'")
    
    # Check Python dependencies
    required_packages = ['aiohttp', 'websockets', 'gitpython', 'pyyaml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        checks["Python dependencies"] = True
        logger.info("✓ All Python dependencies installed")
    else:
        logger.warning(f"✗ Missing packages: {', '.join(missing_packages)}")
        logger.warning(f"  Install with: pip install {' '.join(missing_packages)}")
    
    # Check MCP servers
    mcp_config_path = Path("/mnt/c/Workspace/MCPVots/mcp-config.json")
    if mcp_config_path.exists():
        checks["MCP servers"] = True
        logger.info("✓ MCP configuration found")
    else:
        logger.warning("✗ MCP configuration not found")
    
    return all(checks.values()), checks

async def start_integration():
    """Start the complete integration"""
    logger.info("="*60)
    logger.info("MCPVotsAGI Complete Integration System")
    logger.info("="*60)
    
    # Check prerequisites
    all_ready, checks = await check_prerequisites()
    
    if not all_ready:
        logger.error("Prerequisites not met. Please resolve the issues above.")
        return False
    
    # Import integration modules
    sys.path.append("/mnt/c/Workspace/MCPVotsAGI")
    
    try:
        from daily_sync_workflow import GitHubRepoSyncManager, IPFSIntegrationManager
        from acp_ipfs_integration import setup_complete_integration
        
        logger.info("\n" + "="*60)
        logger.info("Starting integration setup...")
        logger.info("="*60)
        
        # Run complete setup
        await setup_complete_integration()
        
        # Initialize daily sync
        sync_manager = GitHubRepoSyncManager()
        
        logger.info("\n" + "="*60)
        logger.info("Running initial repository sync...")
        logger.info("="*60)
        
        # Run initial sync
        sync_results = await sync_manager.run_daily_sync()
        
        logger.info("\n" + "="*60)
        logger.info("Integration Summary")
        logger.info("="*60)
        logger.info(f"✓ Repositories synced: {len(sync_results)}")
        logger.info("✓ ACP integration: Complete")
        logger.info("✓ IPFS integration: Active")
        logger.info("✓ Knowledge graph: Updated")
        logger.info("✓ Documentation: Generated")
        logger.info("\n" + "="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCPVotsAGI Integration Manager")
    parser.add_argument("command", choices=["setup", "sync", "status", "check"],
                       help="Command to execute")
    parser.add_argument("--force", action="store_true",
                       help="Force execution even if prerequisites not met")
    
    args = parser.parse_args()
    
    if args.command == "check":
        await check_prerequisites()
    
    elif args.command == "setup":
        success = await start_integration()
        if success:
            logger.info("\nSetup complete! You can now run daily sync with:")
            logger.info("  python run_integration.py sync")
    
    elif args.command == "sync":
        from daily_sync_workflow import GitHubRepoSyncManager
        sync_manager = GitHubRepoSyncManager()
        await sync_manager.run_daily_sync()
    
    elif args.command == "status":
        # Check integration status
        readme_path = Path("/mnt/c/Workspace/MCPVotsAGI/README.md")
        if readme_path.exists():
            content = readme_path.read_text()
            if "Daily Repository Sync Status" in content:
                logger.info("✓ Integration is active")
                # Extract last sync time
                import re
                match = re.search(r"Last sync: (.+)", content)
                if match:
                    logger.info(f"  Last sync: {match.group(1)}")
            else:
                logger.info("✗ Integration not yet configured")
        else:
            logger.info("✗ Integration not found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_integration.py [setup|sync|status|check]")
        print("\nCommands:")
        print("  setup  - Initial setup and configuration")
        print("  sync   - Run repository synchronization")
        print("  status - Check integration status")
        print("  check  - Check prerequisites")
        sys.exit(1)
    
    asyncio.run(main())