#!/usr/bin/env python3
"""
MCPVotsAGI Ecosystem Index
=========================
Comprehensive indexing and analysis of the entire ecosystem
"""

import os
import json
import ast
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Set
import hashlib
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcosystemIndex")

class EcosystemIndexer:
    """Index and analyze the entire MCPVotsAGI ecosystem"""
    
    def __init__(self):
        self.workspace = Path("C:/Workspace") if os.name == 'nt' else Path("/mnt/c/Workspace")
        self.mcpvots_path = self.workspace / "MCPVots"
        self.mcpvotsagi_path = self.workspace / "MCPVotsAGI"
        
        # Index database
        self.index_db = self.mcpvotsagi_path / "ecosystem_index.db"
        self.init_database()
        
        # Analysis results
        self.ecosystem_map = {
            "services": {},
            "dependencies": {},
            "capabilities": {},
            "integrations": {},
            "configurations": {},
            "workflows": {},
            "knowledge_bases": {}
        }
        
    def init_database(self):
        """Initialize index database"""
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        # Files index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                file_type TEXT,
                size INTEGER,
                last_modified TIMESTAMP,
                content_hash TEXT,
                analysis TEXT
            )
        ''')
        
        # Services index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id TEXT PRIMARY KEY,
                name TEXT,
                port INTEGER,
                file_path TEXT,
                dependencies TEXT,
                capabilities TEXT,
                configuration TEXT
            )
        ''')
        
        # Dependencies graph
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                target TEXT,
                dep_type TEXT,
                file_path TEXT
            )
        ''')
        
        # Capabilities index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capabilities (
                capability_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                providers TEXT,
                consumers TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for services, dependencies, etc."""
        analysis = {
            "imports": [],
            "classes": [],
            "functions": [],
            "services": [],
            "ports": [],
            "dependencies": [],
            "capabilities": []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Analyze imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis["imports"].append(f"{module}.{alias.name}")
                
                # Analyze classes
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                
                # Analyze functions
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args]
                    })
                
                # Look for port definitions
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and 'port' in target.id.lower():
                            if isinstance(node.value, ast.Constant):
                                analysis["ports"].append(node.value.value)
            
            # Extract service definitions from content
            if "port" in content and ("server" in content.lower() or "service" in content.lower()):
                analysis["services"].append(file_path.stem)
            
            # Extract capabilities from docstrings and comments
            if "capabilities" in content.lower():
                # Simple extraction - in production would use more sophisticated parsing
                import re
                caps = re.findall(r'capabilities["\']?\s*[:=]\s*\[(.*?)\]', content, re.DOTALL)
                for cap_list in caps:
                    capabilities = re.findall(r'["\']([^"\']+)["\']', cap_list)
                    analysis["capabilities"].extend(capabilities)
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
        
        return analysis
    
    def analyze_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JSON configuration files"""
        analysis = {
            "type": "configuration",
            "services": [],
            "settings": {}
        }
        
        try:
            data = json.loads(file_path.read_text())
            
            # Analyze MCP config
            if "servers" in data:
                for server in data["servers"]:
                    analysis["services"].append({
                        "name": server.get("name"),
                        "url": server.get("url"),
                        "capabilities": server.get("capabilities", [])
                    })
            
            # Store all settings
            analysis["settings"] = data
            
        except Exception as e:
            logger.error(f"Error analyzing JSON {file_path}: {e}")
        
        return analysis
    
    def index_file(self, file_path: Path):
        """Index a single file"""
        relative_path = file_path.relative_to(self.workspace)
        
        # Calculate content hash
        content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        
        # Get file stats
        stats = file_path.stat()
        
        # Analyze based on file type
        analysis = {}
        if file_path.suffix == '.py':
            analysis = self.analyze_python_file(file_path)
        elif file_path.suffix == '.json':
            analysis = self.analyze_json_file(file_path)
        
        # Store in database
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (file_path, file_type, size, last_modified, content_hash, analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(relative_path),
            file_path.suffix,
            stats.st_size,
            datetime.fromtimestamp(stats.st_mtime),
            content_hash,
            json.dumps(analysis)
        ))
        
        conn.commit()
        conn.close()
        
        return analysis
    
    def build_dependency_graph(self):
        """Build complete dependency graph"""
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        # Get all Python files and their analyses
        cursor.execute('SELECT file_path, analysis FROM files WHERE file_type = ?', ('.py',))
        
        for file_path, analysis_json in cursor.fetchall():
            analysis = json.loads(analysis_json)
            
            # Track import dependencies
            for imp in analysis.get("imports", []):
                cursor.execute('''
                    INSERT INTO dependencies (source, target, dep_type, file_path)
                    VALUES (?, ?, ?, ?)
                ''', (file_path, imp, "import", file_path))
        
        conn.commit()
        conn.close()
    
    def identify_services(self):
        """Identify all services in the ecosystem"""
        services = {}
        
        # Known service patterns
        service_files = [
            "oracle_agi_ultimate_unified.py",
            "mcp_github_server.py",
            "enhanced_memory_mcp_server.py",
            "trilogy_agi_gateway.py",
            "dgm_evolution_server.py",
            "deerflow_server.py",
            "gemini_cli_http_server.py",
            "ollama_code_review_mcp.py"
        ]
        
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        for service_file in service_files:
            cursor.execute(
                'SELECT file_path, analysis FROM files WHERE file_path LIKE ?',
                (f'%{service_file}',)
            )
            
            result = cursor.fetchone()
            if result:
                file_path, analysis_json = result
                analysis = json.loads(analysis_json)
                
                service_id = Path(service_file).stem
                
                services[service_id] = {
                    "file": file_path,
                    "ports": analysis.get("ports", []),
                    "capabilities": analysis.get("capabilities", []),
                    "dependencies": analysis.get("imports", [])
                }
                
                # Store in services table
                cursor.execute('''
                    INSERT OR REPLACE INTO services
                    (service_id, name, port, file_path, dependencies, capabilities, configuration)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    service_id,
                    service_id.replace('_', ' ').title(),
                    analysis.get("ports", [None])[0] if analysis.get("ports") else None,
                    file_path,
                    json.dumps(analysis.get("imports", [])),
                    json.dumps(analysis.get("capabilities", [])),
                    "{}"
                ))
        
        conn.commit()
        conn.close()
        
        return services
    
    def analyze_ecosystem(self):
        """Perform complete ecosystem analysis"""
        logger.info("Starting ecosystem analysis...")
        
        # Index all Python files
        python_files = list(self.mcpvots_path.rglob("*.py")) + \
                      list(self.mcpvotsagi_path.rglob("*.py"))
        
        logger.info(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if not any(skip in str(file_path) for skip in ['__pycache__', '.git', 'node_modules']):
                self.index_file(file_path)
        
        # Index configuration files
        config_files = list(self.mcpvots_path.rglob("*.json")) + \
                      list(self.mcpvotsagi_path.rglob("*.json"))
        
        logger.info(f"Found {len(config_files)} configuration files")
        
        for file_path in config_files:
            if not any(skip in str(file_path) for skip in ['node_modules', '.git']):
                self.index_file(file_path)
        
        # Build dependency graph
        self.build_dependency_graph()
        
        # Identify services
        services = self.identify_services()
        
        # Generate ecosystem map
        self.ecosystem_map["services"] = services
        
        logger.info("Ecosystem analysis complete!")
        
        return self.ecosystem_map
    
    def generate_report(self) -> str:
        """Generate comprehensive ecosystem report"""
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM services')
        total_services = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM dependencies')
        total_dependencies = cursor.fetchone()[0]
        
        # Get services list
        cursor.execute('SELECT service_id, name, port FROM services')
        services = cursor.fetchall()
        
        conn.close()
        
        report = f"""# MCPVotsAGI Ecosystem Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total Files Indexed: {total_files}
- Total Services: {total_services}
- Total Dependencies: {total_dependencies}

## Services

| Service ID | Name | Port |
|------------|------|------|
"""
        
        for service_id, name, port in services:
            report += f"| {service_id} | {name} | {port or 'N/A'} |\n"
        
        report += """
## Key Findings

### Core Infrastructure
- **Oracle AGI Core**: Main orchestration service (Port 8888)
- **Memory MCP**: Knowledge graph and persistent storage (Port 3002)
- **Trilogy AGI**: Multi-model AI gateway (Port 8000)

### AI/LLM Services
- **Ollama**: Local LLM hosting (Port 11434)
- **Gemini CLI**: Google Gemini integration (Port 8015)
- **DeepSeek**: Advanced reasoning via Ollama

### Automation & Workflows
- **DeerFlow**: Workflow orchestration (Port 8014)
- **n8n**: Visual workflow automation (Port 5678)
- **DGM Evolution**: Self-improving AI system (Port 8013)

### Integration Points
- **GitHub MCP**: Repository management (Port 3001)
- **Solana MCP**: Blockchain integration (Port 3005)
- **IPFS**: Distributed storage (Port 5001)

## Recommendations

1. **Service Health Monitoring**: Implement continuous health checks for all services
2. **Resource Optimization**: Monitor and optimize memory/CPU usage per service
3. **Dependency Management**: Ensure all service dependencies are properly configured
4. **Security Hardening**: Review and secure all exposed ports and endpoints
5. **Documentation**: Keep service documentation up-to-date with changes

## Next Steps

1. Run `python ecosystem_manager.py start` to launch all services
2. Access dashboard at http://localhost:3010
3. Monitor service health and performance
4. Enable auto-start for production deployment
"""
        
        return report
    
    def export_to_knowledge_graph(self):
        """Export ecosystem analysis to knowledge graph"""
        conn = sqlite3.connect(self.index_db)
        cursor = conn.cursor()
        
        # Get all services
        cursor.execute('SELECT * FROM services')
        services = cursor.fetchall()
        
        # Get all dependencies
        cursor.execute('SELECT * FROM dependencies')
        dependencies = cursor.fetchall()
        
        conn.close()
        
        # Create knowledge graph structure
        knowledge_graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Add service nodes
        for service in services:
            node = {
                "id": service[0],
                "type": "service",
                "properties": {
                    "name": service[1],
                    "port": service[2],
                    "file_path": service[3],
                    "capabilities": json.loads(service[5] or "[]")
                }
            }
            knowledge_graph["nodes"].append(node)
        
        # Add dependency edges
        for dep in dependencies:
            edge = {
                "source": dep[1],
                "target": dep[2],
                "type": dep[3]
            }
            knowledge_graph["edges"].append(edge)
        
        # Save to file
        kg_path = self.mcpvotsagi_path / "ecosystem_knowledge_graph.json"
        kg_path.write_text(json.dumps(knowledge_graph, indent=2))
        
        logger.info(f"Knowledge graph exported to {kg_path}")
        
        return knowledge_graph

def main():
    """Run ecosystem indexing"""
    indexer = EcosystemIndexer()
    
    # Analyze ecosystem
    ecosystem_map = indexer.analyze_ecosystem()
    
    # Generate report
    report = indexer.generate_report()
    report_path = indexer.mcpvotsagi_path / "ECOSYSTEM_ANALYSIS.md"
    report_path.write_text(report)
    
    logger.info(f"Report saved to {report_path}")
    
    # Export to knowledge graph
    indexer.export_to_knowledge_graph()
    
    print("\n" + "="*60)
    print("MCPVotsAGI Ecosystem Analysis Complete!")
    print("="*60)
    print(f"\nFiles indexed: {len(ecosystem_map.get('services', {}))}")
    print(f"Services identified: {len(ecosystem_map.get('services', {}))}")
    print(f"\nReports generated:")
    print(f"  - {report_path}")
    print(f"  - {indexer.mcpvotsagi_path / 'ecosystem_knowledge_graph.json'}")
    print(f"  - {indexer.index_db}")

if __name__ == "__main__":
    main()