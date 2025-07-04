#!/usr/bin/env python3
"""
Real System Metrics Collector
============================
Collects actual system performance metrics
"""

import asyncio
import psutil
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemMetricsCollector")

class RealSystemMetricsCollector:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.metrics_path = self.f_drive_root / "metrics"
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.metrics_path / "system_metrics.db"
        self._init_database()
        
        # Track service processes
        self.service_pids = {}
        
    def _init_database(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp REAL PRIMARY KEY,
                cpu_percent REAL,
                cpu_per_core TEXT,
                memory_percent REAL,
                memory_available_mb REAL,
                memory_used_mb REAL,
                swap_percent REAL,
                disk_usage_percent REAL,
                disk_free_gb REAL,
                disk_read_mb REAL,
                disk_write_mb REAL,
                network_sent_mb REAL,
                network_recv_mb REAL,
                process_count INTEGER,
                thread_count INTEGER,
                handle_count INTEGER,
                gpu_percent REAL,
                gpu_memory_mb REAL,
                temperature_cpu REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_metrics (
                timestamp REAL,
                service_name TEXT,
                pid INTEGER,
                cpu_percent REAL,
                memory_mb REAL,
                threads INTEGER,
                connections INTEGER,
                status TEXT,
                uptime_seconds REAL,
                PRIMARY KEY (timestamp, service_name)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def find_service_processes(self):
        """Find MCPVotsAGI service processes"""
        services = {
            'deepseek_mcp': ['python', 'deepseek_ollama_mcp_server.py'],
            'deepseek_trading': ['python', 'deepseek_trading_agent'],
            'memory_mcp': ['python', 'memory_mcp_server.py'],
            'solana_mcp': ['python', 'solana_mcp.py'],
            'opencti_mcp': ['python', 'opencti_mcp_server.py'],
            'ollama': ['ollama', 'serve']
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] or []
                cmdline_str = ' '.join(cmdline)
                
                for service_name, patterns in services.items():
                    if all(pattern in cmdline_str for pattern in patterns):
                        self.service_pids[service_name] = proc.info['pid']
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def collect_system_metrics(self):
        """Collect system-wide metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(percpu=True)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        net_io = psutil.net_io_counters()
        
        # Process metrics
        process_count = len(psutil.pids())
        
        # GPU metrics (if available)
        gpu_percent = 0
        gpu_memory_mb = 0
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_percent = gpu_info.gpu
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_mb = mem_info.used / (1024**2)
        except:
            pass
            
        # Temperature (if available)
        temp_cpu = 0
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp_cpu = temps['coretemp'][0].current
        except:
            pass
            
        return {
            'timestamp': time.time(),
            'cpu_percent': cpu_percent,
            'cpu_per_core': json.dumps(cpu_per_core),
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024**2),
            'memory_used_mb': memory.used / (1024**2),
            'swap_percent': swap.percent,
            'disk_usage_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3),
            'disk_read_mb': disk_io.read_bytes / (1024**2),
            'disk_write_mb': disk_io.write_bytes / (1024**2),
            'network_sent_mb': net_io.bytes_sent / (1024**2),
            'network_recv_mb': net_io.bytes_recv / (1024**2),
            'process_count': process_count,
            'thread_count': sum(p.num_threads() for p in psutil.process_iter()),
            'handle_count': sum(p.num_handles() for p in psutil.process_iter() if hasattr(p, 'num_handles')),
            'gpu_percent': gpu_percent,
            'gpu_memory_mb': gpu_memory_mb,
            'temperature_cpu': temp_cpu
        }
        
    def collect_service_metrics(self):
        """Collect metrics for individual services"""
        service_metrics = []
        
        for service_name, pid in self.service_pids.items():
            try:
                proc = psutil.Process(pid)
                
                # Get process info
                with proc.oneshot():
                    cpu_percent = proc.cpu_percent()
                    memory_info = proc.memory_info()
                    connections = len(proc.connections())
                    create_time = proc.create_time()
                    
                metrics = {
                    'timestamp': time.time(),
                    'service_name': service_name,
                    'pid': pid,
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_info.rss / (1024**2),
                    'threads': proc.num_threads(),
                    'connections': connections,
                    'status': proc.status(),
                    'uptime_seconds': time.time() - create_time
                }
                
                service_metrics.append(metrics)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists
                del self.service_pids[service_name]
                
        return service_metrics
        
    async def store_metrics(self, system_metrics, service_metrics):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store system metrics
        cursor.execute("""
            INSERT INTO system_metrics VALUES (
                :timestamp, :cpu_percent, :cpu_per_core, :memory_percent,
                :memory_available_mb, :memory_used_mb, :swap_percent,
                :disk_usage_percent, :disk_free_gb, :disk_read_mb,
                :disk_write_mb, :network_sent_mb, :network_recv_mb,
                :process_count, :thread_count, :handle_count,
                :gpu_percent, :gpu_memory_mb, :temperature_cpu
            )
        """, system_metrics)
        
        # Store service metrics
        for metrics in service_metrics:
            cursor.execute("""
                INSERT INTO service_metrics VALUES (
                    :timestamp, :service_name, :pid, :cpu_percent,
                    :memory_mb, :threads, :connections, :status,
                    :uptime_seconds
                )
            """, metrics)
            
        conn.commit()
        conn.close()
        
        # Also save latest to JSON for quick access
        latest_file = self.metrics_path / "latest_metrics.json"
        with open(latest_file, 'w') as f:
            json.dump({
                'system': system_metrics,
                'services': service_metrics
            }, f)
            
    async def run_continuous_collection(self):
        """Run continuous metrics collection"""
        logger.info("Starting real system metrics collection...")
        
        while True:
            try:
                # Find service processes
                self.find_service_processes()
                
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                service_metrics = self.collect_service_metrics()
                
                # Store metrics
                await self.store_metrics(system_metrics, service_metrics)
                
                logger.info(f"Collected metrics - CPU: {system_metrics['cpu_percent']:.1f}%, "
                          f"Memory: {system_metrics['memory_percent']:.1f}%, "
                          f"Services: {len(service_metrics)}")
                
                # Collect every 10 seconds
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    collector = RealSystemMetricsCollector()
    asyncio.run(collector.run_continuous_collection())
