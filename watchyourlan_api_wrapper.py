#!/usr/bin/env python3
"""
WatchYourLAN API Wrapper
========================
Python API wrapper for WatchYourLAN network monitoring system
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WatchYourLANAPI")

@dataclass
class NetworkHost:
    """Network host data model"""
    id: str
    ip: str
    mac: str
    hostname: str
    vendor: str
    first_seen: str
    last_seen: str
    online: bool
    ports: List[int]
    os_info: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class NetworkStats:
    """Network statistics data model"""
    total_hosts: int
    online_hosts: int
    offline_hosts: int
    new_hosts_today: int
    scan_duration: float
    last_scan: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class WatchYourLANAPI:
    """API wrapper for WatchYourLAN"""

    def __init__(self, base_url: str = "http://localhost:8840"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.cache = {}
        self.cache_timeout = 30  # seconds

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to WatchYourLAN API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} {await response.text()}")
                    return {}
        except Exception as e:
            logger.error(f"API request error: {e}")
            return {}

    async def get_hosts(self) -> List[NetworkHost]:
        """Get all discovered network hosts"""
        logger.info("🔍 Getting network hosts...")

        # Check cache first
        cache_key = "hosts"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_timeout:
                return data

        try:
            # Try to get hosts from API
            response = await self._request('GET', '/api/hosts')

            if response:
                hosts = []
                for host_data in response.get('hosts', []):
                    host = NetworkHost(
                        id=host_data.get('id', ''),
                        ip=host_data.get('ip', ''),
                        mac=host_data.get('mac', ''),
                        hostname=host_data.get('hostname', ''),
                        vendor=host_data.get('vendor', ''),
                        first_seen=host_data.get('first_seen', ''),
                        last_seen=host_data.get('last_seen', ''),
                        online=host_data.get('online', False),
                        ports=host_data.get('ports', []),
                        os_info=host_data.get('os_info')
                    )
                    hosts.append(host)

                # Cache the result
                self.cache[cache_key] = (datetime.now(), hosts)
                return hosts
            else:
                # Return empty list if API is not available
                logger.warning("WatchYourLAN API not available, returning empty host list")
                return []

        except Exception as e:
            logger.error(f"Error getting hosts: {e}")
            return []

    async def get_host_by_id(self, host_id: str) -> Optional[NetworkHost]:
        """Get specific host by ID"""
        logger.info(f"🔍 Getting host {host_id}...")

        try:
            response = await self._request('GET', f'/api/host/{host_id}')

            if response:
                host_data = response.get('host', {})
                return NetworkHost(
                    id=host_data.get('id', ''),
                    ip=host_data.get('ip', ''),
                    mac=host_data.get('mac', ''),
                    hostname=host_data.get('hostname', ''),
                    vendor=host_data.get('vendor', ''),
                    first_seen=host_data.get('first_seen', ''),
                    last_seen=host_data.get('last_seen', ''),
                    online=host_data.get('online', False),
                    ports=host_data.get('ports', []),
                    os_info=host_data.get('os_info')
                )
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting host {host_id}: {e}")
            return None

    async def get_network_stats(self) -> NetworkStats:
        """Get network statistics"""
        logger.info("📊 Getting network statistics...")

        try:
            response = await self._request('GET', '/api/stats')

            if response:
                return NetworkStats(
                    total_hosts=response.get('total_hosts', 0),
                    online_hosts=response.get('online_hosts', 0),
                    offline_hosts=response.get('offline_hosts', 0),
                    new_hosts_today=response.get('new_hosts_today', 0),
                    scan_duration=response.get('scan_duration', 0.0),
                    last_scan=response.get('last_scan', '')
                )
            else:
                logger.warning("WatchYourLAN API not available, returning empty stats")
                return NetworkStats(
                    total_hosts=0,
                    online_hosts=0,
                    offline_hosts=0,
                    new_hosts_today=0,
                    scan_duration=0.0,
                    last_scan='Never'
                )

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return NetworkStats(
                total_hosts=0,
                online_hosts=0,
                offline_hosts=0,
                new_hosts_today=0,
                scan_duration=0.0,
                last_scan='Never'
            )

    async def trigger_scan(self) -> Dict[str, Any]:
        """Trigger manual network scan"""
        logger.info("🔍 Triggering network scan...")

        try:
            response = await self._request('POST', '/api/scan')
            return response
        except Exception as e:
            logger.error(f"Error triggering scan: {e}")
            return {"success": False, "error": str(e)}

    async def get_host_history(self, host_id: str = None) -> List[Dict[str, Any]]:
        """Get host history"""
        logger.info(f"📈 Getting host history for {host_id or 'all hosts'}...")

        try:
            endpoint = f'/api/history' if not host_id else f'/api/history/{host_id}'
            response = await self._request('GET', endpoint)
            return response.get('history', [])
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []



    async def health_check(self) -> Dict[str, Any]:
        """Check if WatchYourLAN is running"""
        try:
            response = await self._request('GET', '/health')
            return {"status": "healthy", "service": "WatchYourLAN"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Test the API wrapper
async def test_api():
    """Test the WatchYourLAN API wrapper"""
    logger.info("🧪 Testing WatchYourLAN API wrapper...")

    async with WatchYourLANAPI() as api:
        # Test health check
        health = await api.health_check()
        logger.info(f"Health check: {health}")

        # Test get hosts
        hosts = await api.get_hosts()
        logger.info(f"Found {len(hosts)} hosts")

        # Test get stats
        stats = await api.get_network_stats()
        logger.info(f"Network stats: {stats.to_dict()}")

        # Test trigger scan
        scan_result = await api.trigger_scan()
        logger.info(f"Scan result: {scan_result}")

        logger.info("✅ API wrapper test complete!")

if __name__ == "__main__":
    asyncio.run(test_api())
