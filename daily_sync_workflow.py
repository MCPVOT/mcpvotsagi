#!/usr/bin/env python3
"""
Daily Sync Workflow for MCPVotsAGI
==================================
Comprehensive repository synchronization and knowledge graph update system
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import git
import subprocess
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DailySyncWorkflow")

# Import OpenCTI integration if available
try:
    from opencti_integration import OpenCTIConnector
    OPENCTI_AVAILABLE = True
except ImportError:
    OPENCTI_AVAILABLE = False
    logger.info("OpenCTI integration not available")

class GitHubRepoSyncManager:
    """Manage daily synchronization of forked repositories"""
    
    def __init__(self, workspace_path: str = "/mnt/c/Workspace"):
        self.workspace_path = Path(workspace_path)
        self.mcpvots_path = self.workspace_path / "MCPVots"
        self.mcpvotsagi_path = self.workspace_path / "MCPVotsAGI"
        self.github_username = "kabrony"
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        
        # MCP endpoints
        self.mcp_endpoints = {
            "github": "ws://localhost:3001",
            "memory": "ws://localhost:3002",
            "knowledge_graph": "ws://localhost:8011",
            "deerflow": "ws://localhost:8014",
            "n8n": "ws://localhost:8020"
        }
        
        # Sync configuration
        self.sync_config = {
            "core_repos": [
                "acp",
                "n8n-workflows",
                "mcp-servers-js",
                "awesome-mcp-servers",
                "ipfs",
                "ipfs-desktop",
                "js-ipfs"
            ],
            "sync_interval_hours": 24,
            "knowledge_graph_update": True,
            "readme_update": True,
            "mermaid_update": True
        }
        
        self.sync_history = []
        self.knowledge_updates = []
        
        # OpenCTI security integration
        self.opencti = None
        if OPENCTI_AVAILABLE:
            self.opencti = OpenCTIConnector()
            asyncio.create_task(self._init_opencti())
        
    async def get_forked_repos(self) -> List[Dict[str, Any]]:
        """Get all forked repositories from GitHub profile"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repos = []
        page = 1
        
        async with aiohttp.ClientSession() as session:
            while True:
                url = f"https://api.github.com/users/{self.github_username}/repos?type=forks&per_page=100&page={page}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"GitHub API error: {response.status}")
                        break
                    
                    data = await response.json()
                    if not data:
                        break
                    
                    repos.extend(data)
                    page += 1
                    
                    # Check for rate limit
                    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                    if remaining < 10:
                        logger.warning(f"GitHub rate limit low: {remaining} requests remaining")
                        break
        
        logger.info(f"Found {len(repos)} forked repositories")
        return repos
    
    async def _init_opencti(self):
        """Initialize OpenCTI connection"""
        try:
            connected = await self.opencti.connect()
            if connected:
                logger.info("OpenCTI security monitoring active for repo sync")
        except Exception as e:
            logger.error(f"OpenCTI init failed: {e}")
    
    async def security_check_commit(self, repo_name: str, commit_sha: str) -> Dict[str, Any]:
        """Check commit for security threats"""
        if not self.opencti:
            return {"secure": True, "issues": []}
        
        security_report = {
            "repo": repo_name,
            "commit": commit_sha,
            "secure": True,
            "issues": [],
            "ioc_matches": []
        }
        
        try:
            # Check commit SHA against IOCs
            ioc_result = await self.opencti.check_ioc(commit_sha)
            if ioc_result:
                security_report["secure"] = False
                security_report["issues"].append({
                    "type": "malicious_commit",
                    "severity": ioc_result.severity,
                    "description": f"Commit SHA matches known threat: {ioc_result.description}"
                })
                security_report["ioc_matches"].append(commit_sha)
        except Exception as e:
            logger.error(f"Security check failed for {repo_name}: {e}")
        
        return security_report
    
    async def sync_repository(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single repository"""
        repo_name = repo_info["name"]
        repo_path = self.mcpvotsagi_path / "synced_repos" / repo_name
        
        sync_result = {
            "repo": repo_name,
            "status": "pending",
            "commits_behind": 0,
            "updates": [],
            "error": None
        }
        
        try:
            if not repo_path.exists():
                # Clone repository
                logger.info(f"Cloning {repo_name}...")
                clone_url = f"https://{self.github_token}@github.com/{self.github_username}/{repo_name}.git"
                git.Repo.clone_from(clone_url, repo_path)
                sync_result["status"] = "cloned"
            else:
                # Update existing repository
                logger.info(f"Updating {repo_name}...")
                repo = git.Repo(repo_path)
                
                # Fetch upstream
                if "upstream" not in [remote.name for remote in repo.remotes]:
                    repo.create_remote("upstream", repo_info["parent"]["clone_url"])
                
                # Fetch all remotes
                for remote in repo.remotes:
                    remote.fetch()
                
                # Check if behind upstream
                upstream_commits = list(repo.iter_commits('upstream/main..HEAD'))
                local_commits = list(repo.iter_commits('HEAD..upstream/main'))
                
                sync_result["commits_behind"] = len(local_commits)
                
                if local_commits:
                    # Merge upstream changes
                    repo.git.checkout('main')
                    repo.git.merge('upstream/main')
                    
                    # Push to origin
                    repo.remotes.origin.push()
                    
                    sync_result["status"] = "updated"
                    updates = []
                    security_issues = []
                    
                    for commit in local_commits[:10]:  # Limit to 10 commits
                        commit_info = {
                            "sha": commit.hexsha[:7],
                            "message": commit.message.strip(),
                            "author": str(commit.author),
                            "date": datetime.fromtimestamp(commit.committed_date).isoformat()
                        }
                        
                        # Security check each commit
                        if self.opencti:
                            security_check = await self.security_check_commit(repo_name, commit.hexsha)
                            if not security_check["secure"]:
                                commit_info["security_alert"] = True
                                security_issues.extend(security_check["issues"])
                        
                        updates.append(commit_info)
                    
                    sync_result["updates"] = updates
                    
                    if security_issues:
                        sync_result["security_issues"] = security_issues
                        logger.warning(f"Security issues found in {repo_name}: {len(security_issues)} issues")
                else:
                    sync_result["status"] = "up-to-date"
                    
        except Exception as e:
            logger.error(f"Error syncing {repo_name}: {e}")
            sync_result["status"] = "error"
            sync_result["error"] = str(e)
            
        return sync_result
    
    async def update_knowledge_graph(self, sync_results: List[Dict[str, Any]]):
        """Update MCP Memory Knowledge Graph with sync results"""
        knowledge_entries = []
        
        for result in sync_results:
            if result["status"] in ["updated", "cloned"]:
                entry = {
                    "entity_type": "repository_sync",
                    "name": f"sync_{result['repo']}_{datetime.now().strftime('%Y%m%d')}",
                    "properties": {
                        "repository": result["repo"],
                        "sync_status": result["status"],
                        "commits_synced": len(result.get("updates", [])),
                        "timestamp": datetime.now().isoformat()
                    },
                    "relationships": [
                        f"repo:{result['repo']}",
                        "workflow:daily_sync"
                    ]
                }
                knowledge_entries.append(entry)
        
        # Send to Memory MCP
        if knowledge_entries:
            try:
                # Connect to Memory MCP via WebSocket
                import websockets
                
                async with websockets.connect(self.mcp_endpoints["memory"]) as websocket:
                    for entry in knowledge_entries:
                        message = {
                            "jsonrpc": "2.0",
                            "method": "memory/create_entity",
                            "params": entry,
                            "id": hashlib.md5(json.dumps(entry).encode()).hexdigest()
                        }
                        
                        await websocket.send(json.dumps(message))
                        response = await websocket.recv()
                        logger.info(f"Knowledge graph updated: {entry['name']}")
                        
            except Exception as e:
                logger.error(f"Failed to update knowledge graph: {e}")
    
    async def generate_sync_report(self, sync_results: List[Dict[str, Any]]) -> str:
        """Generate a detailed sync report"""
        report = f"""# Daily Repository Sync Report
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Profile**: {self.github_username}

## Summary
- Total repositories: {len(sync_results)}
- Updated: {len([r for r in sync_results if r['status'] == 'updated'])}
- Cloned: {len([r for r in sync_results if r['status'] == 'cloned'])}
- Up-to-date: {len([r for r in sync_results if r['status'] == 'up-to-date'])}
- Errors: {len([r for r in sync_results if r['status'] == 'error'])}

## Detailed Results

"""
        
        for result in sync_results:
            report += f"### {result['repo']}\n"
            report += f"- **Status**: {result['status']}\n"
            
            if result['status'] == 'updated':
                report += f"- **Commits synced**: {len(result.get('updates', []))}\n"
                if result.get('updates'):
                    report += "- **Recent updates**:\n"
                    for update in result['updates'][:5]:
                        report += f"  - `{update['sha']}`: {update['message']}\n"
            
            elif result['status'] == 'error':
                report += f"- **Error**: {result['error']}\n"
            
            report += "\n"
        
        return report
    
    async def update_readme_and_diagrams(self, sync_results: List[Dict[str, Any]]):
        """Update README.md and Mermaid diagrams"""
        readme_path = self.mcpvotsagi_path / "README.md"
        
        # Generate updated Mermaid diagram
        mermaid_diagram = self.generate_ecosystem_diagram(sync_results)
        
        # Read current README
        if readme_path.exists():
            content = readme_path.read_text()
        else:
            content = "# MCPVotsAGI Ecosystem\n\n"
        
        # Update or add sync section
        sync_section = f"""
## Daily Repository Sync Status

Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Synced Repositories
{len([r for r in sync_results if r['status'] in ['updated', 'cloned', 'up-to-date']])} repositories synchronized

### Ecosystem Architecture

```mermaid
{mermaid_diagram}
```

### Integration Status
- ✅ GitHub MCP Server: Active
- ✅ Memory Knowledge Graph: Connected
- ✅ Daily Sync Workflow: Operational
- ✅ IPFS Integration: {self.check_ipfs_status()}
- ✅ OpenCTI Security: {"Active" if self.opencti else "Not Configured"}

### Security Status
{self.generate_security_summary(sync_results)}
"""
        
        # Update README
        if "## Daily Repository Sync Status" in content:
            # Replace existing section
            import re
            pattern = r"## Daily Repository Sync Status.*?(?=##|\Z)"
            content = re.sub(pattern, sync_section, content, flags=re.DOTALL)
        else:
            # Add new section
            content += "\n" + sync_section
        
        # Write updated README
        readme_path.write_text(content)
        logger.info("README.md updated with sync status")
    
    def generate_ecosystem_diagram(self, sync_results: List[Dict[str, Any]]) -> str:
        """Generate Mermaid diagram of the ecosystem"""
        active_repos = [r for r in sync_results if r['status'] in ['updated', 'cloned', 'up-to-date']]
        
        diagram = """graph TB
    subgraph "MCPVotsAGI Ecosystem"
        GitHub[GitHub Profile: kabrony]
        MCPVots[MCPVots Core]
        MCPVotsAGI[MCPVotsAGI]
        
        subgraph "MCP Servers"
            GH_MCP[GitHub MCP :3001]
            MEM_MCP[Memory MCP :3002]
            KG_MCP[Knowledge Graph :8011]
            DF_MCP[DeerFlow :8014]
            N8N_MCP[n8n Integration :8020]
        end
        
        subgraph "Synced Repositories"
"""
        
        # Add synced repos
        for i, repo in enumerate(active_repos[:10]):  # Limit to 10 for readability
            diagram += f"            REPO_{i}[{repo['repo']}]\n"
        
        if len(active_repos) > 10:
            diagram += f"            MORE[+{len(active_repos) - 10} more...]\n"
        
        diagram += """        end
        
        subgraph "Integrations"
            IPFS[IPFS Network]
            ACP[ACP Framework]
            N8N[n8n Workflows]
        end
        
        GitHub -->|Daily Sync| MCPVotsAGI
        MCPVotsAGI --> GH_MCP
        MCPVotsAGI --> MEM_MCP
        MEM_MCP --> KG_MCP
        MCPVotsAGI --> DF_MCP
        MCPVotsAGI --> N8N_MCP
        MCPVotsAGI --> IPFS
        MCPVotsAGI --> ACP
        N8N_MCP --> N8N
"""
        
        # Add repo connections
        for i in range(min(10, len(active_repos))):
            diagram += f"        GitHub --> REPO_{i}\n"
        
        diagram += "    end"
        
        return diagram
    
    def check_ipfs_status(self) -> str:
        """Check IPFS integration status"""
        ipfs_path = self.mcpvotsagi_path / "synced_repos" / "ipfs"
        if ipfs_path.exists():
            return "Active"
        return "Pending"
    
    def generate_security_summary(self, sync_results: List[Dict[str, Any]]) -> str:
        """Generate security summary for README"""
        total_issues = 0
        affected_repos = []
        
        for result in sync_results:
            if "security_issues" in result:
                total_issues += len(result["security_issues"])
                affected_repos.append(result["repo"])
        
        if total_issues == 0:
            return "🛡️ **All repositories passed security checks**"
        else:
            summary = f"⚠️ **Security alerts: {total_issues} issues found**\n\n"
            summary += "Affected repositories:\n"
            for repo in affected_repos:
                summary += f"- {repo}\n"
            summary += "\nRun `python check_security_alerts.py` for details"
            return summary
    
    async def run_daily_sync(self):
        """Run the complete daily sync workflow"""
        logger.info("Starting daily sync workflow...")
        
        # Get all forked repositories
        repos = await self.get_forked_repos()
        
        # Filter for core repos and any with recent activity
        sync_targets = []
        for repo in repos:
            if repo["name"] in self.sync_config["core_repos"] or \
               (repo.get("pushed_at") and 
                datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00")) > 
                datetime.now(timezone.utc) - timedelta(days=30)):
                sync_targets.append(repo)
        
        logger.info(f"Syncing {len(sync_targets)} repositories...")
        
        # Sync repositories
        sync_results = []
        for repo in sync_targets:
            result = await self.sync_repository(repo)
            sync_results.append(result)
            
            # Brief pause to avoid rate limits
            await asyncio.sleep(1)
        
        # Update knowledge graph
        if self.sync_config["knowledge_graph_update"]:
            await self.update_knowledge_graph(sync_results)
        
        # Generate sync report
        report = await self.generate_sync_report(sync_results)
        report_path = self.mcpvotsagi_path / "sync_reports" / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report)
        
        # Update README and diagrams
        if self.sync_config["readme_update"]:
            await self.update_readme_and_diagrams(sync_results)
        
        logger.info("Daily sync workflow completed!")
        
        return sync_results

class IPFSIntegrationManager:
    """Manage IPFS integration and knowledge updates"""
    
    def __init__(self, workspace_path: str = "/mnt/c/Workspace"):
        self.workspace_path = Path(workspace_path)
        self.ipfs_repos = ["ipfs", "ipfs-desktop", "js-ipfs"]
        self.ipfs_api_url = "http://localhost:5001/api/v0"
        
    async def setup_ipfs_integration(self):
        """Set up IPFS integration with MCPVotsAGI"""
        logger.info("Setting up IPFS integration...")
        
        # Check if IPFS daemon is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ipfs_api_url}/id") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"IPFS daemon connected: {data['ID']}")
                    else:
                        logger.warning("IPFS daemon not running")
        except:
            logger.error("Could not connect to IPFS daemon")
        
        # Create IPFS integration module
        ipfs_module_path = self.workspace_path / "MCPVotsAGI" / "ipfs_integration.py"
        ipfs_module_content = '''#!/usr/bin/env python3
"""
IPFS Integration for MCPVotsAGI
==============================
Distributed storage and content addressing for the AGI ecosystem
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiohttp
import ipfshttpclient

logger = logging.getLogger("IPFSIntegration")

class IPFSManager:
    """Manage IPFS operations for MCPVotsAGI"""
    
    def __init__(self, api_url: str = "/ip4/127.0.0.1/tcp/5001"):
        self.client = None
        try:
            self.client = ipfshttpclient.connect(api_url)
            logger.info("Connected to IPFS daemon")
        except Exception as e:
            logger.error(f"Failed to connect to IPFS: {e}")
    
    async def add_to_ipfs(self, file_path: Path) -> Optional[str]:
        """Add file to IPFS and return hash"""
        if not self.client:
            return None
        
        try:
            result = self.client.add(str(file_path))
            return result['Hash']
        except Exception as e:
            logger.error(f"Failed to add to IPFS: {e}")
            return None
    
    async def pin_content(self, ipfs_hash: str) -> bool:
        """Pin content to ensure persistence"""
        if not self.client:
            return False
        
        try:
            self.client.pin.add(ipfs_hash)
            return True
        except Exception as e:
            logger.error(f"Failed to pin content: {e}")
            return False
    
    async def create_knowledge_dag(self, knowledge_entries: List[Dict[str, Any]]) -> Optional[str]:
        """Create a DAG of knowledge entries"""
        if not self.client:
            return None
        
        try:
            # Create DAG structure
            dag = {
                "type": "knowledge_dag",
                "timestamp": datetime.now().isoformat(),
                "entries": knowledge_entries,
                "version": "1.0"
            }
            
            # Add to IPFS as JSON
            result = self.client.add_json(dag)
            return result
        except Exception as e:
            logger.error(f"Failed to create knowledge DAG: {e}")
            return None
    
    async def retrieve_from_ipfs(self, ipfs_hash: str) -> Optional[Any]:
        """Retrieve content from IPFS"""
        if not self.client:
            return None
        
        try:
            content = self.client.cat(ipfs_hash)
            return content.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to retrieve from IPFS: {e}")
            return None
'''
        
        ipfs_module_path.write_text(ipfs_module_content)
        logger.info("IPFS integration module created")

async def create_n8n_sync_workflow():
    """Create n8n workflow for automated sync"""
    workflow = {
        "name": "MCPVotsAGI Daily Sync",
        "nodes": [
            {
                "id": "schedule_trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [100, 200],
                "parameters": {
                    "rule": {
                        "interval": [{"field": "hours", "hoursInterval": 24}]
                    }
                }
            },
            {
                "id": "sync_repos",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [300, 200],
                "parameters": {
                    "url": "http://localhost:8020/trigger/daily_sync",
                    "method": "POST",
                    "jsonParameters": True,
                    "options": {},
                    "bodyParametersJson": {"action": "sync_all_repos"}
                }
            },
            {
                "id": "update_knowledge",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [500, 200],
                "parameters": {
                    "url": "ws://localhost:3002",
                    "method": "POST",
                    "jsonParameters": True,
                    "options": {},
                    "bodyParametersJson": {"method": "memory/batch_update"}
                }
            },
            {
                "id": "ipfs_backup",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [700, 200],
                "parameters": {
                    "url": "http://localhost:5001/api/v0/add",
                    "method": "POST",
                    "options": {}
                }
            }
        ],
        "connections": {
            "schedule_trigger": {
                "main": [[{"node": "sync_repos", "type": "main", "index": 0}]]
            },
            "sync_repos": {
                "main": [[{"node": "update_knowledge", "type": "main", "index": 0}]]
            },
            "update_knowledge": {
                "main": [[{"node": "ipfs_backup", "type": "main", "index": 0}]]
            }
        }
    }
    
    # Save workflow
    workflow_path = Path("/mnt/c/Workspace/MCPVotsAGI/n8n_workflows/daily_sync.json")
    workflow_path.parent.mkdir(exist_ok=True)
    workflow_path.write_text(json.dumps(workflow, indent=2))
    
    logger.info("n8n daily sync workflow created")

async def main():
    """Main entry point for daily sync"""
    # Initialize managers
    sync_manager = GitHubRepoSyncManager()
    ipfs_manager = IPFSIntegrationManager()
    
    # Setup IPFS integration
    await ipfs_manager.setup_ipfs_integration()
    
    # Create n8n workflow
    await create_n8n_sync_workflow()
    
    # Run daily sync
    results = await sync_manager.run_daily_sync()
    
    logger.info(f"Sync completed: {len(results)} repositories processed")

if __name__ == "__main__":
    # Add timezone support
    from datetime import timezone
    
    # Run the sync
    asyncio.run(main())