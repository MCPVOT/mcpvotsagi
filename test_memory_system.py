#!/usr/bin/env python3
"""
Test the Ultimate Memory System
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

async def main():
    print("🧪 Testing Ultimate Memory System...")
    
    try:
        from memory.ultimate_memory_system import UltimateMemorySystem, MemoryType
        
        # Initialize memory system
        memory = UltimateMemorySystem(Path("C:/Workspace/MCPVotsAGI"))
        
        # Store some test memories
        print("\n📝 Storing memories...")
        
        # User preferences
        await memory.store_memory(
            "User prefers dark mode and minimalist UI design",
            memory_type=MemoryType.LONG_TERM,
            importance=0.8,
            tags=["preferences", "ui", "user"]
        )
        
        # System knowledge
        await memory.store_memory(
            "DeepSeek-R1 is the primary reasoning model for complex decisions",
            memory_type=MemoryType.SEMANTIC,
            importance=0.9,
            tags=["system", "models", "deepseek"]
        )
        
        # Trading knowledge
        await memory.store_memory(
            "The trading system uses multi-agent DGM algorithms for decision making",
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
            tags=["trading", "algorithms", "agents"]
        )
        
        # Add knowledge graph entries
        print("\n🕸️ Building knowledge graph...")
        await memory.add_knowledge("MCPVotsAGI", "uses", "DeepSeek-R1")
        await memory.add_knowledge("MCPVotsAGI", "integrates", "Ollama")
        await memory.add_knowledge("MCPVotsAGI", "stores_data_on", "F: Drive")
        await memory.add_knowledge("DeepSeek-R1", "is_a", "Language Model")
        await memory.add_knowledge("DeepSeek-R1", "specializes_in", "Complex Reasoning")
        await memory.add_knowledge("TradingAgents", "implements", "DGM Algorithms")
        await memory.add_knowledge("Ultimate AGI", "consolidates", "All Dashboards")
        
        # Test conversation storage
        print("\n💬 Storing conversation...")
        session_id = "test_session_001"
        await memory.save_conversation(session_id, "user", "What is the primary AI model?")
        await memory.save_conversation(session_id, "assistant", "The primary AI model is DeepSeek-R1, which specializes in complex reasoning and decision-making.")
        
        # Test memory recall
        print("\n🔍 Testing memory recall...")
        
        # Search for DeepSeek
        results = await memory.recall_memory("deepseek", top_k=3)
        print(f"Found {len(results)} memories about DeepSeek:")
        for mem in results:
            print(f"  - {mem['content'][:80]}...")
        
        # Search for trading
        results = await memory.recall_memory("trading", top_k=3)
        print(f"\nFound {len(results)} memories about trading:")
        for mem in results:
            print(f"  - {mem['content'][:80]}...")
        
        # Query knowledge graph
        print("\n🧠 Querying knowledge graph...")
        knowledge = await memory.query_knowledge("MCPVotsAGI")
        print(f"Found {len(knowledge)} knowledge entries about MCPVotsAGI:")
        for k in knowledge:
            print(f"  - {k['subject']} {k['predicate']} {k['object']}")
        
        # Get conversation history
        print("\n📜 Retrieving conversation history...")
        history = await memory.get_conversation_history(session_id)
        print(f"Found {len(history)} messages in conversation:")
        for msg in history:
            print(f"  [{msg['role']}]: {msg['content']}")
        
        # Get memory statistics
        print("\n📊 Memory System Statistics:")
        stats = await memory.get_memory_stats()
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Memory types: {stats['memory_counts']}")
        print(f"  Knowledge nodes: {stats['knowledge_nodes']}")
        print(f"  Knowledge edges: {stats['knowledge_edges']}")
        print(f"  Recent memories (24h): {stats['memories_24h']}")
        
        # Test memory consolidation
        print("\n🔄 Testing memory consolidation...")
        await memory.consolidate_memories()
        
        # Close the system
        memory.close()
        
        print("\n✅ Memory system test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing memory system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())