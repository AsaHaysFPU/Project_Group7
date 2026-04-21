"""RAG Pipeline for Medical Dosage Knowledge Retrieval"""
import os
from typing import List, Dict
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    from langchain.embeddings import GoogleGenerativeAIEmbeddings

from langchain_chroma import Chroma
try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document

import logging

logger = logging.getLogger(__name__)


class MedicalRAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for medical dosage knowledge.
    Integrates ChromaDB for vector storage and retrieval.
    """
    
    def __init__(self, embedding_model: str = "models/embedding-001", persist_dir: str = "data/chroma_db"):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Google Generative AI embedding model
            persist_dir: Directory to persist ChromaDB
        """
        self.embedding_model = embedding_model
        self.persist_dir = persist_dir
        self.fallback_documents: List[Dict] = []
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize embeddings
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
            logger.info("Embeddings initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize embeddings: {e}. Using mock embeddings.")
            self.embeddings = None
        
        # Initialize vector store
        self.vector_store = None
        self._load_or_create_vector_store()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one"""
        try:
            if self.embeddings:
                self.vector_store = Chroma(
                    collection_name="medical_dosage_kb",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_dir
                )
                logger.info(f"Vector store loaded from {self.persist_dir}")
            else:
                logger.warning("Embeddings not available - vector store not initialized")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            self.vector_store = None
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of dicts with 'title' and 'content' keys
        """
        # Always keep a local fallback corpus so retrieval works without external API keys.
        self.fallback_documents.extend(documents)

        if not self.embeddings or not self.vector_store:
            logger.warning("Embeddings/vector store unavailable; using local fallback corpus only")
            return
        
        texts = []
        metadatas = []
        
        for doc in documents:
            # Split document into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_text(doc.get("content", ""))
            
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    "title": doc.get("title", "Unknown"),
                    "source": doc.get("source", "Unknown")
                })
        
        if texts:
            self.vector_store.add_texts(texts, metadatas=metadatas)
            self.vector_store.persist()
            logger.info(f"Added {len(texts)} text chunks to vector store")
    
    def retrieve(self, query: str, k: int = 4) -> List[Dict]:
        """
        Retrieve relevant documents from knowledge base.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized - using local fallback retrieval")
            return self._retrieve_fallback(query, k)
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            retrieved = []
            for doc, score in results:
                retrieved.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            return retrieved
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return self._retrieve_fallback(query, k)

    def _retrieve_fallback(self, query: str, k: int = 4) -> List[Dict]:
        """Simple keyword scoring fallback when embeddings/vector store are unavailable."""
        if not query.strip() or not self.fallback_documents:
            return []

        query_terms = [term for term in query.lower().split() if term]
        scored = []

        for doc in self.fallback_documents:
            content = doc.get("content", "")
            title = doc.get("title", "Unknown")
            source = doc.get("source", "Unknown")
            haystack = f"{title} {content}".lower()
            score = sum(haystack.count(term) for term in query_terms)
            if score > 0:
                scored.append(
                    {
                        "content": content.strip(),
                        "metadata": {"title": title, "source": source},
                        "relevance_score": float(score),
                    }
                )

        scored.sort(key=lambda item: item["relevance_score"], reverse=True)
        return scored[:k]
    
    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base"""
        if self.vector_store:
            try:
                # Delete and recreate collection
                self.vector_store._collection.delete()
                logger.info("Knowledge base cleared")
            except Exception as e:
                logger.error(f"Error clearing knowledge base: {e}")


# Mock medical knowledge base
MEDICAL_KNOWLEDGE_BASE = [
    {
        "title": "Acetaminophen (Tylenol) Dosing Guidelines",
        "source": "FDA Guidelines",
        "content": """
        Acetaminophen dosing for adults and children:
        - Adults and children over 12 years: 325-650 mg every 4-6 hours, not to exceed 3000 mg/day
        - Children 6-12 years: 325 mg every 4-6 hours, not to exceed 1300 mg/day
        - Weight-based dosing: 10-15 mg/kg per dose, maximum 5 doses per day
        - Maximum daily dose is lower in elderly patients with liver disease
        Overdose risk: Taking more than 4000 mg in 24 hours increases risk of liver toxicity
        """
    },
    {
        "title": "Amoxicillin Pediatric Dosing",
        "source": "AAP Clinical Guidelines",
        "content": """
        Amoxicillin dosing for pediatric infections:
        - Standard dose: 25-45 mg/kg/day divided into three doses
        - For severe infections: up to 90 mg/kg/day divided into three doses
        - Infants under 3 months: 30 mg/kg/day divided into two doses
        - Maximum single dose: 500 mg
        - Renal impairment: Adjust dosing based on creatinine clearance
        - Penicillin allergy: Contraindicated
        """
    },
    {
        "title": "Ibuprofen Anti-inflammatory Dosing",
        "source": "Clinical Pharmacology",
        "content": """
        Ibuprofen dosing for pain and inflammation:
        - Adult dose: 200-400 mg every 4-6 hours, maximum 1200 mg/day OTC, 3200 mg/day prescription
        - Pediatric dose: 10 mg/kg every 6-8 hours (not to exceed 40 mg/kg/day or 2400 mg/day)
        - For fever: Dosing every 6-8 hours as needed
        - With food to reduce GI upset
        - Monitor renal function in elderly patients
        """
    },
    {
        "title": "Drug Interaction Safety Guidelines",
        "source": "Micromedex",
        "content": """
        Critical drug interaction considerations:
        - Avoid combining ibuprofen with other NSAIDs
        - Do not exceed acetaminophen + ibuprofen combination dosing
        - Monitor drug interactions with anticoagulants
        - Adjust dosing for patients on dialysis
        - Consider hepatic and renal impairment in elderly patients
        - Always check current FDA warnings and black box warnings
        """
    }
]
