#!/usr/bin/env python3
"""
Cyberpunk Dashboard for WatchYourLAN Integration
Real-time network monitoring with Jupiter DEX integration
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import aiohttp
from aiohttp import web
import aiohttp_jinja2
import jinja2
import logging
from dataclasses import asdict
import time

class CyberpunkDashboard:
    """Cyberpunk-themed dashboard for WatchYourLAN data"""

    def __init__(self, db_path: str = "data/watchyourlan_cyber.db", port: int = 8891):
        self.db_path = Path(db_path)
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.setup_templates()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("CyberpunkDashboard")

    def setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/devices', self.api_devices)
        self.app.router.add_get('/api/events', self.api_events)
        self.app.router.add_get('/api/jupiter', self.api_jupiter)
        self.app.router.add_get('/api/stats', self.api_stats)
        self.app.router.add_static('/static/', path='static/', name='static')

    def setup_templates(self):
        """Setup Jinja2 templates"""
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)

        # Create cyberpunk template
        cyberpunk_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 CYBERPUNK NETWORK MONITOR 🔥</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Orbitron', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff00;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="20" fill="%23003300" opacity="0.1">01010101</text></svg>');
            z-index: -1;
            animation: matrixScroll 20s linear infinite;
        }

        @keyframes matrixScroll {
            0% { transform: translateY(0); }
            100% { transform: translateY(-100px); }
        }

        .header {
            text-align: center;
            padding: 2rem;
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00ff00;
            box-shadow: 0 0 20px #00ff00;
        }

        .title {
            font-size: 3rem;
            font-weight: 900;
            text-shadow: 0 0 10px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 0 10px #00ff00; }
            to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }

        .card {
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.5);
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-transform: uppercase;
            color: #00ffff;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .stat-item {
            background: rgba(0, 255, 0, 0.1);
            padding: 1rem;
            border-radius: 5px;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ffff00;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #00ff00;
            text-transform: uppercase;
        }

        .device-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .device-item {
            background: rgba(0, 255, 0, 0.1);
            margin: 0.5rem 0;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #00ff00;
        }

        .device-item.threat-high {
            border-left-color: #ff0000;
            background: rgba(255, 0, 0, 0.1);
        }

        .device-item.threat-critical {
            border-left-color: #ff00ff;
            background: rgba(255, 0, 255, 0.1);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        .device-name {
            font-weight: 700;
            color: #00ffff;
        }

        .device-info {
            font-size: 0.9rem;
            color: #00ff00;
            margin-top: 0.5rem;
        }

        .threat-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .threat-low { background: #00ff00; color: #000; }
        .threat-medium { background: #ffff00; color: #000; }
        .threat-high { background: #ff8800; color: #000; }
        .threat-critical { background: #ff0000; color: #fff; }

        .jupiter-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff00;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            50% { opacity: 0.5; }
        }

        .refresh-btn {
            background: linear-gradient(45deg, #00ff00, #00ffff);
            color: #000;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 5px;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }

        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }

        .cyber-scrollbar::-webkit-scrollbar {
            width: 8px;
        }

        .cyber-scrollbar::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.5);
        }

        .cyber-scrollbar::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }

        .cyber-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #00ffff;
        }
    </style>
</head>
<body>
    <div class="matrix-bg"></div>

    <div class="header">
        <h1 class="title">🔥 CYBERPUNK NETWORK MONITOR 🔥</h1>
        <p>Real-time network surveillance with Jupiter DEX integration</p>
    </div>

    <div class="container">
        <div class="dashboard-grid">
            <!-- Network Statistics -->
            <div class="card">
                <div class="card-title">📊 Network Statistics</div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="total-devices">0</div>
                        <div class="stat-label">Total Devices</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="active-devices">0</div>
                        <div class="stat-label">Active Devices</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="crypto-devices">0</div>
                        <div class="stat-label">Crypto Devices</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="trading-devices">0</div>
                        <div class="stat-label">Trading Devices</div>
                    </div>
                </div>
                <button class="refresh-btn" onclick="refreshData()">🔄 REFRESH DATA</button>
            </div>

            <!-- Threat Monitor -->
            <div class="card">
                <div class="card-title">🚨 Threat Monitor</div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="threat-critical">0</div>
                        <div class="stat-label">Critical</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="threat-high">0</div>
                        <div class="stat-label">High</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="threat-medium">0</div>
                        <div class="stat-label">Medium</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="threat-low">0</div>
                        <div class="stat-label">Low</div>
                    </div>
                </div>
            </div>

            <!-- Jupiter DEX Monitor -->
            <div class="card">
                <div class="card-title">💰 Jupiter DEX Monitor</div>
                <div class="jupiter-status">
                    <div class="status-indicator"></div>
                    <span>Jupiter Integration Active</span>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="jupiter-transactions">0</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="jupiter-volume">$0</div>
                        <div class="stat-label">Volume</div>
                    </div>
                </div>
            </div>

            <!-- Device List -->
            <div class="card">
                <div class="card-title">📡 Active Devices</div>
                <div class="device-list cyber-scrollbar" id="device-list">
                    <!-- Devices will be populated here -->
                </div>
            </div>

            <!-- Recent Events -->
            <div class="card">
                <div class="card-title">📝 Recent Events</div>
                <div class="device-list cyber-scrollbar" id="event-list">
                    <!-- Events will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh data every 30 seconds
        setInterval(refreshData, 30000);

        // Initial data load
        refreshData();

        async function refreshData() {
            try {
                await Promise.all([
                    updateStats(),
                    updateDevices(),
                    updateEvents(),
                    updateJupiter()
                ]);
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                document.getElementById('total-devices').textContent = data.total_devices || 0;
                document.getElementById('active-devices').textContent = data.active_devices || 0;
                document.getElementById('crypto-devices').textContent = data.crypto_devices || 0;
                document.getElementById('trading-devices').textContent = data.trading_devices || 0;

                // Update threat distribution
                document.getElementById('threat-critical').textContent = data.threat_distribution?.critical || 0;
                document.getElementById('threat-high').textContent = data.threat_distribution?.high || 0;
                document.getElementById('threat-medium').textContent = data.threat_distribution?.medium || 0;
                document.getElementById('threat-low').textContent = data.threat_distribution?.low || 0;
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }

        async function updateDevices() {
            try {
                const response = await fetch('/api/devices');
                const devices = await response.json();

                const deviceList = document.getElementById('device-list');
                deviceList.innerHTML = '';

                devices.forEach(device => {
                    const deviceItem = document.createElement('div');
                    deviceItem.className = `device-item threat-${device.threat_level}`;

                    deviceItem.innerHTML = `
                        <div class="device-name">${device.hostname} (${device.ip})</div>
                        <div class="device-info">
                            <span class="threat-badge threat-${device.threat_level}">${device.threat_level}</span>
                            Type: ${device.device_type} | Security: ${device.security_score}%
                            ${device.crypto_activity ? ' | 💰 CRYPTO' : ''}
                            ${device.trading_activity ? ' | 📈 TRADING' : ''}
                        </div>
                    `;

                    deviceList.appendChild(deviceItem);
                });
            } catch (error) {
                console.error('Error updating devices:', error);
            }
        }

        async function updateEvents() {
            try {
                const response = await fetch('/api/events');
                const events = await response.json();

                const eventList = document.getElementById('event-list');
                eventList.innerHTML = '';

                events.slice(-10).forEach(event => {
                    const eventItem = document.createElement('div');
                    eventItem.className = `device-item threat-${event.threat_level}`;

                    const timestamp = new Date(event.timestamp).toLocaleString();
                    eventItem.innerHTML = `
                        <div class="device-name">${event.event_type.toUpperCase()}</div>
                        <div class="device-info">
                            ${timestamp} | ${event.device_ip}<br>
                            ${event.description}
                        </div>
                    `;

                    eventList.appendChild(eventItem);
                });
            } catch (error) {
                console.error('Error updating events:', error);
            }
        }

        async function updateJupiter() {
            try {
                const response = await fetch('/api/jupiter');
                const data = await response.json();

                document.getElementById('jupiter-transactions').textContent = data.total_transactions || 0;
                document.getElementById('jupiter-volume').textContent = `$${data.total_volume || 0}`;
            } catch (error) {
                console.error('Error updating Jupiter data:', error);
            }
        }
    </script>
</body>
</html>
        '''

        template_path = template_dir / "index.html"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(cyberpunk_template)

        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(str(template_dir)))

    async def index(self, request):
        """Serve the main dashboard page"""
        return aiohttp_jinja2.render_template('index.html', request, {})

    async def api_stats(self, request):
        """API endpoint for network statistics"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Get device statistics
                cursor.execute("SELECT COUNT(*) FROM cyber_devices")
                total_devices = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cyber_devices WHERE is_active = 1")
                active_devices = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cyber_devices WHERE crypto_activity = 1")
                crypto_devices = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cyber_devices WHERE trading_activity = 1")
                trading_devices = cursor.fetchone()[0]

                # Get threat distribution
                cursor.execute("SELECT threat_level, COUNT(*) FROM cyber_devices GROUP BY threat_level")
                threat_rows = cursor.fetchall()
                threat_distribution = {row[0]: row[1] for row in threat_rows}

                stats = {
                    "total_devices": total_devices,
                    "active_devices": active_devices,
                    "crypto_devices": crypto_devices,
                    "trading_devices": trading_devices,
                    "threat_distribution": threat_distribution
                }

                return web.json_response(stats)
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_devices(self, request):
        """API endpoint for device list"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mac, ip, hostname, vendor, device_type, threat_level,
                           is_active, crypto_activity, trading_activity, security_score
                    FROM cyber_devices
                    WHERE is_active = 1
                    ORDER BY last_seen DESC
                """)

                devices = []
                for row in cursor.fetchall():
                    device = {
                        "mac": row[0],
                        "ip": row[1],
                        "hostname": row[2],
                        "vendor": row[3],
                        "device_type": row[4],
                        "threat_level": row[5],
                        "is_active": bool(row[6]),
                        "crypto_activity": bool(row[7]),
                        "trading_activity": bool(row[8]),
                        "security_score": row[9]
                    }
                    devices.append(device)

                return web.json_response(devices)
        except Exception as e:
            self.logger.error(f"Error getting devices: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_events(self, request):
        """API endpoint for recent events"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, event_type, device_mac, device_ip, description, threat_level
                    FROM network_events
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)

                events = []
                for row in cursor.fetchall():
                    event = {
                        "timestamp": row[0],
                        "event_type": row[1],
                        "device_mac": row[2],
                        "device_ip": row[3],
                        "description": row[4],
                        "threat_level": row[5]
                    }
                    events.append(event)

                return web.json_response(events)
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_jupiter(self, request):
        """API endpoint for Jupiter DEX data"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Get Jupiter transaction count
                cursor.execute("SELECT COUNT(*) FROM jupiter_activity")
                total_transactions = cursor.fetchone()[0]

                # Get total volume from database
                cursor.execute("SELECT SUM(amount_in) FROM jupiter_activity WHERE success = 1")
                total_volume = cursor.fetchone()[0] or 0

                jupiter_data = {
                    "total_transactions": total_transactions,
                    "total_volume": round(total_volume, 2)
                }

                return web.json_response(jupiter_data)
        except Exception as e:
            self.logger.error(f"Error getting Jupiter data: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def start_server(self):
        """Start the web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()

        self.logger.info(f"🔥 Cyberpunk Dashboard started on http://localhost:{self.port} 🔥")

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("🔥 Dashboard stopped by user 🔥")
        finally:
            await runner.cleanup()

async def main():
    """Main function to run the cyberpunk dashboard"""
    dashboard = CyberpunkDashboard()
    await dashboard.start_server()

if __name__ == "__main__":
    asyncio.run(main())
