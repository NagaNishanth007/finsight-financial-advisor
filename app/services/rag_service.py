import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RAGService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        settings = get_settings()
        
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="financial_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Embedding model
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # Seed with basic financial knowledge if empty
            if self.collection.count() == 0:
                self._seed_knowledge()
            
            logger.info(f"RAG service loaded with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self.client = None
            self.collection = None
        
        self._initialized = True
    
    def _seed_knowledge(self):
        """Seed initial financial knowledge"""
        knowledge_base = [
            {
                "id": "emergency_fund_1",
                "text": "An emergency fund should cover 3-6 months of expenses. Start small with $500-1000, then build up. Keep it in a high-yield savings account for easy access.",
                "category": "saving",
                "topic": "emergency_fund"
            },
            {
                "id": "investing_fear_1",
                "text": "Market volatility is normal. Dollar-cost averaging (investing regular amounts consistently) reduces risk. Start with low-cost index funds. Time in the market beats timing the market.",
                "category": "investing",
                "topic": "fear_management"
            },
            {
                "id": "rent_vs_invest_1",
                "text": "Pay rent first - it's a necessity and late fees affect credit. With remaining money, consider: 1) Small emergency buffer, 2) High-interest debt, 3) Investment with money you won't need soon.",
                "category": "budgeting",
                "topic": "conflict_resolution"
            },
            {
                "id": "50k_advice_1",
                "text": "With a $50k lump sum: 1) Build 3-month emergency fund, 2) Pay off high-interest debt (>7%), 3) Consider maxing tax-advantaged accounts (401k, IRA), 4) Diversify remaining across index funds, bonds based on risk tolerance.",
                "category": "financial_planning",
                "topic": "windfall"
            },
            {
                "id": "credit_debt_1",
                "text": "Credit card debt should be prioritized (avg 20% APR). Pay minimums on all cards, then put extra toward highest APR card (avalanche method) or smallest balance (snowball for motivation).",
                "category": "debt",
                "topic": "credit_cards"
            },
            {
                "id": "student_loans_1",
                "text": "Student loans: Federal loans have options like income-driven repayment, deferment. Private loans are less flexible. Interest rates typically 4-8%. Don't rush payoff if rate is low and you need liquidity.",
                "category": "debt",
                "topic": "student_loans"
            },
            {
                "id": "emotional_1",
                "text": "Financial anxiety is common. Small steps matter more than perfect plans. Starting with $50/month invested is better than waiting until you feel 'ready'. Progress, not perfection.",
                "category": "emotional_support",
                "topic": "anxiety"
            },
            {
                "id": "budget_50_30_20",
                "text": "50/30/20 rule: 50% needs (rent, food, bills), 30% wants, 20% savings/debt. Adjust based on your situation - high cost of living areas might need 60/20/20.",
                "category": "budgeting",
                "topic": "rule_of_thumb"
            },
            {
                "id": "fomo_investing",
                "text": "Fear of missing out leads to bad decisions. If everyone is talking about an investment (crypto, meme stocks), the easy gains are likely gone. Stick to diversified, boring strategies for wealth building.",
                "category": "investing",
                "topic": "behavioral"
            },
            {
                "id": "first_invest_steps",
                "text": "First-time investing steps: 1) Employer 401k match (free money), 2) Roth IRA for tax-free growth, 3) Low-cost total market index funds (VTI, VOO), 4) Target-date funds for hands-off approach.",
                "category": "investing",
                "topic": "beginners"
            }
        ]
        
        self.add_documents(knowledge_base)
        logger.info(f"Seeded {len(knowledge_base)} knowledge documents")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base"""
        if self.collection is None:
            return
        
        texts = [doc["text"] for doc in documents]
        ids = [doc["id"] for doc in documents]
        metadatas = [{k: v for k, v in doc.items() if k not in ["id", "text"]} for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query the knowledge base"""
        if self.collection is None:
            return []
        
        try:
            query_embedding = self.embedding_model.encode([query_text]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return []


rag_service = RAGService()
