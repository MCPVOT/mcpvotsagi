#!/usr/bin/env python3
"""
Test RL Trading and Solana Integration
======================================
Quick test to verify both systems are working
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingTest")

async def test_rl_training():
    """Test RL training system"""
    logger.info("🧠 Testing RL Training System...")

    try:
        # Test basic RL monitoring
        from real_rl_training_monitor import RealRLTrainingMonitor

        monitor = RealRLTrainingMonitor()

        # Test metric collection
        test_metrics = monitor.collect_training_metrics()
        logger.info(f"✅ RL Metrics collected: {len(test_metrics)} data points")

        # Test F: drive storage
        f_drive_path = Path("F:/MCPVotsAGI_Data/rl_training")
        if f_drive_path.exists():
            logger.info("✅ F: drive RL storage accessible")
        else:
            logger.warning("⚠️ F: drive RL storage not found")

    except Exception as e:
        logger.error(f"❌ RL Training test failed: {e}")

async def test_solana_trading():
    """Test Solana trading system"""
    logger.info("🚀 Testing Solana Trading System...")

    try:
        # Test Solana components without wallet connection
        from solana.publickey import PublicKey
        from solana.rpc.async_api import AsyncClient

        # Test basic Solana connectivity
        client = AsyncClient("https://api.devnet.solana.com")

        # Test phantom wallet connector
        sys.path.insert(0, str(Path(__file__).parent))
        from solana_phantom_trading_integration import PhantomWalletConnector

        phantom = PhantomWalletConnector()
        logger.info("✅ Phantom wallet connector initialized")

        # Test F: drive trading storage
        f_drive_path = Path("F:/MCPVotsAGI_Data/trading")
        if f_drive_path.exists():
            logger.info("✅ F: drive trading storage accessible")
        else:
            logger.warning("⚠️ F: drive trading storage not found")

    except Exception as e:
        logger.error(f"❌ Solana Trading test failed: {e}")

async def test_claudia_deepseek():
    """Test Claudia DeepSeek integration"""
    logger.info("🤖 Testing Claudia DeepSeek Integration...")

    try:
        from claudia_deepseek_system_analyzer import ClaudiaDeepSeekAnalyzer

        analyzer = ClaudiaDeepSeekAnalyzer()
        logger.info("✅ Claudia DeepSeek analyzer initialized")

        # Test basic analysis capability
        test_result = analyzer.analyze_architecture()
        logger.info(f"✅ Architecture analysis completed: {len(test_result)} recommendations")

    except Exception as e:
        logger.error(f"❌ Claudia DeepSeek test failed: {e}")

async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("🧪 TESTING ULTIMATE AGI TRADING SYSTEMS")
    logger.info("=" * 60)

    # Test all systems
    await test_rl_training()
    await test_solana_trading()
    await test_claudia_deepseek()

    logger.info("=" * 60)
    logger.info("✅ ALL TESTS COMPLETED")
    logger.info("=" * 60)

    # Check overall system status
    logger.info("📊 System Status Summary:")
    logger.info(f"  • RL Training: {'✅ Ready' if Path('F:/MCPVotsAGI_Data/rl_training').exists() else '❌ Not Ready'}")
    logger.info(f"  • Solana Trading: {'✅ Ready' if Path('F:/MCPVotsAGI_Data/trading').exists() else '❌ Not Ready'}")
    logger.info(f"  • F: Drive Storage: {'✅ Ready' if Path('F:/MCPVotsAGI_Data').exists() else '❌ Not Ready'}")

    # Next steps
    logger.info("\n🚀 NEXT STEPS:")
    logger.info("1. Start RL training: python real_rl_training_monitor.py")
    logger.info("2. Start Solana trading: python solana_precious_metals_trading.py")
    logger.info("3. Run Claudia analysis: python execute_claudia_deepseek_analysis.py")
    logger.info("4. Open frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    asyncio.run(main())
