#!/usr/bin/env python3
"""
Start Real Data Collectors
=========================
Launches all real-time data collection services
"""

import subprocess
import time
import sys
from pathlib import Path

def start_collectors():
    """Start all data collection services"""
    print("🚀 Starting Real Data Collection Services...")
    
    collectors = [
        ("Market Data Collector", "python realtime_market_data_collector.py"),
        ("System Metrics Collector", "python real_system_metrics_collector.py"),
        ("RL Training Monitor", "python real_rl_training_monitor.py")
    ]
    
    processes = []
    
    for name, command in collectors:
        print(f"Starting {name}...")
        try:
            proc = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append((name, proc))
            print(f"✓ {name} started (PID: {proc.pid})")
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            
    print("\n✅ All collectors started!")
    print("\nPress Ctrl+C to stop all collectors...")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️ {name} has stopped!")
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all collectors...")
        
        for name, proc in processes:
            proc.terminate()
            proc.wait()
            print(f"✓ {name} stopped")
            
        print("\n✅ All collectors stopped")

if __name__ == "__main__":
    start_collectors()
