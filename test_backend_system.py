#!/usr/bin/env python3
"""
Backend System Test Suite
=========================
Comprehensive tests for all backend components
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import aiohttp
from typing import Dict, Any, List
import numpy as np

# Add project paths
sys.path.append(str(Path(__file__).parent))

from unified_trading_backend import UnifiedTradingBackend, TradingConfig
from dgm_trading_algorithms import UnifiedTradingAlgorithmEngine, TradingStrategy, MarketState
from solana_mcp_deepseek_integration import SolanaMCPConnector
from knowledge_base_system import KnowledgeBaseSystem
from finnhub_integration import FinnhubClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BackendTester")


class BackendSystemTester:
    """Test all backend components"""
    
    def __init__(self):
        self.results = {
            "mcp_servers": {},
            "trading_algorithms": {},
            "integrations": {},
            "performance": {},
            "errors": []
        }
        
    async def test_mcp_servers(self):
        """Test all MCP server connections"""
        logger.info("\n" + "="*60)
        logger.info("TESTING MCP SERVERS")
        logger.info("="*60)
        
        servers = [
            ("Memory MCP", 3002, "/memory/status"),
            ("GitHub MCP", 3001, "/github/status"),
            ("Solana MCP", 3005, "/solana/status"),
            ("Browser Tools MCP", 3006, "/browser/status"),
            ("Oracle AGI", 3011, "/api/status")
        ]
        
        for name, port, endpoint in servers:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://localhost:{port}{endpoint}"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.results["mcp_servers"][name] = {
                                "status": "online",
                                "port": port,
                                "response": data
                            }
                            logger.info(f"✓ {name} - ONLINE on port {port}")
                        else:
                            self.results["mcp_servers"][name] = {
                                "status": "error",
                                "port": port,
                                "error": f"HTTP {resp.status}"
                            }
                            logger.error(f"✗ {name} - ERROR: HTTP {resp.status}")
            except Exception as e:
                self.results["mcp_servers"][name] = {
                    "status": "offline",
                    "port": port,
                    "error": str(e)
                }
                logger.warning(f"✗ {name} - OFFLINE: {str(e)[:50]}")
                
    async def test_trading_algorithms(self):
        """Test DGM and RL trading algorithms"""
        logger.info("\n" + "="*60)
        logger.info("TESTING TRADING ALGORITHMS")
        logger.info("="*60)
        
        # Test DGM
        try:
            engine = UnifiedTradingAlgorithmEngine()
            
            # Test signal generation
            market_data = {
                "price": 100.0,
                "volatility": 0.2,
                "trend": 0.5,
                "volume": 1000000,
                "sentiment": 0.6
            }
            
            signal = await engine.generate_trading_signal(market_data, "SOL")
            
            self.results["trading_algorithms"]["dgm"] = {
                "status": "working",
                "signal": {
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "strategy": signal.strategy_used
                }
            }
            
            logger.info(f"✓ DGM Algorithm - Signal: {signal.action} ({signal.confidence:.2%} confidence)")
            
        except Exception as e:
            self.results["trading_algorithms"]["dgm"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"✗ DGM Algorithm - Error: {e}")
            
    async def test_solana_integration(self):
        """Test Solana and Phantom integration"""
        logger.info("\n" + "="*60)
        logger.info("TESTING SOLANA INTEGRATION")
        logger.info("="*60)
        
        try:
            connector = SolanaMCPConnector()
            await connector.connect()
            
            # Test blockhash
            blockhash = await connector.get_latest_blockhash()
            self.results["integrations"]["solana_rpc"] = {
                "status": "connected",
                "blockhash": blockhash.get("blockhash", "none")
            }
            logger.info("✓ Solana RPC - Connected")
            
            # Test ZK proof generation
            proof = await connector.generate_zk_proof("test_data")
            self.results["integrations"]["zk_proof"] = {
                "status": "working",
                "commitment": proof.commitment[:20] + "..."
            }
            logger.info("✓ ZK Proof Generation - Working")
            
            await connector.close()
            
        except Exception as e:
            self.results["integrations"]["solana"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"✗ Solana Integration - Error: {e}")
            
    async def test_knowledge_base(self):
        """Test knowledge base system"""
        logger.info("\n" + "="*60)
        logger.info("TESTING KNOWLEDGE BASE")
        logger.info("="*60)
        
        try:
            kb = KnowledgeBaseSystem()
            
            # Test search
            results = await kb.search("Solana AI trading", collection="all", top_k=3)
            
            self.results["integrations"]["knowledge_base"] = {
                "status": "working",
                "documents_found": len(results),
                "collections": ["trading", "solana"]
            }
            
            logger.info(f"✓ Knowledge Base - Found {len(results)} documents")
            
        except Exception as e:
            self.results["integrations"]["knowledge_base"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"✗ Knowledge Base - Error: {e}")
            
    async def test_finnhub_integration(self):
        """Test Finnhub API integration"""
        logger.info("\n" + "="*60)
        logger.info("TESTING FINNHUB INTEGRATION")
        logger.info("="*60)
        
        try:
            client = FinnhubClient()
            
            # Test quote
            quote = await client.get_quote("AAPL")
            
            if quote:
                self.results["integrations"]["finnhub"] = {
                    "status": "working",
                    "sample_price": quote.current_price
                }
                logger.info(f"✓ Finnhub API - Working (AAPL: ${quote.current_price})")
            else:
                self.results["integrations"]["finnhub"] = {
                    "status": "no_data"
                }
                logger.warning("✗ Finnhub API - No data returned")
                
        except Exception as e:
            self.results["integrations"]["finnhub"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"✗ Finnhub API - Error: {e}")
            
    async def test_unified_backend(self):
        """Test the unified trading backend"""
        logger.info("\n" + "="*60)
        logger.info("TESTING UNIFIED BACKEND")
        logger.info("="*60)
        
        try:
            config = TradingConfig()
            backend = UnifiedTradingBackend(config)
            
            # Initialize
            await backend.initialize()
            
            # Test analysis
            result = await backend.analyze_and_trade("SOL", 0.01)
            
            self.results["integrations"]["unified_backend"] = {
                "status": "working",
                "signal": result["signal"]["action"],
                "confidence": result["signal"]["confidence"]
            }
            
            logger.info(f"✓ Unified Backend - Signal: {result['signal']['action']} "
                       f"({result['signal']['confidence']:.2%} confidence)")
            
        except Exception as e:
            self.results["integrations"]["unified_backend"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"✗ Unified Backend - Error: {e}")
            
    async def test_performance(self):
        """Test system performance"""
        logger.info("\n" + "="*60)
        logger.info("TESTING PERFORMANCE")
        logger.info("="*60)
        
        # Test response times
        timings = {}
        
        # Test trading signal generation speed
        start = datetime.now()
        engine = UnifiedTradingAlgorithmEngine()
        signal = await engine.generate_trading_signal({"price": 100}, "SOL")
        timings["signal_generation"] = (datetime.now() - start).total_seconds()
        
        # Test knowledge base search speed
        start = datetime.now()
        kb = KnowledgeBaseSystem()
        await kb.search("test query")
        timings["kb_search"] = (datetime.now() - start).total_seconds()
        
        self.results["performance"] = timings
        
        for operation, time in timings.items():
            status = "✓" if time < 1.0 else "⚠"
            logger.info(f"{status} {operation}: {time:.3f}s")
            
    def generate_report(self):
        """Generate test report"""
        logger.info("\n" + "="*60)
        logger.info("TEST REPORT SUMMARY")
        logger.info("="*60)
        
        # MCP Servers
        online_servers = sum(1 for s in self.results["mcp_servers"].values() 
                           if s.get("status") == "online")
        total_servers = len(self.results["mcp_servers"])
        logger.info(f"MCP Servers: {online_servers}/{total_servers} online")
        
        # Integrations
        working_integrations = sum(1 for i in self.results["integrations"].values()
                                 if i.get("status") == "working")
        total_integrations = len(self.results["integrations"])
        logger.info(f"Integrations: {working_integrations}/{total_integrations} working")
        
        # Performance
        avg_response = np.mean(list(self.results["performance"].values()))
        logger.info(f"Average Response Time: {avg_response:.3f}s")
        
        # Errors
        if self.results["errors"]:
            logger.warning(f"Errors Encountered: {len(self.results['errors'])}")
            
        # Save detailed report
        report_path = Path("test_results.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        logger.info(f"\nDetailed report saved to: {report_path}")
        
        return self.results


async def main():
    """Run all backend tests"""
    tester = BackendSystemTester()
    
    # Run tests
    await tester.test_mcp_servers()
    await tester.test_trading_algorithms()
    await tester.test_solana_integration()
    await tester.test_knowledge_base()
    await tester.test_finnhub_integration()
    await tester.test_unified_backend()
    await tester.test_performance()
    
    # Generate report
    report = tester.generate_report()
    
    # Overall status
    all_good = (
        all(s.get("status") == "online" for s in report["mcp_servers"].values()) and
        all(i.get("status") == "working" for i in report["integrations"].values())
    )
    
    if all_good:
        logger.info("\n✅ ALL SYSTEMS OPERATIONAL")
    else:
        logger.warning("\n⚠️  SOME SYSTEMS NEED ATTENTION")
        
    return report


if __name__ == "__main__":
    asyncio.run(main())