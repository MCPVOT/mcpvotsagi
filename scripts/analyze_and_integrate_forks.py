#!/usr/bin/env python3
"""Analyze forked repositories and create integration plan for MCPVotsAgi"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any

def get_github_repos(username: str = 'kabrony') -> List[Dict[str, Any]]:
    """Get all repositories for a GitHub user using git CLI"""
    print(f"Analyzing GitHub repositories for {username}...")

    # Use GitHub CLI if available, otherwise use git remote
    repos = []

    try:
        # Try to get repo list from GitHub API using curl
        import requests

        # Get user's repositories
        for page in range(1, 5):  # Check first 5 pages
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
            response = requests.get(url)

            if response.status_code == 200:
                page_repos = response.json()
                if not page_repos:
                    break
                repos.extend(page_repos)
            else:
                print(f"Error fetching repos: {response.status_code}")
                break

    except Exception as e:
        print(f"Error: {e}")
        print("Please install 'requests' or use GitHub CLI")

    return repos

def analyze_forked_repos(repos: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Analyze and categorize forked repositories"""

    categorized = {
        'ai_ml': [],
        'blockchain': [],
        'trading': [],
        'data_processing': [],
        'devops': [],
        'security': [],
        'other': []
    }

    # Keywords for categorization
    ai_keywords = ['ai', 'ml', 'llm', 'gpt', 'neural', 'model', 'deep', 'learning', 'bert', 'transformer']
    blockchain_keywords = ['blockchain', 'crypto', 'defi', 'web3', 'solana', 'ethereum', 'smart', 'contract', 'nft']
    trading_keywords = ['trade', 'trading', 'finance', 'market', 'bot', 'algorithm', 'quant', 'forex', 'stock']
    data_keywords = ['data', 'pipeline', 'etl', 'stream', 'process', 'analytics', 'database', 'api']
    devops_keywords = ['docker', 'kubernetes', 'ci', 'cd', 'deploy', 'infra', 'terraform', 'ansible']
    security_keywords = ['security', 'audit', 'pentest', 'vulnerability', 'cyber', 'auth', 'encrypt']

    for repo in repos:
        if not repo.get('fork', False):
            continue

        name = repo.get('name', '').lower()
        description = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]

        # Combine all text for searching
        search_text = f"{name} {description} {' '.join(topics)}"

        # Categorize based on keywords
        if any(kw in search_text for kw in ai_keywords):
            categorized['ai_ml'].append(repo)
        elif any(kw in search_text for kw in blockchain_keywords):
            categorized['blockchain'].append(repo)
        elif any(kw in search_text for kw in trading_keywords):
            categorized['trading'].append(repo)
        elif any(kw in search_text for kw in data_keywords):
            categorized['data_processing'].append(repo)
        elif any(kw in search_text for kw in devops_keywords):
            categorized['devops'].append(repo)
        elif any(kw in search_text for kw in security_keywords):
            categorized['security'].append(repo)
        else:
            categorized['other'].append(repo)

    return categorized

def create_integration_recommendations(categorized: Dict[str, List[Dict[str, Any]]]) -> str:
    """Create specific integration recommendations for MCPVotsAgi"""

    recommendations = []

    # AI/ML Recommendations
    if categorized['ai_ml']:
        recommendations.append("""
## AI/ML Integration Recommendations

### High Priority Integrations:""")

        for repo in categorized['ai_ml'][:5]:
            recommendations.append(f"""
- **{repo['name']}**: {repo.get('description', 'No description')}
  - Integration Point: `src/integrations/ai/`
  - Use Case: Enhance MCPVotsAgi's AI capabilities
  - Implementation: Create wrapper in `unified_model_hub.py`""")

    # Blockchain Recommendations
    if categorized['blockchain']:
        recommendations.append("""
## Blockchain Integration Recommendations

### Enhance Multi-Chain Support:""")

        for repo in categorized['blockchain'][:5]:
            recommendations.append(f"""
- **{repo['name']}**: {repo.get('description', 'No description')}
  - Integration Point: `src/integrations/blockchain/`
  - Use Case: Expand blockchain capabilities
  - Implementation: Add to `multi_chain_manager.py`""")

    # Trading Recommendations
    if categorized['trading']:
        recommendations.append("""
## Trading Strategy Recommendations

### Advanced Trading Algorithms:""")

        for repo in categorized['trading'][:5]:
            recommendations.append(f"""
- **{repo['name']}**: {repo.get('description', 'No description')}
  - Integration Point: `src/integrations/trading/`
  - Use Case: New trading strategies
  - Implementation: Extend `strategy_manager.py`""")

    return '\n'.join(recommendations)

