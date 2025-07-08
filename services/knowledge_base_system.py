#!/usr/bin/env python3
"""
Knowledge Base System with Solana AI Integration
===============================================
Vector database and knowledge graph for trading insights
Includes Solana AI documentation and best practices
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
import faiss
import networkx as nx
from dataclasses import dataclass
import hashlib
import pickle
import torch
from transformers import AutoTokenizer, AutoModel
import chromadb
from chromadb.config import Settings

# Import F: drive storage system
try:
    from src.core.unified_f_drive_storage import (
        get_storage_path,
        ensure_storage_path,
        storage_manager
    )
    HAS_F_DRIVE = True
except ImportError:
    HAS_F_DRIVE = False
    storage_manager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KnowledgeBaseSystem")


@dataclass
class KnowledgeDocument:
    """Knowledge document structure"""
    id: str
    title: str
    content: str
    source: str
    category: str
    timestamp: datetime
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class EmbeddingGenerator:
    """Generate embeddings for documents"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        # Tokenize
        inputs = self.tokenizer(
            text, 
            padding=True, 
            truncation=True, 
            max_length=512,
            return_tensors="pt"
        )
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.squeeze().numpy()


class KnowledgeBaseSystem:
    """Main knowledge base with vector search and knowledge graph"""
    
    def __init__(self, data_path: str = None):
        # Use F: drive if available, otherwise use local path
        if data_path is None:
            if HAS_F_DRIVE and storage_manager:
                # Use F: drive memory store for knowledge graph
                self.data_path = ensure_storage_path('memory_store', 'knowledge_graph')
                logger.info(f"Using F: drive storage at: {self.data_path}")
            else:
                # Fallback to local storage
                self.data_path = Path(os.environ.get(
                    'MCPVOTSAGI_MEMORY_PATH',
                    '/mnt/c/Workspace/MCPVotsAGI/knowledge'
                ))
                self.data_path.mkdir(exist_ok=True)
                logger.info(f"Using local storage at: {self.data_path}")
        else:
            self.data_path = Path(data_path)
            self.data_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.embedding_gen = EmbeddingGenerator()
        self.knowledge_graph = nx.DiGraph()
        
        # Initialize Chroma vector DB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.data_path / "chroma")
        ))
        
        # Get or create collections
        self.trading_collection = self.chroma_client.get_or_create_collection(
            name="trading_knowledge"
        )
        self.solana_collection = self.chroma_client.get_or_create_collection(
            name="solana_knowledge"
        )
        
        # FAISS index for fast similarity search
        self.dimension = 384  # Embedding dimension
        self.faiss_index = None
        self.document_store = {}
        
        # Load existing index if available
        self._load_index()
        
        # Initialize with Solana AI knowledge
        asyncio.create_task(self._init_solana_knowledge())
        
    async def _init_solana_knowledge(self):
        """Initialize Solana AI knowledge base"""
        
        # Core Solana AI concepts
        solana_docs = [
            {
                "title": "Solana AI Integration Overview",
                "content": """
                Solana provides powerful capabilities for AI integration:
                
                1. High Performance: 65,000 TPS enables real-time AI inference
                2. Low Cost: Fraction of a cent per transaction
                3. Parallel Processing: Sealevel runtime for concurrent execution
                4. GPU Integration: Direct GPU compute for AI models
                
                Key AI Use Cases on Solana:
                - On-chain AI inference
                - Decentralized AI training
                - AI-powered DeFi strategies
                - Zero-knowledge AI proofs
                - Autonomous trading agents
                """,
                "category": "solana_ai_overview"
            },
            {
                "title": "Building AI Agents on Solana",
                "content": """
                Steps to build AI agents on Solana:
                
                1. Smart Contract Development:
                   - Use Anchor framework for program development
                   - Implement CPI (Cross-Program Invocation) for composability
                   - Store AI model parameters on-chain or IPFS
                
                2. Off-chain Components:
                   - Run inference servers with Solana RPC connection
                   - Use WebSocket for real-time updates
                   - Implement MEV protection for trading
                
                3. Integration Pattern:
                   ```rust
                   // Anchor program for AI agent
                   #[program]
                   pub mod ai_agent {
                       use super::*;
                       
                       pub fn execute_ai_action(
                           ctx: Context<ExecuteAI>,
                           prediction: Vec<u8>
                       ) -> Result<()> {
                           // Verify AI prediction
                           // Execute on-chain action
                           Ok(())
                       }
                   }
                   ```
                
                4. Best Practices:
                   - Use PDAs for deterministic addresses
                   - Implement circuit breakers
                   - Add slippage protection
                   - Monitor for sandwich attacks
                """,
                "category": "solana_ai_development"
            },
            {
                "title": "Zero-Knowledge AI on Solana",
                "content": """
                Implementing ZK-AI proofs on Solana:
                
                1. ZK-SNARK Integration:
                   - Use Groth16 or PLONK proofs
                   - Verify AI computations without revealing data
                   - Reduce on-chain compute requirements
                
                2. Architecture:
                   - Off-chain: Generate ZK proofs for AI inference
                   - On-chain: Verify proofs and execute actions
                   
                3. Libraries:
                   - arkworks-rs for ZK circuits
                   - snarkVM for proof generation
                   - Light Protocol for privacy
                
                4. Example Use Cases:
                   - Private AI trading strategies
                   - Confidential credit scoring
                   - Anonymous AI predictions
                   - Secure model parameters
                
                5. Implementation:
                   ```rust
                   // Verify ZK proof on-chain
                   pub fn verify_ai_proof(
                       proof: Proof,
                       public_inputs: Vec<Fr>
                   ) -> bool {
                       // Verify the proof
                       groth16::verify(&vk, &proof, &public_inputs)
                   }
                   ```
                """,
                "category": "solana_zk_ai"
            },
            {
                "title": "Solana AI Trading Best Practices",
                "content": """
                Best practices for AI trading on Solana:
                
                1. Transaction Optimization:
                   - Use priority fees for time-sensitive trades
                   - Implement Jito bundles for MEV protection
                   - Monitor slot leader schedule
                
                2. Risk Management:
                   - Implement on-chain stop losses
                   - Use Serum DEX for limit orders
                   - Monitor liquidity depth
                
                3. AI Model Integration:
                   - Store model hashes on-chain
                   - Use Arweave for model storage
                   - Implement model versioning
                
                4. Security Considerations:
                   - Audit smart contracts
                   - Use multisig for upgrades
                   - Implement timelock mechanisms
                   - Monitor for exploits
                
                5. Performance Tips:
                   - Use lookup tables for addresses
                   - Batch transactions when possible
                   - Optimize account data layout
                   - Use rent-exempt accounts
                
                6. DeFi Integration:
                   - Jupiter for aggregated swaps
                   - Orca/Raydium for concentrated liquidity
                   - Marinade for liquid staking
                   - Kamino for leveraged strategies
                """,
                "category": "solana_ai_trading"
            },
            {
                "title": "Phantom Wallet AI Integration",
                "content": """
                Integrating AI features with Phantom wallet:
                
                1. Connection Setup:
                   ```javascript
                   const provider = window.solana;
                   if (provider?.isPhantom) {
                       const resp = await provider.connect();
                       const pubKey = resp.publicKey.toString();
                   }
                   ```
                
                2. Transaction Signing:
                   - Present AI analysis before signing
                   - Show risk scores and predictions
                   - Implement approval workflows
                
                3. Security Features:
                   - Transaction simulation
                   - Address verification
                   - Scam detection
                   - Amount validation
                
                4. UX Best Practices:
                   - Clear AI explanations
                   - Risk warnings
                   - Confirmation dialogs
                   - Transaction history
                """,
                "category": "phantom_integration"
            },
            {
                "title": "Solana Program Security for AI",
                "content": """
                Security considerations for AI programs on Solana:
                
                1. Input Validation:
                   - Validate all AI predictions
                   - Check parameter bounds
                   - Prevent overflow/underflow
                
                2. Access Control:
                   - Use PDA signers
                   - Implement role-based access
                   - Time-based restrictions
                
                3. Economic Security:
                   - Prevent flash loan attacks
                   - Add slippage protection
                   - Implement fee mechanisms
                
                4. Upgrade Security:
                   - Use upgradeable programs carefully
                   - Implement governance
                   - Add migration paths
                
                5. Common Vulnerabilities:
                   - Missing signer checks
                   - Arithmetic errors
                   - Reentrancy (less common)
                   - Oracle manipulation
                """,
                "category": "solana_security"
            }
        ]
        
        # Add Solana AI documents to knowledge base
        for doc_data in solana_docs:
            doc = KnowledgeDocument(
                id=hashlib.md5(doc_data["title"].encode()).hexdigest(),
                title=doc_data["title"],
                content=doc_data["content"],
                source="solana_ai_guide",
                category=doc_data["category"],
                timestamp=datetime.now(),
                metadata={"type": "documentation"}
            )
            
            await self.add_document(doc, collection="solana")
            
        # Add relationships to knowledge graph
        self._build_solana_knowledge_graph()
        
        logger.info("Initialized Solana AI knowledge base")
        
    def _build_solana_knowledge_graph(self):
        """Build knowledge graph relationships"""
        
        # Add nodes
        nodes = [
            ("Solana", {"type": "blockchain"}),
            ("AI Trading", {"type": "application"}),
            ("Zero-Knowledge", {"type": "technology"}),
            ("Phantom", {"type": "wallet"}),
            ("Jupiter", {"type": "dex_aggregator"}),
            ("Anchor", {"type": "framework"}),
            ("DeepSeek-R1", {"type": "ai_model"}),
            ("DGM", {"type": "algorithm"}),
            ("TradingAgents", {"type": "framework"})
        ]
        
        for node, attrs in nodes:
            self.knowledge_graph.add_node(node, **attrs)
            
        # Add relationships
        edges = [
            ("Solana", "AI Trading", {"relation": "enables"}),
            ("Solana", "Zero-Knowledge", {"relation": "supports"}),
            ("Phantom", "Solana", {"relation": "wallet_for"}),
            ("Jupiter", "Solana", {"relation": "built_on"}),
            ("Anchor", "Solana", {"relation": "framework_for"}),
            ("DeepSeek-R1", "AI Trading", {"relation": "powers"}),
            ("DGM", "AI Trading", {"relation": "optimizes"}),
            ("TradingAgents", "AI Trading", {"relation": "implements"}),
            ("Zero-Knowledge", "AI Trading", {"relation": "secures"})
        ]
        
        self.knowledge_graph.add_edges_from(edges)
        
    async def add_document(self, 
                         document: KnowledgeDocument,
                         collection: str = "trading") -> str:
        """Add document to knowledge base"""
        
        # Generate embedding
        if document.embedding is None:
            document.embedding = self.embedding_gen.generate_embedding(
                f"{document.title}\n{document.content}"
            )
            
        # Choose collection
        if collection == "solana":
            target_collection = self.solana_collection
        else:
            target_collection = self.trading_collection
            
        # Add to Chroma
        target_collection.add(
            embeddings=[document.embedding.tolist()],
            documents=[document.content],
            metadatas=[{
                "title": document.title,
                "source": document.source,
                "category": document.category,
                "timestamp": document.timestamp.isoformat()
            }],
            ids=[document.id]
        )
        
        # Add to document store
        self.document_store[document.id] = document
        
        # Update FAISS index
        self._update_faiss_index()
        
        logger.info(f"Added document: {document.title}")
        
        return document.id
        
    async def search(self, 
                    query: str,
                    collection: str = "all",
                    top_k: int = 5) -> List[Tuple[KnowledgeDocument, float]]:
        """Search knowledge base"""
        
        # Generate query embedding
        query_embedding = self.embedding_gen.generate_embedding(query)
        
        results = []
        
        # Search in Chroma
        if collection in ["all", "trading"]:
            trading_results = self.trading_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            results.extend(self._process_chroma_results(trading_results))
            
        if collection in ["all", "solana"]:
            solana_results = self.solana_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            results.extend(self._process_chroma_results(solana_results))
            
        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
        
    def _process_chroma_results(self, 
                              results: Dict[str, Any]) -> List[Tuple[KnowledgeDocument, float]]:
        """Process Chroma search results"""
        
        processed = []
        
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                if doc_id in self.document_store:
                    doc = self.document_store[doc_id]
                    distance = results["distances"][0][i] if results["distances"] else 0
                    relevance = 1 / (1 + distance)  # Convert distance to relevance
                    processed.append((doc, relevance))
                    
        return processed
        
    async def get_trading_insights(self, context: Dict[str, Any]) -> List[str]:
        """Get relevant trading insights based on context"""
        
        insights = []
        
        # Search for relevant documents
        query_parts = []
        
        if "token" in context:
            query_parts.append(f"{context['token']} trading")
            
        if "strategy" in context:
            query_parts.append(f"{context['strategy']} strategy")
            
        if "market_condition" in context:
            query_parts.append(f"{context['market_condition']} market")
            
        query = " ".join(query_parts) + " Solana AI"
        
        results = await self.search(query, collection="all", top_k=3)
        
        for doc, relevance in results:
            if relevance > 0.7:  # High relevance threshold
                insights.append(f"{doc.title}: {doc.content[:200]}...")
                
        # Add graph-based insights
        graph_insights = self._get_graph_insights(context)
        insights.extend(graph_insights)
        
        return insights
        
    def _get_graph_insights(self, context: Dict[str, Any]) -> List[str]:
        """Get insights from knowledge graph"""
        
        insights = []
        
        # Find relevant paths in graph
        if "token" in context and context["token"] == "SOL":
            # Get Solana-related insights
            neighbors = list(self.knowledge_graph.neighbors("Solana"))
            
            for neighbor in neighbors:
                edge_data = self.knowledge_graph.get_edge_data("Solana", neighbor)
                relation = edge_data.get("relation", "related to")
                insights.append(f"Solana {relation} {neighbor}")
                
        return insights
        
    def _update_faiss_index(self):
        """Update FAISS index with all documents"""
        
        if not self.document_store:
            return
            
        # Get all embeddings
        embeddings = []
        doc_ids = []
        
        for doc_id, doc in self.document_store.items():
            if doc.embedding is not None:
                embeddings.append(doc.embedding)
                doc_ids.append(doc_id)
                
        if embeddings:
            embeddings_matrix = np.array(embeddings).astype('float32')
            
            # Create or update index
            if self.faiss_index is None:
                self.faiss_index = faiss.IndexFlatL2(self.dimension)
                
            self.faiss_index.reset()
            self.faiss_index.add(embeddings_matrix)
            
            # Save mapping
            self.doc_id_mapping = doc_ids
            
    def _save_index(self):
        """Save FAISS index and document store"""
        
        # Save FAISS index
        if self.faiss_index is not None:
            faiss.write_index(
                self.faiss_index, 
                str(self.data_path / "faiss.index")
            )
            
        # Save document store
        with open(self.data_path / "documents.pkl", 'wb') as f:
            pickle.dump(self.document_store, f)
            
        # Save knowledge graph
        nx.write_gpickle(
            self.knowledge_graph,
            str(self.data_path / "knowledge_graph.pkl")
        )
        
        logger.info("Saved knowledge base index")
        
    def _load_index(self):
        """Load existing index if available"""
        
        faiss_path = self.data_path / "faiss.index"
        docs_path = self.data_path / "documents.pkl"
        graph_path = self.data_path / "knowledge_graph.pkl"
        
        if faiss_path.exists():
            self.faiss_index = faiss.read_index(str(faiss_path))
            logger.info("Loaded FAISS index")
            
        if docs_path.exists():
            with open(docs_path, 'rb') as f:
                self.document_store = pickle.load(f)
            logger.info(f"Loaded {len(self.document_store)} documents")
            
        if graph_path.exists():
            self.knowledge_graph = nx.read_gpickle(str(graph_path))
            logger.info("Loaded knowledge graph")


async def main():
    """Test knowledge base system"""
    
    kb = KnowledgeBaseSystem()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Test search
    results = await kb.search("Solana AI trading strategies", collection="all")
    
    print("\nSearch Results for 'Solana AI trading strategies':")
    print("="*60)
    
    for doc, relevance in results:
        print(f"\nTitle: {doc.title}")
        print(f"Relevance: {relevance:.2f}")
        print(f"Category: {doc.category}")
        print(f"Preview: {doc.content[:150]}...")
        
    # Test insights
    insights = await kb.get_trading_insights({
        "token": "SOL",
        "strategy": "AI",
        "market_condition": "volatile"
    })
    
    print("\n\nTrading Insights:")
    print("="*60)
    
    for insight in insights:
        print(f"- {insight}")


if __name__ == "__main__":
    asyncio.run(main())