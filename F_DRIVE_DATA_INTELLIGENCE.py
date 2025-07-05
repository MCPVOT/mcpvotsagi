#!/usr/bin/env python3
"""
F: Drive Data Intelligence System
=================================
Demonstrates how ULTIMATE AGI uses F: drive for:
- RL trading data storage and analysis
- Memory persistence and retrieval
- Context management for 1M tokens
- Knowledge graph operations
"""

import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
import numpy as np

# Import unified storage system
from src.core.unified_f_drive_storage import (
    storage_manager,
    get_storage_path,
    ensure_storage_path,
    get_storage_stats,
    initialize_storage
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataIntelligence")

class FDriveDataIntelligence:
    """Manages data intelligence operations on F: drive"""
    
    def __init__(self):
        self.storage = storage_manager
        self.initialized = False
        
    async def initialize(self):
        """Initialize F: drive for data intelligence"""
        logger.info("🧠 Initializing F: Drive Data Intelligence System...")
        
        # Initialize storage
        if initialize_storage():
            self.initialized = True
            
            # Show storage stats
            stats = get_storage_stats()
            logger.info(f"📊 Storage ready at: {stats['base_path']}")
            
            if stats.get('f_drive_available'):
                logger.info("✅ Using F: drive (800GB+ available)")
            else:
                logger.info("ℹ️ Using local storage (F: drive not available)")
                
            return True
        return False
        
    async def store_rl_trading_data(self, data: dict):
        """Store RL trading data to F: drive"""
        # Get RL trading path
        rl_path = ensure_storage_path('rl_trading', 'experience_replay')
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rl_experience_{timestamp}.json"
        filepath = rl_path / filename
        
        # Store data
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"💾 Stored RL data: {filename}")
        return filepath
        
    async def store_chat_memory(self, conversation: dict):
        """Store chat memory to F: drive"""
        # Get chat memory path
        chat_path = ensure_storage_path('chat_memory', 'conversations')
        
        # Create filename based on user and timestamp
        user_id = conversation.get('user_id', 'anonymous')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{user_id}_{timestamp}.json"
        filepath = chat_path / filename
        
        # Store conversation
        with open(filepath, 'w') as f:
            json.dump(conversation, f, indent=2)
            
        logger.info(f"💬 Stored chat memory: {filename}")
        return filepath
        
    async def store_market_data(self, market_data: dict):
        """Store market data for analysis"""
        # Get market data path
        market_path = ensure_storage_path('market_data', 'price_history')
        
        # Organize by date
        date_str = datetime.now().strftime("%Y%m%d")
        daily_path = market_path / date_str
        daily_path.mkdir(exist_ok=True)
        
        # Store market data
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"market_{timestamp}.json"
        filepath = daily_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(market_data, f, indent=2)
            
        logger.info(f"📈 Stored market data: {date_str}/{filename}")
        return filepath
        
    async def manage_context_cache(self, context_data: dict):
        """Manage 1M token context cache"""
        # Get context cache path
        context_path = ensure_storage_path('context_cache', 'active')
        
        # Calculate context size
        context_size = len(json.dumps(context_data))
        
        # Store if under 1M token equivalent (roughly 4MB)
        if context_size < 4 * 1024 * 1024:
            session_id = context_data.get('session_id', 'default')
            filename = f"context_{session_id}.json"
            filepath = context_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(context_data, f)
                
            logger.info(f"🧠 Cached context: {filename} ({context_size/1024:.1f}KB)")
        else:
            # Compress and archive large contexts
            archive_path = ensure_storage_path('context_cache', 'compressed')
            logger.info("📦 Context too large, compressing...")
            # Compression logic here
            
        return context_path
        
    async def analyze_stored_data(self):
        """Analyze data stored on F: drive"""
        logger.info("🔍 Analyzing F: drive data...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "categories": {}
        }
        
        # Get storage stats
        stats = get_storage_stats()
        
        for category, data in stats['categories'].items():
            if 'error' not in data and 'status' not in data:
                analysis['categories'][category] = {
                    'used_gb': data['used_gb'],
                    'file_count': data['file_count'],
                    'usage_percent': data['usage_percent']
                }
                
                # Category-specific analysis
                if category == 'rl_trading':
                    analysis['categories'][category]['insights'] = await self._analyze_rl_data()
                elif category == 'market_data':
                    analysis['categories'][category]['insights'] = await self._analyze_market_data()
                elif category == 'chat_memory':
                    analysis['categories'][category]['insights'] = await self._analyze_chat_data()
                    
        return analysis
        
    async def _analyze_rl_data(self):
        """Analyze RL trading data"""
        rl_path = get_storage_path('rl_trading', 'experience_replay')
        
        insights = {
            'total_experiences': 0,
            'recent_files': [],
            'performance_trend': 'analyzing...'
        }
        
        # Count experience files
        if rl_path.exists():
            files = list(rl_path.glob('*.json'))
            insights['total_experiences'] = len(files)
            
            # Get recent files
            recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            insights['recent_files'] = [f.name for f in recent_files]
            
        return insights
        
    async def _analyze_market_data(self):
        """Analyze market data"""
        market_path = get_storage_path('market_data', 'price_history')
        
        insights = {
            'days_of_data': 0,
            'total_data_points': 0,
            'latest_date': None
        }
        
        if market_path.exists():
            date_dirs = [d for d in market_path.iterdir() if d.is_dir()]
            insights['days_of_data'] = len(date_dirs)
            
            # Count total data points
            total_files = sum(len(list(d.glob('*.json'))) for d in date_dirs)
            insights['total_data_points'] = total_files
            
            # Get latest date
            if date_dirs:
                latest = max(date_dirs, key=lambda x: x.name)
                insights['latest_date'] = latest.name
                
        return insights
        
    async def _analyze_chat_data(self):
        """Analyze chat memory data"""
        chat_path = get_storage_path('chat_memory', 'conversations')
        
        insights = {
            'total_conversations': 0,
            'unique_users': set(),
            'avg_conversation_size': 0
        }
        
        if chat_path.exists():
            files = list(chat_path.glob('*.json'))
            insights['total_conversations'] = len(files)
            
            # Extract unique users
            for f in files:
                parts = f.stem.split('_')
                if len(parts) >= 2:
                    insights['unique_users'].add(parts[1])
                    
            insights['unique_users'] = len(insights['unique_users'])
            
            # Calculate average size
            if files:
                sizes = [f.stat().st_size for f in files]
                insights['avg_conversation_size'] = sum(sizes) / len(sizes) / 1024  # KB
                
        return insights
        
    async def demonstrate_intelligence_gathering(self):
        """Demonstrate data intelligence gathering capabilities"""
        logger.info("\n🚀 Demonstrating F: Drive Data Intelligence Capabilities\n")
        
        # 1. Store some sample RL data
        logger.info("1️⃣ Storing RL Trading Experience...")
        rl_data = {
            'state': [0.5, 0.3, 0.8, 0.2],
            'action': 'buy',
            'reward': 0.15,
            'next_state': [0.6, 0.4, 0.7, 0.3],
            'timestamp': datetime.now().isoformat()
        }
        await self.store_rl_trading_data(rl_data)
        
        # 2. Store chat memory
        logger.info("\n2️⃣ Storing Chat Memory...")
        chat_data = {
            'user_id': 'demo_user',
            'messages': [
                {'role': 'user', 'content': 'How do I analyze trading patterns?'},
                {'role': 'assistant', 'content': 'I can help you analyze patterns using our RL models...'}
            ],
            'timestamp': datetime.now().isoformat()
        }
        await self.store_chat_memory(chat_data)
        
        # 3. Store market data
        logger.info("\n3️⃣ Storing Market Data...")
        market_data = {
            'symbol': 'BTC/USD',
            'price': 45000,
            'volume': 1234567,
            'timestamp': datetime.now().isoformat()
        }
        await self.store_market_data(market_data)
        
        # 4. Manage context cache
        logger.info("\n4️⃣ Managing Context Cache...")
        context_data = {
            'session_id': 'demo_session',
            'context': 'Large language model context data...' * 100,
            'tokens_used': 5000
        }
        await self.manage_context_cache(context_data)
        
        # 5. Analyze all stored data
        logger.info("\n5️⃣ Analyzing Stored Data...")
        analysis = await self.analyze_stored_data()
        
        logger.info("\n📊 Data Intelligence Analysis:")
        logger.info(json.dumps(analysis, indent=2, default=str))
        
        # 6. Show storage statistics
        logger.info("\n6️⃣ Storage Statistics:")
        stats = get_storage_stats()
        
        if 'disk_usage' in stats and 'error' not in stats['disk_usage']:
            disk = stats['disk_usage']
            logger.info(f"💾 Disk Usage: {disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB ({disk['percent']:.1f}%)")
            
        logger.info("\n✅ F: Drive Data Intelligence System Demonstration Complete!")


async def main():
    """Main demonstration"""
    intelligence = FDriveDataIntelligence()
    
    # Initialize system
    if await intelligence.initialize():
        # Run demonstration
        await intelligence.demonstrate_intelligence_gathering()
    else:
        logger.error("Failed to initialize F: drive storage")


if __name__ == "__main__":
    asyncio.run(main())