def create_integration_script(repo: Dict[str, Any], category: str) -> str:
    """Create an integration script for a specific repository"""

    repo_name = repo['name']
    safe_name = repo_name.replace('-', '_')

    return f"""#!/usr/bin/env python3
\"\"\"Integration script for {repo_name}\"\"\"

import sys
import os
from pathlib import Path

# Add the forked repo to path
sys.path.insert(0, str(Path(__file__).parent / 'external' / '{category}' / '{repo_name}'))

from src.integrations.external.base_wrapper import BaseExternalWrapper

class {safe_name.title()}Integration(BaseExternalWrapper):
    \"\"\"Integration wrapper for {repo_name}\"\"\"

    def __init__(self):
        super().__init__('{repo_name}', {{
            'category': '{category}',
            'description': '''{repo.get('description', '')}''',
            'url': '{repo.get('html_url', '')}',
            'topics': {repo.get('topics', [])}
        }})

    async def _initialize_external(self):
        \"\"\"Initialize the {repo_name} integration\"\"\"
        try:
            # TODO: Import main module from {repo_name}
            # from {safe_name} import MainClass
            # self.instance = MainClass()
            pass
        except ImportError as e:
            self.logger.error(f"Failed to import {repo_name}: {{e}}")
            raise

    async def execute(self, command: str, **kwargs):
        \"\"\"Execute commands on {repo_name}\"\"\"
        # TODO: Implement command execution
        return {{'status': 'not_implemented', 'command': command}}

    async def _perform_health_check(self):
        \"\"\"Check health of {repo_name} integration\"\"\"
        return {{
            'status': 'healthy' if self._initialized else 'not_initialized',
            'integration': '{repo_name}'
        }}

# Usage example
if __name__ == '__main__':
    import asyncio

    async def test():
        integration = {safe_name.title()}Integration()
        await integration.initialize()
        result = await integration.execute('test')
        print(f"Result: {{result}}")

    asyncio.run(test())
"""

def generate_integration_report(username: str = 'kabrony'):
    """Generate comprehensive integration report"""

    print(f"Analyzing repositories for {username}...")

    # Get repositories
    repos = get_github_repos(username)

    if not repos:
        print("No repositories found!")
        return

    # Filter forked repos
    forked_repos = [r for r in repos if r.get('fork', False)]
    print(f"Found {len(forked_repos)} forked repositories")

    # Categorize repos
    categorized = analyze_forked_repos(repos)

    # Create report
    report = f"""# MCPVotsAgi Forked Repository Integration Report

Generated for: {username}
Total Repositories: {len(repos)}
Forked Repositories: {len(forked_repos)}

## Repository Categories

"""

    for category, category_repos in categorized.items():
        if category_repos:
            report += f"### {category.replace('_', ' ').title()} ({len(category_repos)} repos)\n\n"

            for repo in category_repos[:10]:  # Show top 10
                report += f"- **[{repo['name']}]({repo['html_url']})**: {repo.get('description', 'No description')}\n"
                report += f"  - Language: {repo.get('language', 'Unknown')}\n"
                report += f"  - Stars: {repo.get('stargazers_count', 0)}\n"
                report += f"  - Last Updated: {repo.get('updated_at', 'Unknown')}\n\n"

            if len(category_repos) > 10:
                report += f"  *...and {len(category_repos) - 10} more*\n\n"

    # Add recommendations
    report += "\n" + create_integration_recommendations(categorized)

    # Add implementation guide
    report += """

## Implementation Guide

### Step 1: Add Repository as Submodule
```bash
git submodule add https://github.com/{username}/{repo_name} external/{category}/{repo_name}
```

### Step 2: Create Integration Wrapper
Use the generated integration scripts in `src/integrations/external/`

### Step 3: Register with Ecosystem
Add to `ecosystem_manager.py`:
```python
from src.integrations.external.{category}.{repo_name}_wrapper import {RepoName}Integration

self.integrations['{repo_name}'] = {RepoName}Integration()
```

### Step 4: Test Integration
```bash
python -m pytest tests/test_{repo_name}_integration.py
```

## Priority Integration List

Based on MCPVotsAgi's current capabilities, prioritize these integrations:

1. **AI/ML Models** - Enhance AGI capabilities
2. **Blockchain Tools** - Expand multi-chain support
3. **Trading Algorithms** - Improve trading strategies
4. **Data Processing** - Better data pipeline
5. **Security Tools** - Strengthen security posture
"""

    # Save report
    report_path = "FORKED_REPOS_INTEGRATION_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    # Create integration scripts for top repos
    script_dir = Path("src/integrations/external/generated")
    script_dir.mkdir(parents=True, exist_ok=True)

    scripts_created = 0
    for category, repos in categorized.items():
        for repo in repos[:3]:  # Top 3 per category
            script_path = script_dir / f"{repo['name']}_integration.py"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(create_integration_script(repo, category))
            scripts_created += 1

    print(f"Created {scripts_created} integration scripts in {script_dir}")

if __name__ == "__main__":
    generate_integration_report()