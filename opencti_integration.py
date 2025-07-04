#!/usr/bin/env python3
"""
OpenCTI Integration for MCPVotsAGI
==================================
Comprehensive threat intelligence and security monitoring
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import hashlib
from dataclasses import dataclass, asdict

logger = logging.getLogger("OpenCTI")

@dataclass
class ThreatIndicator:
    """Threat indicator from OpenCTI"""
    indicator_id: str
    pattern: str
    threat_type: str  # 'malware', 'ip', 'domain', 'hash', 'url'
    severity: str  # 'critical', 'high', 'medium', 'low'
    confidence: int  # 0-100
    first_seen: datetime
    last_seen: datetime
    description: str
    mitre_techniques: List[str]
    
@dataclass
class SecurityEvent:
    """Security event for the ecosystem"""
    event_id: str
    timestamp: datetime
    service_id: str
    event_type: str  # 'threat_detected', 'anomaly', 'vulnerability', 'incident'
    severity: str
    description: str
    ioc_matches: List[str]
    recommended_actions: List[str]

class OpenCTIConnector:
    """OpenCTI connector for threat intelligence"""
    
    def __init__(self, api_url: str = None, api_token: str = None):
        self.api_url = api_url or os.environ.get("OPENCTI_URL", "http://localhost:8080")
        self.api_token = api_token or os.environ.get("OPENCTI_TOKEN", "")
        self.session = None
        self.threat_cache = {}
        self.ioc_database = {}
        
        # STIX2 patterns for different threat types
        self.stix_patterns = {
            "malicious_ip": r"\[ipv4-addr:value = '(.+?)'\]",
            "malicious_domain": r"\[domain-name:value = '(.+?)'\]",
            "malicious_hash": r"\[file:hashes\.'(MD5|SHA-1|SHA-256)' = '(.+?)'\]",
            "malicious_url": r"\[url:value = '(.+?)'\]"
        }
        
    async def connect(self):
        """Connect to OpenCTI API"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        self.session = aiohttp.ClientSession(headers=headers)
        
        # Test connection
        try:
            async with self.session.get(f"{self.api_url}/graphql") as response:
                if response.status == 200:
                    logger.info("Connected to OpenCTI")
                    return True
                else:
                    logger.error(f"Failed to connect to OpenCTI: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"OpenCTI connection error: {e}")
            return False
    
    async def get_threat_indicators(self, limit: int = 100) -> List[ThreatIndicator]:
        """Get latest threat indicators from OpenCTI"""
        query = """
        query GetIndicators($limit: Int!) {
            indicators(first: $limit, orderBy: created_at, orderMode: desc) {
                edges {
                    node {
                        id
                        pattern
                        pattern_type
                        valid_from
                        valid_until
                        confidence
                        created
                        modified
                        description
                        killChainPhases {
                            edges {
                                node {
                                    kill_chain_name
                                    phase_name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"limit": limit}
        
        try:
            async with self.session.post(
                f"{self.api_url}/graphql",
                json={"query": query, "variables": variables}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    indicators = []
                    
                    for edge in data.get("data", {}).get("indicators", {}).get("edges", []):
                        node = edge["node"]
                        
                        # Determine threat type and severity
                        threat_type = self._classify_threat_type(node["pattern"])
                        severity = self._calculate_severity(node["confidence"])
                        
                        indicator = ThreatIndicator(
                            indicator_id=node["id"],
                            pattern=node["pattern"],
                            threat_type=threat_type,
                            severity=severity,
                            confidence=node["confidence"],
                            first_seen=datetime.fromisoformat(node["created"].replace("Z", "+00:00")),
                            last_seen=datetime.fromisoformat(node["modified"].replace("Z", "+00:00")),
                            description=node.get("description", ""),
                            mitre_techniques=self._extract_mitre_techniques(node)
                        )
                        
                        indicators.append(indicator)
                        self.threat_cache[indicator.indicator_id] = indicator
                    
                    return indicators
                    
        except Exception as e:
            logger.error(f"Failed to get threat indicators: {e}")
            return []
    
    def _classify_threat_type(self, pattern: str) -> str:
        """Classify threat type from STIX pattern"""
        if "ipv4-addr" in pattern or "ipv6-addr" in pattern:
            return "ip"
        elif "domain-name" in pattern:
            return "domain"
        elif "file:hashes" in pattern:
            return "hash"
        elif "url:value" in pattern:
            return "url"
        else:
            return "unknown"
    
    def _calculate_severity(self, confidence: int) -> str:
        """Calculate severity based on confidence score"""
        if confidence >= 90:
            return "critical"
        elif confidence >= 70:
            return "high"
        elif confidence >= 50:
            return "medium"
        else:
            return "low"
    
    def _extract_mitre_techniques(self, node: Dict) -> List[str]:
        """Extract MITRE ATT&CK techniques"""
        techniques = []
        for edge in node.get("killChainPhases", {}).get("edges", []):
            phase = edge["node"]
            if phase["kill_chain_name"] == "mitre-attack":
                techniques.append(phase["phase_name"])
        return techniques
    
    async def check_ioc(self, value: str) -> Optional[ThreatIndicator]:
        """Check if a value matches any IOC"""
        # Check cache first
        for indicator in self.threat_cache.values():
            if value in indicator.pattern:
                return indicator
        
        # Query OpenCTI for specific IOC
        query = """
        query SearchIOC($value: String!) {
            stixCoreObjects(
                search: $value,
                types: ["Indicator"],
                first: 10
            ) {
                edges {
                    node {
                        ... on Indicator {
                            id
                            pattern
                            confidence
                            description
                        }
                    }
                }
            }
        }
        """
        
        try:
            async with self.session.post(
                f"{self.api_url}/graphql",
                json={"query": query, "variables": {"value": value}}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Process results
                    for edge in data.get("data", {}).get("stixCoreObjects", {}).get("edges", []):
                        if value in edge["node"].get("pattern", ""):
                            return ThreatIndicator(
                                indicator_id=edge["node"]["id"],
                                pattern=edge["node"]["pattern"],
                                threat_type=self._classify_threat_type(edge["node"]["pattern"]),
                                severity=self._calculate_severity(edge["node"]["confidence"]),
                                confidence=edge["node"]["confidence"],
                                first_seen=datetime.now(),
                                last_seen=datetime.now(),
                                description=edge["node"].get("description", ""),
                                mitre_techniques=[]
                            )
        except Exception as e:
            logger.error(f"IOC check failed: {e}")
        
        return None

class OpenCTIMCPServer:
    """MCP Server for OpenCTI integration"""
    
    def __init__(self, port: int = 3007):
        self.port = port
        self.opencti = OpenCTIConnector()
        self.security_events: List[SecurityEvent] = []
        self.monitored_services = {}
        
    async def handle_message(self, websocket, message: str):
        """Handle MCP protocol messages"""
        try:
            data = json.loads(message)
            method = data.get("method")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            if method == "initialize":
                response = await self.initialize(params)
            elif method == "opencti/get_threats":
                response = await self.get_threats(params)
            elif method == "opencti/check_ioc":
                response = await self.check_ioc(params)
            elif method == "opencti/monitor_service":
                response = await self.monitor_service(params)
            elif method == "opencti/get_security_events":
                response = await self.get_security_events(params)
            elif method == "opencti/threat_hunt":
                response = await self.threat_hunt(params)
            else:
                response = {"error": {"code": -32601, "message": "Method not found"}}
            
            if msg_id:
                response["id"] = msg_id
                
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize OpenCTI MCP server"""
        # Connect to OpenCTI
        connected = await self.opencti.connect()
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "name": "OpenCTI MCP Server",
                "version": "1.0.0",
                "capabilities": [
                    "threat-intelligence",
                    "ioc-checking",
                    "service-monitoring",
                    "threat-hunting",
                    "mitre-attack"
                ],
                "connected": connected
            }
        }
    
    async def get_threats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get latest threat indicators"""
        limit = params.get("limit", 100)
        severity_filter = params.get("severity", None)
        
        threats = await self.opencti.get_threat_indicators(limit)
        
        # Filter by severity if specified
        if severity_filter:
            threats = [t for t in threats if t.severity == severity_filter]
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "threats": [asdict(t) for t in threats],
                "count": len(threats),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def check_ioc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a value is a known IOC"""
        value = params.get("value")
        if not value:
            return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "value required"}}
        
        indicator = await self.opencti.check_ioc(value)
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "is_threat": indicator is not None,
                "indicator": asdict(indicator) if indicator else None
            }
        }
    
    async def monitor_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor a service for security threats"""
        service_id = params.get("service_id")
        monitoring_config = params.get("config", {})
        
        self.monitored_services[service_id] = {
            "enabled": True,
            "config": monitoring_config,
            "last_check": datetime.now()
        }
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "service_id": service_id,
                "monitoring": "enabled",
                "config": monitoring_config
            }
        }
    
    async def get_security_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get security events"""
        since = params.get("since")
        service_filter = params.get("service_id")
        
        events = self.security_events
        
        # Filter by time
        if since:
            since_dt = datetime.fromisoformat(since)
            events = [e for e in events if e.timestamp >= since_dt]
        
        # Filter by service
        if service_filter:
            events = [e for e in events if e.service_id == service_filter]
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "events": [asdict(e) for e in events[-100:]],  # Last 100 events
                "count": len(events)
            }
        }
    
    async def threat_hunt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform threat hunting"""
        hunt_type = params.get("type", "general")
        target = params.get("target", "all")
        
        hunt_results = {
            "suspicious_activities": [],
            "ioc_matches": [],
            "anomalies": [],
            "recommendations": []
        }
        
        # Simulate threat hunting (in production, would do real analysis)
        if hunt_type == "repository":
            hunt_results["recommendations"].append({
                "action": "scan_commits",
                "description": "Scan recent commits for malicious patterns",
                "priority": "high"
            })
        elif hunt_type == "network":
            hunt_results["recommendations"].append({
                "action": "monitor_connections",
                "description": "Monitor outbound connections for C2 activity",
                "priority": "critical"
            })
        
        return {
            "jsonrpc": "2.0",
            "result": hunt_results
        }

class OpenCTIDashboardIntegration:
    """Integration module for Oracle AGI Dashboard"""
    
    def __init__(self):
        self.opencti = OpenCTIConnector()
        self.threat_indicators = []
        self.security_score = 100.0
        self.active_threats = 0
        self.last_threat_check = datetime.now()
        
    async def initialize(self):
        """Initialize OpenCTI integration"""
        connected = await self.opencti.connect()
        if connected:
            # Load initial threat indicators
            self.threat_indicators = await self.opencti.get_threat_indicators()
            self.calculate_security_score()
            logger.info(f"OpenCTI initialized with {len(self.threat_indicators)} indicators")
        return connected
    
    def calculate_security_score(self):
        """Calculate overall security score"""
        if not self.threat_indicators:
            self.security_score = 100.0
            return
        
        # Calculate based on threat severity
        critical_threats = sum(1 for t in self.threat_indicators if t.severity == "critical")
        high_threats = sum(1 for t in self.threat_indicators if t.severity == "high")
        medium_threats = sum(1 for t in self.threat_indicators if t.severity == "medium")
        
        # Weighted scoring
        threat_impact = (critical_threats * 10) + (high_threats * 5) + (medium_threats * 2)
        self.security_score = max(0, 100 - threat_impact)
        self.active_threats = len(self.threat_indicators)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get security data for dashboard display"""
        # Update threats if needed
        if (datetime.now() - self.last_threat_check).seconds > 300:  # 5 minutes
            self.threat_indicators = await self.opencti.get_threat_indicators()
            self.calculate_security_score()
            self.last_threat_check = datetime.now()
        
        # Categorize threats
        threat_summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        threat_types = {
            "ip": 0,
            "domain": 0,
            "hash": 0,
            "url": 0,
            "unknown": 0
        }
        
        for threat in self.threat_indicators:
            threat_summary[threat.severity] += 1
            threat_types[threat.threat_type] += 1
        
        # Get recent threats
        recent_threats = sorted(
            self.threat_indicators,
            key=lambda t: t.last_seen,
            reverse=True
        )[:10]
        
        return {
            "security_score": self.security_score,
            "active_threats": self.active_threats,
            "threat_summary": threat_summary,
            "threat_types": threat_types,
            "recent_threats": [
                {
                    "id": t.indicator_id,
                    "type": t.threat_type,
                    "severity": t.severity,
                    "description": t.description[:100],
                    "last_seen": t.last_seen.isoformat()
                }
                for t in recent_threats
            ],
            "last_update": self.last_threat_check.isoformat()
        }
    
    async def check_service_security(self, service_id: str, service_data: Dict) -> Dict[str, Any]:
        """Check security status of a specific service"""
        security_status = {
            "service_id": service_id,
            "secure": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check for known vulnerable ports
        vulnerable_ports = {
            21: "FTP (unencrypted)",
            23: "Telnet (unencrypted)",
            80: "HTTP (unencrypted)",
            445: "SMB (potential vulnerability)",
            3389: "RDP (potential vulnerability)"
        }
        
        port = service_data.get("port", 0)
        if port in vulnerable_ports:
            security_status["secure"] = False
            security_status["issues"].append({
                "type": "vulnerable_port",
                "description": f"Service running on {vulnerable_ports[port]}",
                "severity": "medium"
            })
            security_status["recommendations"].append(
                f"Consider using encrypted alternative for {vulnerable_ports[port]}"
            )
        
        # Check for security headers (for HTTP services)
        if service_data.get("protocol") == "http":
            security_status["recommendations"].append(
                "Implement security headers: CSP, HSTS, X-Frame-Options"
            )
        
        return security_status

# Dashboard HTML/JS additions for security display
SECURITY_DASHBOARD_HTML = '''
<!-- Add to the dashboard HTML -->
<div class="security-container">
    <h2>🛡️ Security Status (OpenCTI)</h2>
    <div class="security-grid">
        <div class="metric-card security-score">
            <h3>Security Score</h3>
            <div class="metric-value" id="securityScore">--</div>
            <div class="health-bar">
                <div class="health-fill" id="securityBar" style="width: 0%"></div>
            </div>
        </div>
        <div class="metric-card">
            <h3>Active Threats</h3>
            <div class="metric-value" id="activeThreats">--</div>
        </div>
        <div class="metric-card">
            <h3>Critical Alerts</h3>
            <div class="metric-value critical" id="criticalAlerts">--</div>
        </div>
    </div>
    
    <div class="threat-summary">
        <h3>Threat Intelligence Summary</h3>
        <div id="threatSummary"></div>
    </div>
    
    <div class="recent-threats">
        <h3>Recent Threat Indicators</h3>
        <div id="recentThreats"></div>
    </div>
</div>

<style>
.security-container {
    background: #1a1a2e;
    padding: 30px;
    border-radius: 15px;
    margin-top: 30px;
    border: 1px solid #ff3838;
}

.security-score .metric-value {
    background: linear-gradient(135deg, #ff3838, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.critical {
    color: #ff3838 !important;
}

.threat-summary {
    margin-top: 20px;
    background: #16213e;
    padding: 20px;
    border-radius: 10px;
}

.recent-threats {
    margin-top: 20px;
    background: #16213e;
    padding: 20px;
    border-radius: 10px;
}

.threat-item {
    padding: 10px;
    margin: 5px 0;
    background: #1a1a2e;
    border-radius: 5px;
    border-left: 3px solid #ff3838;
}
</style>

<script>
// Add to dashboard JavaScript
async function updateSecurityStatus() {
    try {
        const response = await fetch('/api/security/status');
        const data = await response.json();
        
        // Update security score
        document.getElementById('securityScore').textContent = data.security_score.toFixed(0) + '%';
        document.getElementById('securityBar').style.width = data.security_score + '%';
        
        // Update threat counts
        document.getElementById('activeThreats').textContent = data.active_threats;
        document.getElementById('criticalAlerts').textContent = data.threat_summary.critical;
        
        // Update threat summary
        const summaryHtml = Object.entries(data.threat_summary)
            .map(([severity, count]) => `
                <span class="threat-badge ${severity}">
                    ${severity.toUpperCase()}: ${count}
                </span>
            `).join(' ');
        document.getElementById('threatSummary').innerHTML = summaryHtml;
        
        // Update recent threats
        const threatsHtml = data.recent_threats.map(threat => `
            <div class="threat-item">
                <strong>${threat.type.toUpperCase()}</strong> - 
                <span class="${threat.severity}">${threat.severity}</span>
                <br>
                <small>${threat.description}</small>
            </div>
        `).join('');
        document.getElementById('recentThreats').innerHTML = threatsHtml || '<p>No recent threats</p>';
        
    } catch (error) {
        console.error('Failed to update security status:', error);
    }
}

// Update security status every 30 seconds
setInterval(updateSecurityStatus, 30000);
updateSecurityStatus();
</script>
'''

async def main():
    """Test OpenCTI integration"""
    # Initialize components
    opencti_integration = OpenCTIDashboardIntegration()
    
    # Connect to OpenCTI
    connected = await opencti_integration.initialize()
    if connected:
        logger.info("OpenCTI integration successful")
        
        # Get dashboard data
        security_data = await opencti_integration.get_dashboard_data()
        print(json.dumps(security_data, indent=2))
    else:
        logger.error("Failed to initialize OpenCTI")

if __name__ == "__main__":
    asyncio.run(main())