#!/usr/bin/env python3
"""
Ultimate Memory System for AGI
==============================
Comprehensive memory management with multiple backends
"""

import asyncio
import json
import sqlite3
import hashlib
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import pickle
import logging

# Advanced imports
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    import networkx as nx
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_ADVANCED = True
except ImportError:
    HAS_ADVANCED = False
    print("Advanced memory features not available. Install: pip install chromadb sentence-transformers networkx scikit-learn")

logger = logging.getLogger(__name__)

class MemoryType:
    """Memory type definitions"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"

class UltimateMemorySystem:
    """Ultimate memory system with multiple backends and AI capabilities"""
    
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize memory stores
        self.short_term_memory = deque(maxlen=1000)  # Recent memories
        self.working_memory = {}  # Current context
        self.memory_index = defaultdict(list)  # Fast lookup
        
        # Initialize databases
        self._init_databases()
        
        # Initialize advanced features if available
        if HAS_ADVANCED:
            self._init_advanced_features()
        
        logger.info("🧠 Ultimate Memory System initialized")
    
    def _init_databases(self):
        """Initialize SQLite databases for persistent storage"""
        # Main memory database
        self.db_path = self.memory_dir / "ultimate_memory.db"
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            -- Core memory table
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                embedding BLOB,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                tags TEXT
            );
            
            -- Knowledge graph nodes
            CREATE TABLE IF NOT EXISTS knowledge_nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                type TEXT,
                properties TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Knowledge graph edges
            CREATE TABLE IF NOT EXISTS knowledge_edges (
                source_id TEXT,
                target_id TEXT,
                relationship TEXT,
                weight REAL DEFAULT 1.0,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id, relationship),
                FOREIGN KEY (source_id) REFERENCES knowledge_nodes(id),
                FOREIGN KEY (target_id) REFERENCES knowledge_nodes(id)
            );
            
            -- Memory associations
            CREATE TABLE IF NOT EXISTS memory_associations (
                memory_id TEXT,
                associated_id TEXT,
                strength REAL DEFAULT 0.5,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (memory_id, associated_id),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            );
            
            -- Conversation history
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
            CREATE INDEX IF NOT EXISTS idx_knowledge_label ON knowledge_nodes(label);
            CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
        """)
        self.conn.commit()
    
    def _init_advanced_features(self):
        """Initialize advanced AI-powered features"""
        # Vector database for semantic search
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.memory_dir / "chroma")
        )
        
        # Get or create collections
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="memories",
            metadata={"description": "AGI memory embeddings"}
        )
        
        self.knowledge_collection = self.chroma_client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "Knowledge graph embeddings"}
        )
        
        # Embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Knowledge graph
        self.knowledge_graph = nx.DiGraph()
        self._load_knowledge_graph()
        
        logger.info("🚀 Advanced memory features initialized")
    
    async def store_memory(self, 
                          content: str, 
                          memory_type: str = MemoryType.SHORT_TERM,
                          metadata: Dict = None,
                          importance: float = 0.5,
                          tags: List[str] = None) -> str:
        """Store a new memory"""
        memory_id = hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()
        
        # Generate embedding if available
        embedding = None
        if HAS_ADVANCED:
            embedding = self.embedder.encode(content)
            
            # Store in vector database
            self.memory_collection.add(
                documents=[content],
                embeddings=[embedding.tolist()],
                ids=[memory_id],
                metadatas=[metadata or {}]
            )
        
        # Store in SQLite
        self.conn.execute("""
            INSERT INTO memories (id, type, content, metadata, embedding, importance, tags, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            memory_type,
            content,
            json.dumps(metadata or {}),
            pickle.dumps(embedding) if embedding is not None else None,
            importance,
            json.dumps(tags or []),
            datetime.now()
        ))
        self.conn.commit()
        
        # Add to short-term memory
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term_memory.append({
                'id': memory_id,
                'content': content,
                'timestamp': datetime.now()
            })
        
        # Update memory index
        if tags:
            for tag in tags:
                self.memory_index[tag].append(memory_id)
        
        logger.info(f"💾 Stored {memory_type} memory: {memory_id[:8]}...")
        return memory_id
    
    async def recall_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recall memories based on query"""
        results = []
        
        if HAS_ADVANCED:
            # Semantic search using vector database
            query_embedding = self.embedder.encode(query)
            search_results = self.memory_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            if search_results['ids'][0]:
                memory_ids = search_results['ids'][0]
                
                # Fetch full memory data
                for memory_id in memory_ids:
                    cursor = self.conn.execute("""
                        SELECT * FROM memories WHERE id = ?
                    """, (memory_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        # Update access count
                        self.conn.execute("""
                            UPDATE memories 
                            SET access_count = access_count + 1,
                                last_accessed = ?
                            WHERE id = ?
                        """, (datetime.now(), memory_id))
                        
                        results.append({
                            'id': row['id'],
                            'type': row['type'],
                            'content': row['content'],
                            'metadata': json.loads(row['metadata']),
                            'importance': row['importance'],
                            'created_at': row['created_at']
                        })
        else:
            # Fallback to keyword search
            cursor = self.conn.execute("""
                SELECT * FROM memories 
                WHERE content LIKE ? 
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            """, (f"%{query}%", top_k))
            
            for row in cursor:
                results.append({
                    'id': row['id'],
                    'type': row['type'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']),
                    'importance': row['importance'],
                    'created_at': row['created_at']
                })
        
        self.conn.commit()
        return results
    
    async def add_knowledge(self, subject: str, predicate: str, object: str, properties: Dict = None):
        """Add knowledge to the graph"""
        # Create nodes if they don't exist
        for node in [subject, object]:
            node_id = hashlib.md5(node.encode()).hexdigest()
            
            # Check if node exists
            cursor = self.conn.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (node_id,))
            if not cursor.fetchone():
                # Create node
                embedding = None
                if HAS_ADVANCED:
                    embedding = self.embedder.encode(node)
                    self.knowledge_collection.add(
                        documents=[node],
                        embeddings=[embedding.tolist()],
                        ids=[node_id],
                        metadatas=[{"label": node}]
                    )
                
                self.conn.execute("""
                    INSERT INTO knowledge_nodes (id, label, embedding)
                    VALUES (?, ?, ?)
                """, (node_id, node, pickle.dumps(embedding) if embedding else None))
        
        # Create edge
        subject_id = hashlib.md5(subject.encode()).hexdigest()
        object_id = hashlib.md5(object.encode()).hexdigest()
        
        self.conn.execute("""
            INSERT OR REPLACE INTO knowledge_edges (source_id, target_id, relationship, properties)
            VALUES (?, ?, ?, ?)
        """, (subject_id, object_id, predicate, json.dumps(properties or {})))
        
        self.conn.commit()
        
        # Update networkx graph if available
        if HAS_ADVANCED:
            self.knowledge_graph.add_edge(subject, object, relationship=predicate, **(properties or {}))
        
        logger.info(f"📊 Added knowledge: {subject} --{predicate}--> {object}")
    
    async def query_knowledge(self, query: str) -> List[Dict]:
        """Query the knowledge graph"""
        results = []
        
        if HAS_ADVANCED:
            # Find relevant nodes
            query_embedding = self.embedder.encode(query)
            search_results = self.knowledge_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=10
            )
            
            if search_results['ids'][0]:
                # Get connected knowledge
                for node_id in search_results['ids'][0]:
                    cursor = self.conn.execute("""
                        SELECT n1.label as subject, e.relationship, n2.label as object, e.properties
                        FROM knowledge_edges e
                        JOIN knowledge_nodes n1 ON e.source_id = n1.id
                        JOIN knowledge_nodes n2 ON e.target_id = n2.id
                        WHERE e.source_id = ? OR e.target_id = ?
                    """, (node_id, node_id))
                    
                    for row in cursor:
                        results.append({
                            'subject': row['subject'],
                            'predicate': row['relationship'],
                            'object': row['object'],
                            'properties': json.loads(row['properties'])
                        })
        
        return results
    
    async def consolidate_memories(self):
        """Consolidate short-term memories into long-term"""
        # Get recent short-term memories
        cursor = self.conn.execute("""
            SELECT * FROM memories 
            WHERE type = ? AND created_at < ?
            ORDER BY importance DESC, access_count DESC
            LIMIT 100
        """, (MemoryType.SHORT_TERM, datetime.now() - timedelta(hours=1)))
        
        for row in cursor:
            # Evaluate for long-term storage
            if row['importance'] > 0.7 or row['access_count'] > 5:
                # Promote to long-term
                self.conn.execute("""
                    UPDATE memories SET type = ? WHERE id = ?
                """, (MemoryType.LONG_TERM, row['id']))
                
                logger.info(f"📈 Promoted memory {row['id'][:8]}... to long-term")
        
        self.conn.commit()
    
    async def forget_memories(self, threshold_days: int = 30):
        """Forget old, unimportant memories"""
        cutoff_date = datetime.now() - timedelta(days=threshold_days)
        
        # Delete expired memories
        self.conn.execute("""
            DELETE FROM memories 
            WHERE expires_at < ? OR (
                created_at < ? AND 
                importance < 0.3 AND 
                access_count < 2
            )
        """, (datetime.now(), cutoff_date))
        
        deleted = self.conn.total_changes
        self.conn.commit()
        
        if deleted > 0:
            logger.info(f"🗑️ Forgot {deleted} old memories")
    
    def _load_knowledge_graph(self):
        """Load knowledge graph from database"""
        if not HAS_ADVANCED:
            return
        
        cursor = self.conn.execute("""
            SELECT n1.label as subject, e.relationship, n2.label as object, e.properties
            FROM knowledge_edges e
            JOIN knowledge_nodes n1 ON e.source_id = n1.id
            JOIN knowledge_nodes n2 ON e.target_id = n2.id
        """)
        
        for row in cursor:
            properties = json.loads(row['properties'])
            self.knowledge_graph.add_edge(
                row['subject'], 
                row['object'], 
                relationship=row['relationship'],
                **properties
            )
    
    async def get_memory_stats(self) -> Dict:
        """Get memory system statistics"""
        stats = {}
        
        # Count memories by type
        cursor = self.conn.execute("""
            SELECT type, COUNT(*) as count 
            FROM memories 
            GROUP BY type
        """)
        
        stats['memory_counts'] = {row['type']: row['count'] for row in cursor}
        
        # Total memories
        cursor = self.conn.execute("SELECT COUNT(*) as total FROM memories")
        stats['total_memories'] = cursor.fetchone()['total']
        
        # Knowledge graph stats
        cursor = self.conn.execute("SELECT COUNT(*) as total FROM knowledge_nodes")
        stats['knowledge_nodes'] = cursor.fetchone()['total']
        
        cursor = self.conn.execute("SELECT COUNT(*) as total FROM knowledge_edges")
        stats['knowledge_edges'] = cursor.fetchone()['total']
        
        # Recent activity
        cursor = self.conn.execute("""
            SELECT COUNT(*) as recent FROM memories 
            WHERE created_at > ?
        """, (datetime.now() - timedelta(hours=24),))
        stats['memories_24h'] = cursor.fetchone()['recent']
        
        return stats
    
    async def backup_memory(self, backup_path: Path = None):
        """Backup memory to file"""
        if not backup_path:
            backup_path = self.memory_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # Create backup
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        logger.info(f"💾 Memory backed up to {backup_path}")
        return backup_path
    
    async def save_conversation(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Save conversation to history"""
        conv_id = hashlib.md5(f"{session_id}{datetime.now()}".encode()).hexdigest()
        
        self.conn.execute("""
            INSERT INTO conversations (id, session_id, role, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (conv_id, session_id, role, content, json.dumps(metadata or {})))
        
        self.conn.commit()
        return conv_id
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        cursor = self.conn.execute("""
            SELECT * FROM conversations 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (session_id, limit))
        
        history = []
        for row in cursor:
            history.append({
                'role': row['role'],
                'content': row['content'],
                'metadata': json.loads(row['metadata']),
                'timestamp': row['created_at']
            })
        
        return list(reversed(history))  # Return in chronological order
    
    def close(self):
        """Close database connections"""
        self.conn.close()
        logger.info("🔒 Memory system closed")

# Example usage and testing
async def test_memory_system():
    """Test the memory system"""
    workspace = Path("C:/Workspace/MCPVotsAGI")
    memory = UltimateMemorySystem(workspace)
    
    # Store some memories
    await memory.store_memory(
        "The user prefers dark mode interfaces",
        memory_type=MemoryType.LONG_TERM,
        tags=["preferences", "ui"]
    )
    
    await memory.store_memory(
        "DeepSeek-R1 is the primary reasoning model",
        memory_type=MemoryType.SEMANTIC,
        importance=0.9,
        tags=["system", "ai", "models"]
    )
    
    # Add knowledge
    await memory.add_knowledge("DeepSeek-R1", "is_a", "Language Model")
    await memory.add_knowledge("DeepSeek-R1", "used_for", "Complex Reasoning")
    await memory.add_knowledge("MCPVotsAGI", "uses", "DeepSeek-R1")
    
    # Recall memories
    memories = await memory.recall_memory("deepseek")
    print(f"Found {len(memories)} relevant memories")
    
    # Get stats
    stats = await memory.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    memory.close()

if __name__ == "__main__":
    asyncio.run(test_memory_system())