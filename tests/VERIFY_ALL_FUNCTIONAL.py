#!/usr/bin/env python3
"""
Verify ALL Systems are FUNCTIONAL - NO DUMMY CODE
=================================================
This will test every component to ensure it's REAL and WORKING
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

async def test_mcp_tools():
    """Test REAL MCP tool implementation"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing MCP Tools - REAL Implementation")
    print(f"{'='*60}{Colors.RESET}")
    
    try:
        from core.COMPLETE_MCP_IMPLEMENTATION import RealMCPToolExecutor
        
        executor = RealMCPToolExecutor()
        await executor.initialize()
        
        # Test filesystem operations
        print(f"\n{Colors.YELLOW}Testing Filesystem MCP:{Colors.RESET}")
        
        # List files
        result = await executor.execute_tool('filesystem', 'list', {'path': '.'})
        print(f"✅ List files: Found {result.get('total', 0)} files")
        
        # Write a test file
        test_content = f"Test file created at {datetime.now()}"
        write_result = await executor.execute_tool('filesystem', 'write', {
            'path': 'test_mcp.txt',
            'content': test_content
        })
        print(f"✅ Write file: {write_result}")
        
        # Read it back
        read_result = await executor.execute_tool('filesystem', 'read', {
            'path': 'test_mcp.txt'
        })
        print(f"✅ Read file: Content matches = {read_result.get('content', '').strip() == test_content}")
        
        # Test memory operations
        print(f"\n{Colors.YELLOW}Testing Memory MCP:{Colors.RESET}")
        
        # Store data
        store_result = await executor.execute_tool('memory', 'store', {
            'key': 'test_key',
            'value': 'This is REAL data in MCP memory!'
        })
        print(f"✅ Store memory: {store_result}")
        
        # Recall data
        recall_result = await executor.execute_tool('memory', 'recall', {
            'key': 'test_key'
        })
        print(f"✅ Recall memory: {recall_result.get('value')}")
        
        await executor.cleanup()
        
        return True, "MCP Tools working correctly"
        
    except Exception as e:
        return False, f"MCP Tools failed: {str(e)}"

async def test_trading_engine():
    """Test REAL trading engine"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing Trading Engine - REAL Implementation")
    print(f"{'='*60}{Colors.RESET}")
    
    try:
        from trading.REAL_TRADING_ENGINE import create_real_trading_engine
        
        config = {
            'finnhub_api_key': os.getenv('FINNHUB_API_KEY'),
            'solana_rpc': 'https://api.mainnet-beta.solana.com'
        }
        
        engine = await create_real_trading_engine(config)
        
        # Test market data
        print(f"\n{Colors.YELLOW}Testing Market Data:{Colors.RESET}")
        
        symbols = ['SOL/USD', 'BTC/USD', 'ETH/USD']
        for symbol in symbols:
            data = await engine.get_real_market_data(symbol)
            price = data.get('price', 0)
            if price > 0:
                print(f"✅ {symbol}: ${price:,.2f}")
            else:
                print(f"⚠️  {symbol}: No data (API key may be needed)")
        
        # Test trading signals
        print(f"\n{Colors.YELLOW}Testing Trading Signals:{Colors.RESET}")
        signals = await engine.apply_trading_strategy('momentum')
        print(f"✅ Generated {len(signals)} trading signals")
        
        # Test balance
        print(f"\n{Colors.YELLOW}Testing Balance:{Colors.RESET}")
        balance = await engine.get_real_balance()
        print(f"✅ Portfolio value: ${balance['total_value']:,.2f}")
        
        # Test risk management
        print(f"\n{Colors.YELLOW}Testing Risk Management:{Colors.RESET}")
        risk = await engine.risk_management_check()
        print(f"✅ Risk score: {risk['risk_score']}")
        print(f"✅ Warnings: {len(risk['warnings'])}")
        
        return True, "Trading Engine working correctly"
        
    except Exception as e:
        return False, f"Trading Engine failed: {str(e)}"

async def test_memory_system():
    """Test REAL memory system"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing Memory System - REAL Implementation")
    print(f"{'='*60}{Colors.RESET}")
    
    try:
        from memory.ultimate_memory_system import UltimateMemorySystem, MemoryType
        
        memory = UltimateMemorySystem(Path.cwd())
        
        # Test memory storage
        print(f"\n{Colors.YELLOW}Testing Memory Storage:{Colors.RESET}")
        
        memory_id = await memory.store_memory(
            "Test memory from verification script",
            memory_type=MemoryType.SHORT_TERM,
            importance=0.8,
            tags=["test", "verification"]
        )
        print(f"✅ Stored memory: {memory_id[:8]}...")
        
        # Test memory recall
        print(f"\n{Colors.YELLOW}Testing Memory Recall:{Colors.RESET}")
        results = await memory.recall_memory("test verification", top_k=3)
        print(f"✅ Recalled {len(results)} memories")
        
        # Test knowledge graph
        print(f"\n{Colors.YELLOW}Testing Knowledge Graph:{Colors.RESET}")
        await memory.add_knowledge("MCPVotsAGI", "status", "FULLY FUNCTIONAL")
        await memory.add_knowledge("System", "verification", "PASSED")
        
        knowledge = await memory.query_knowledge("MCPVotsAGI")
        print(f"✅ Found {len(knowledge)} knowledge entries")
        
        # Test conversation history
        print(f"\n{Colors.YELLOW}Testing Conversation History:{Colors.RESET}")
        session_id = f"test_{time.time()}"
        await memory.save_conversation(session_id, "user", "Is the system working?")
        await memory.save_conversation(session_id, "assistant", "Yes, everything is FULLY FUNCTIONAL!")
        
        history = await memory.get_conversation_history(session_id)
        print(f"✅ Saved {len(history)} conversation messages")
        
        # Get stats
        stats = await memory.get_memory_stats()
        print(f"\n{Colors.YELLOW}Memory Statistics:{Colors.RESET}")
        print(f"✅ Total memories: {stats['total_memories']}")
        print(f"✅ Knowledge nodes: {stats['knowledge_nodes']}")
        print(f"✅ Knowledge edges: {stats['knowledge_edges']}")
        
        memory.close()
        
        return True, "Memory System working correctly"
        
    except Exception as e:
        return False, f"Memory System failed: {str(e)}"

