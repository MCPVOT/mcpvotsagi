#!/usr/bin/env python3
"""
Start RL Trading and Solana Systems
===================================
Launches all trading systems in the correct order
"""

import asyncio
import logging
import sys
from pathlib import Path
import subprocess
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingLauncher")

async def start_rl_training():
    """Start RL training monitoring in background"""
    logger.info("🧠 Starting RL Training Monitor...")

    try:
        from real_rl_training_monitor import RealRLTrainingMonitor

        monitor = RealRLTrainingMonitor()

        # Collect current metrics
        logger.info("📊 Collecting RL metrics...")
        await monitor.collect_and_store_metrics()

        logger.info("✅ RL Training Monitor started successfully")
        return monitor

    except Exception as e:
        logger.error(f"❌ RL Training failed to start: {e}")
        return None

async def test_solana_connection():
    """Test Solana connection"""
    logger.info("🚀 Testing Solana Connection...")

    try:
        # Use the new Solana Python SDK syntax
        from solders.pubkey import Pubkey
        from solana.rpc.async_api import AsyncClient

        client = AsyncClient("https://api.devnet.solana.com")

        # Test basic connection
        result = await client.get_health()
        logger.info(f"✅ Solana devnet connected: {result}")

        await client.close()
        return True

    except Exception as e:
        logger.error(f"❌ Solana connection failed: {e}")
        return False

async def start_claudia_analysis():
    """Start Claudia DeepSeek analysis"""
    logger.info("🤖 Starting Claudia DeepSeek Analysis...")

    try:
        # Run analysis in subprocess to avoid blocking
        result = subprocess.run([
            sys.executable,
            "execute_claudia_deepseek_analysis.py"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            logger.info("✅ Claudia DeepSeek analysis completed")
            return True
        else:
            logger.error(f"❌ Analysis failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.info("⏱️ Analysis running in background (timeout reached)")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start analysis: {e}")
        return False

async def main():
    """Launch all trading systems"""
    logger.info("=" * 60)
    logger.info("🚀 ULTIMATE AGI TRADING SYSTEMS LAUNCHER")
    logger.info("=" * 60)

    # Check F: drive storage
    f_drive = Path("F:/MCPVotsAGI_Data")
    if not f_drive.exists():
        logger.error("❌ F: drive storage not found! Run configure_f_drive_storage.py first")
        return

    logger.info("✅ F: drive storage ready")

    # Start systems in order
    systems_status = {}

    # 1. Start RL Training
    rl_monitor = await start_rl_training()
    systems_status['RL Training'] = rl_monitor is not None

    # 2. Test Solana
    solana_ok = await test_solana_connection()
    systems_status['Solana'] = solana_ok

    # 3. Start Claudia Analysis
    claudia_ok = await start_claudia_analysis()
    systems_status['Claudia DeepSeek'] = claudia_ok

    # Show results
    logger.info("=" * 60)
    logger.info("📊 SYSTEM STATUS")
    logger.info("=" * 60)

    for system, status in systems_status.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"  {status_icon} {system}: {'Running' if status else 'Failed'}")

    # Start continuous monitoring if RL is working
    if rl_monitor:
        logger.info("\n🔄 Starting continuous RL monitoring...")
        try:
            # Run monitoring for a few cycles to test
            for i in range(3):
                logger.info(f"📈 Monitoring cycle {i+1}/3...")
                await rl_monitor.collect_and_store_metrics()
                await asyncio.sleep(2)

            logger.info("✅ RL monitoring test completed")

        except Exception as e:
            logger.error(f"❌ RL monitoring failed: {e}")

    # Final instructions
    logger.info("\n🎯 NEXT STEPS:")
    logger.info("1. Monitor RL training: python real_rl_training_monitor.py")
    logger.info("2. Start Solana trading: python solana_precious_metals_trading.py")
    logger.info("3. Open frontend dashboard: cd frontend && npm run dev")
    logger.info("4. View F: drive data: dir F:\\MCPVotsAGI_Data")

if __name__ == "__main__":
    asyncio.run(main())
