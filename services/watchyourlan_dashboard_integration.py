#!/usr/bin/env python3
"""
WatchYourLAN Dashboard Integration
=================================
Integration of WatchYourLAN network monitoring into Ultimate AGI Dashboard
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import aiohttp
from aiohttp import web
import aiohttp_jinja2
import jinja2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WatchYourLANDashboard")

class WatchYourLANDashboardIntegration:
    """WatchYourLAN integration for Ultimate AGI Dashboard"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.wyl_api_base = "http://localhost:8840"  # Default WatchYourLAN port
        self.integration_port = 8895
        self.mock_mode = False  # Disabled mock mode - using real API only

        # Network monitoring data
        self.network_data = {
            "hosts": [],
            "statistics": {},
            "scan_history": [],
            "alerts": [],
            "last_update": None
        }

    async def fetch_network_data(self) -> dict[str, Any]:
        """Fetch network data from WatchYourLAN API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get hosts
                async with session.get(f"{self.wyl_api_base}/api/hosts") as response:
                    if response.status == 200:
                        hosts_data = await response.json()
                        self.network_data["hosts"] = hosts_data

                # Get statistics
                async with session.get(f"{self.wyl_api_base}/api/stats") as response:
                    if response.status == 200:
                        stats_data = await response.json()
                        self.network_data["statistics"] = stats_data

                # Get scan history
                async with session.get(f"{self.wyl_api_base}/api/history") as response:
                    if response.status == 200:
                        history_data = await response.json()
                        self.network_data["scan_history"] = history_data

                self.network_data["last_update"] = datetime.now().isoformat()
                return self.network_data

        except Exception as e:
            logger.error(f"Failed to fetch network data: {e}")
            # Return empty data structure instead of mock data
            return {
                "hosts": [],
                "statistics": {
                    "total_hosts": 0,
                    "online_hosts": 0,
                    "offline_hosts": 0,
                    "new_hosts_today": 0,
                    "scan_duration": 0.0,
                    "last_scan": "Never",
                    "network_range": "Unknown",
                    "scan_interval": 0
                },
                "scan_history": [],
                "alerts": [],
                "last_update": datetime.now().isoformat()
            }



    async def get_network_overview(self) -> dict[str, Any]:
        """Get network overview for dashboard"""
        data = await self.fetch_network_data()

        overview = {
            "summary": {
                "total_devices": data["statistics"].get("total_hosts", 0),
                "online_devices": data["statistics"].get("online_hosts", 0),
                "offline_devices": data["statistics"].get("offline_hosts", 0),
                "new_devices_today": data["statistics"].get("new_hosts_today", 0),
                "last_scan": data["statistics"].get("last_scan", "Never"),
                "scan_duration": data["statistics"].get("scan_duration", 0),
                "network_health": self.calculate_network_health(data)
            },
            "recent_events": data["scan_history"][-5:],  # Last 5 events
            "active_alerts": [alert for alert in data["alerts"] if not alert.get("acknowledged", False)],
            "device_breakdown": self.get_device_breakdown(data["hosts"]),
            "network_topology": self.generate_network_topology(data["hosts"])
        }

        return overview

    def calculate_network_health(self, data: dict[str, Any]) -> dict[str, Any]:
        """Calculate network health metrics"""
        stats = data["statistics"]
        total = stats.get("total_hosts", 0)
        online = stats.get("online_hosts", 0)

        if total == 0:
            health_score = 0
        else:
            health_score = (online / total) * 100

        health_status = "excellent" if health_score >= 95 else \
                       "good" if health_score >= 85 else \
                       "fair" if health_score >= 70 else "poor"

        return {
            "score": round(health_score, 1),
            "status": health_status,
            "color": "#00ff00" if health_score >= 95 else
                    "#ffff00" if health_score >= 85 else
                    "#ff8000" if health_score >= 70 else "#ff0000"
        }

    def get_device_breakdown(self, hosts: list[Dict[str, Any]]) -> dict[str, Any]:
        """Get device breakdown by vendor/type"""
        vendors = {}
        status_counts = {"online": 0, "offline": 0}

        for host in hosts:
            vendor = host.get("vendor", "Unknown")
            vendors[vendor] = vendors.get(vendor, 0) + 1

            status = host.get("status", "unknown")
            if status in status_counts:
                status_counts[status] += 1

        return {
            "by_vendor": vendors,
            "by_status": status_counts
        }

    def generate_network_topology(self, hosts: list[Dict[str, Any]]) -> dict[str, Any]:
        """Generate network topology data for visualization"""
        nodes = []
        edges = []

        # Add router as central node
        nodes.append({
            "id": "router",
            "label": "Router",
            "ip": "192.168.1.1",
            "type": "router",
            "status": "online",
            "x": 0,
            "y": 0
        })

        # Add hosts as nodes
        for i, host in enumerate(hosts):
            if host["ip"] != "192.168.1.1":  # Skip router
                angle = (i * 60) % 360  # Distribute around router
                nodes.append({
                    "id": f"host_{host['id']}",
                    "label": host.get("hostname", host["ip"]),
                    "ip": host["ip"],
                    "type": "device",
                    "status": host.get("status", "unknown"),
                    "vendor": host.get("vendor", "Unknown"),
                    "angle": angle
                })

                # Add edge to router
                edges.append({
                    "from": "router",
                    "to": f"host_{host['id']}",
                    "type": "ethernet"
                })

        return {
            "nodes": nodes,
            "edges": edges
        }

    async def setup_dashboard_routes(self, app: web.Application):
        """Setup dashboard routes"""
        # API routes
        app.router.add_get('/api/network/overview', self.handle_network_overview)
        app.router.add_get('/api/network/hosts', self.handle_network_hosts)
        app.router.add_get('/api/network/stats', self.handle_network_stats)
        app.router.add_get('/api/network/scan', self.handle_trigger_scan)
        app.router.add_post('/api/network/alerts/{alert_id}/acknowledge', self.handle_acknowledge_alert)

        # Dashboard routes
        app.router.add_get('/network', self.handle_network_dashboard)
        app.router.add_static('/static/network/', self.base_path / 'static' / 'network')

    async def handle_network_overview(self, request: web.Request) -> web.Response:
        """Handle network overview API request"""
        try:
            overview = await self.get_network_overview()
            return web.json_response(overview)
        except Exception as e:
            logger.error(f"Error getting network overview: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_network_hosts(self, request: web.Request) -> web.Response:
        """Handle network hosts API request"""
        try:
            data = await self.fetch_network_data()
            return web.json_response(data["hosts"])
        except Exception as e:
            logger.error(f"Error getting network hosts: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_network_stats(self, request: web.Request) -> web.Response:
        """Handle network stats API request"""
        try:
            data = await self.fetch_network_data()
            return web.json_response(data["statistics"])
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_trigger_scan(self, request: web.Request) -> web.Response:
        """Handle trigger scan API request"""
        try:
            # Actual API call to WatchYourLAN
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.wyl_api_base}/api/scan") as response:
                    if response.status == 200:
                        result = await response.json()
                        return web.json_response(result)
                    else:
                        return web.json_response({"error": "Failed to trigger scan"}, status=500)
        except Exception as e:
            logger.error(f"Error triggering scan: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_acknowledge_alert(self, request: web.Request) -> web.Response:
        """Handle acknowledge alert API request"""
        try:
            alert_id = int(request.match_info['alert_id'])

            # Update alert status
            data = await self.fetch_network_data()
            for alert in data["alerts"]:
                if alert["id"] == alert_id:
                    alert["acknowledged"] = True
                    break

            return web.json_response({"message": f"Alert {alert_id} acknowledged", "status": "success"})
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_network_dashboard(self, request: web.Request) -> web.Response:
        """Handle network dashboard page"""
        try:
            overview = await self.get_network_overview()

            # Generate HTML dashboard
            dashboard_html = self.generate_dashboard_html(overview)
            return web.Response(text=dashboard_html, content_type='text/html')
        except Exception as e:
            logger.error(f"Error rendering network dashboard: {e}")
            return web.Response(text=f"Error: {e}", status=500)

    def generate_dashboard_html(self, overview: dict[str, Any]) -> str:
        """Generate HTML dashboard"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Monitor - Ultimate AGI Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }}

        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #00ff00;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 0 0 20px #00ff00;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #cccccc;
            margin-top: 5px;
        }}

        .section {{
            background: rgba(0, 255, 0, 0.05);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .section h2 {{
            color: #00ff00;
            margin-top: 0;
        }}

        .device-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}

        .device {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
        }}

        .device.online {{
            border-color: #00ff00;
        }}

        .device.offline {{
            border-color: #ff0000;
            color: #ff0000;
        }}

        .alert {{
            background: rgba(255, 255, 0, 0.1);
            border: 1px solid #ffff00;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }}

        .alert.warning {{
            border-color: #ff8000;
            color: #ff8000;
        }}

        .alert.error {{
            border-color: #ff0000;
            color: #ff0000;
        }}

        .btn {{
            background: #00ff00;
            color: #000000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}

        .btn:hover {{
            background: #00cc00;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🌐 Network Monitor</h1>
            <p>Ultimate AGI Dashboard - Network Monitoring Integration</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{overview['summary']['total_devices']}</div>
                <div class="stat-label">Total Devices</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['summary']['online_devices']}</div>
                <div class="stat-label">Online</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['summary']['offline_devices']}</div>
                <div class="stat-label">Offline</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['summary']['network_health']['score']}%</div>
                <div class="stat-label">Network Health</div>
            </div>
        </div>

        <div class="section">
            <h2>🚨 Active Alerts</h2>
            <div id="alerts">
                {self.render_alerts(overview['active_alerts'])}
            </div>
        </div>

        <div class="section">
            <h2>📱 Network Devices</h2>
            <div class="device-list">
                {self.render_devices(overview)}
            </div>
        </div>

        <div class="section">
            <h2>📊 Network Statistics</h2>
            <canvas id="networkChart" width="400" height="200"></canvas>
        </div>

        <div class="section">
            <h2>🕐 Recent Events</h2>
            <div id="events">
                {self.render_events(overview['recent_events'])}
            </div>
        </div>
    </div>

    <script>
        // Initialize network chart
        const ctx = document.getElementById('networkChart').getContext('2d');
        const networkChart = new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Online', 'Offline'],
                datasets: [{{
                    data: [{overview['summary']['online_devices']}, {overview['summary']['offline_devices']}],
                    backgroundColor: ['#00ff00', '#ff0000'],
                    borderColor: ['#00ff00', '#ff0000'],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#00ff00'
                        }}
                    }}
                }}
            }}
        }});

        // Auto-refresh every 30 seconds
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """

    def render_alerts(self, alerts: list[Dict[str, Any]]) -> str:
        """Render alerts HTML"""
        if not alerts:
            return "<p>No active alerts</p>"

        html = ""
        for alert in alerts:
            severity_class = alert.get('severity', 'info')
            html += f"""
            <div class="alert {severity_class}">
                <strong>{alert['type'].replace('_', ' ').title()}</strong>
                <p>{alert['message']}</p>
                <small>{alert['timestamp']}</small>
                <button class="btn" onclick="acknowledgeAlert({alert['id']})">Acknowledge</button>
            </div>
            """
        return html

    def render_devices(self, overview: dict[str, Any]) -> str:
        """Render devices HTML"""
        devices = overview.get('device_breakdown', {}).get('by_vendor', {})
        if not devices:
            return "<p>No devices found</p>"

        html = ""
        for vendor, count in devices.items():
            html += f"""
            <div class="device">
                <h3>{vendor}</h3>
                <p>{count} device{'s' if count != 1 else ''}</p>
            </div>
            """
        return html

    def render_events(self, events: list[Dict[str, Any]]) -> str:
        """Render events HTML"""
        if not events:
            return "<p>No recent events</p>"

        html = ""
        for event in events:
            html += f"""
            <div class="event">
                <strong>{event['event'].replace('_', ' ').title()}</strong>
                <p>{event.get('message', 'No details available')}</p>
                <small>{event['timestamp']}</small>
            </div>
            """
        return html

    async def run_dashboard_server(self):
        """Run the dashboard server"""
        logger.info(f"🚀 Starting WatchYourLAN Dashboard Integration on port {self.integration_port}...")

        # Create web application
        app = web.Application()

        # Setup routes
        await self.setup_dashboard_routes(app)

        # Create and start server
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, 'localhost', self.integration_port)
        await site.start()

        logger.info(f"✅ Dashboard server started at http://localhost:{self.integration_port}")
        logger.info(f"🌐 Network dashboard: http://localhost:{self.integration_port}/network")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 Shutting down dashboard server...")
            await runner.cleanup()

async def main():
    """Main function"""
    dashboard = WatchYourLANDashboardIntegration()
    await dashboard.run_dashboard_server()

if __name__ == "__main__":
    asyncio.run(main())