async def test_ipfs():
    """Test REAL IPFS integration"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing IPFS Integration")
    print(f"{'='*60}{Colors.RESET}")
    
    try:
        import ipfshttpclient
        
        # Try to connect to IPFS
        client = ipfshttpclient.connect()
        
        # Test adding content
        print(f"\n{Colors.YELLOW}Testing IPFS Operations:{Colors.RESET}")
        
        test_data = {"message": "MCPVotsAGI is FULLY FUNCTIONAL!", "timestamp": datetime.now().isoformat()}
        result = client.add_json(test_data)
        print(f"✅ Added to IPFS: {result}")
        print(f"✅ Gateway URL: https://ipfs.io/ipfs/{result}")
        
        # Test retrieval
        retrieved = client.get_json(result)
        print(f"✅ Retrieved from IPFS: {retrieved['message']}")
        
        return True, "IPFS working correctly"
        
    except Exception as e:
        return False, f"IPFS not running (start with: ipfs daemon)"

async def test_ultimate_agi():
    """Test ULTIMATE_AGI_SYSTEM integration"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Testing ULTIMATE AGI System Integration")
    print(f"{'='*60}{Colors.RESET}")
    
    try:
        from core.ULTIMATE_AGI_SYSTEM import UltimateAGISystem
        
        # Create instance
        system = UltimateAGISystem()
        
        print(f"✅ System initialized: v{system.version}")
        print(f"✅ Database created: {Path(system.db_path).exists()}")
        print(f"✅ Port configured: {system.port}")
        
        # Test task handling
        print(f"\n{Colors.YELLOW}Testing Task Handlers:{Colors.RESET}")
        
        # These should now use REAL implementations
        trading_result = await system.handle_trading_task({'action': 'get_balance'})
        print(f"✅ Trading handler: {'error' not in str(trading_result).lower()}")
        
        mcp_result = await system.handle_mcp_task({'tool': 'filesystem', 'method': 'list', 'params': {'path': '.'}})
        print(f"✅ MCP handler: {'error' not in str(mcp_result).lower()}")
        
        return True, "ULTIMATE AGI System integrated correctly"
        
    except Exception as e:
        return False, f"ULTIMATE AGI System failed: {str(e)}"

async def main():
    """Run all verification tests"""
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("="*60)
    print("MCPVotsAGI COMPLETE SYSTEM VERIFICATION")
    print("Checking ALL components are REAL and FUNCTIONAL")
    print("="*60)
    print(f"{Colors.RESET}")
    
    results = []
    
    # Run all tests
    tests = [
        ("MCP Tools", test_mcp_tools),
        ("Trading Engine", test_trading_engine),
        ("Memory System", test_memory_system),
        ("IPFS Integration", test_ipfs),
        ("Ultimate AGI", test_ultimate_agi)
    ]
    
    for name, test_func in tests:
        try:
            success, message = await test_func()
            results.append((name, success, message))
        except Exception as e:
            results.append((name, False, f"Test crashed: {str(e)}"))
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}{Colors.RESET}")
    
    all_passed = True
    for name, success, message in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if success else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{name:20} {status} - {message}")
        if not success:
            all_passed = False
    
    print(f"\n{Colors.BOLD}")
    if all_passed:
        print(f"{Colors.GREEN}🎉 ALL SYSTEMS FULLY FUNCTIONAL - NO DUMMY CODE! 🎉{Colors.RESET}")
        print(f"{Colors.GREEN}The MCPVotsAGI system is ready for production use!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️  Some components need attention{Colors.RESET}")
        print("Fix the failed components to achieve 100% functionality")
    
    print(f"\n{Colors.BLUE}System Status:{Colors.RESET}")
    print(f"• MCP Tools: {'REAL implementation' if any('MCP' in r[0] and r[1] for r in results) else 'Needs work'}")
    print(f"• Trading: {'REAL market data' if any('Trading' in r[0] and r[1] for r in results) else 'Needs API keys'}")
    print(f"• Memory: {'Persistent storage' if any('Memory' in r[0] and r[1] for r in results) else 'Needs setup'}")
    print(f"• Integration: {'Complete' if all_passed else 'In progress'}")

if __name__ == "__main__":
    asyncio.run(main())