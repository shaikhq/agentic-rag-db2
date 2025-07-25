import logging
import os
from typing import List, Dict, Any, Optional
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_db2 import DB2VS
# Try to import DistanceStrategy, fallback if not available
try:
    from langchain_db2.db2vs import DistanceStrategy
except ImportError:
    try:
        from langchain_db2 import DistanceStrategy
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning("DistanceStrategy not found, will use default")
        DistanceStrategy = None

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Try different imports for create_retriever_tool
try:
    from langchain_community.tools import create_retriever_tool
except ImportError:
    try:
        from langchain.tools.retriever import create_retriever_tool
    except ImportError:
        try:
            from langchain_core.tools import create_retriever_tool
        except ImportError:
            # Create a simple retriever tool manually
            def create_retriever_tool(retriever, name, description):
                """Simple retriever tool implementation"""
                def retriever_tool_func(query: str):
                    """Retrieve documents for the given query"""
                    try:
                        docs = retriever.get_relevant_documents(query)
                        return "\n\n".join([doc.page_content for doc in docs])
                    except Exception as e:
                        return f"Error retrieving documents: {str(e)}"
                
                # Create a simple tool-like object
                class SimpleRetrieverTool:
                    def __init__(self, func, name, description):
                        self.func = func
                        self.name = name
                        self.description = description
                    
                    def invoke(self, args):
                        if isinstance(args, dict):
                            query = args.get('query', '')
                        else:
                            query = str(args)
                        return self.func(query)
                    
                    def __call__(self, query):
                        return self.func(query)
                
                return SimpleRetrieverTool(retriever_tool_func, name, description)

import ibm_db
from .config import config

logger = logging.getLogger(__name__)

class GraniteDB2Store:
    """DB2 + Granite store with graceful fallback"""
    
    def __init__(self):
        # Initialize LlamaCpp embeddings (this worked!)
        self.embeddings = LlamaCppEmbeddings(
            model_path=config.GRANITE_MODEL_PATH
        )
        logger.info("✅ Granite embeddings model loaded successfully")
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # DB2 connection and vectorstore
        self.connection = None
        self.vectorstore = None
        self.retriever = None
        self.retriever_tool = None
        self.db2_available = False
        
        # Simple fallback storage
        self.simple_storage = []
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize DB2 connection with graceful fallback"""
        try:
            # Create DB2 connection string
            connection_string = config.get_db2_connection_string()
            logger.info(f"Attempting to connect to DB2: {config.DB2_HOST}:{config.DB2_PORT}")
            
            # Connect to DB2
            self.connection = ibm_db.connect(connection_string, "", "")
            self.db2_available = True
            logger.info("✅ Successfully connected to IBM DB2")
            
        except Exception as e:
            logger.warning(f"⚠️  DB2 connection failed: {e}")
            logger.warning("🔄 Falling back to simple in-memory storage for development")
            self.db2_available = False
            # Continue without DB2 for development
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Process documents with DB2 or fallback storage"""
        try:
            # Convert documents to chunks
            chunks = []
            
            for doc in documents:
                text_chunks = self.text_splitter.split_text(doc['content'])
                for i, chunk_text in enumerate(text_chunks):
                    chunk = {
                        'id': f"{doc['id']}_chunk_{i}",
                        'content': chunk_text,
                        'source': doc['source'],
                        'metadata': doc.get('metadata', {})
                    }
                    chunks.append(chunk)
            
            logger.info(f"Created {len(chunks)} text chunks")
            
            if self.db2_available and self.connection:
                # Use DB2 vectorstore
                try:
                    chunk_texts = [chunk['content'] for chunk in chunks]
                    
                    if DistanceStrategy:
                        self.vectorstore = DB2VS.from_texts(
                            chunk_texts,
                            self.embeddings,
                            client=self.connection,
                            table_name="Documents_EUCLIDEAN",
                            distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
                        )
                    else:
                        self.vectorstore = DB2VS.from_texts(
                            chunk_texts,
                            self.embeddings,
                            client=self.connection,
                            table_name="Documents_EUCLIDEAN",
                        )
                    
                    self.retriever = self.vectorstore.as_retriever()
                    self.retriever_tool = create_retriever_tool(
                        self.retriever,
                        "retrieve_blog_posts",
                        "Search and return information about Shaikh's ML blog posts.",
                    )
                    
                    logger.info("✅ Added documents to DB2 vectorstore")
                    
                except Exception as e:
                    logger.error(f"DB2 vectorstore creation failed: {e}")
                    # Fall back to simple storage
                    self._fallback_to_simple_storage(chunks)
            else:
                # Use simple storage
                self._fallback_to_simple_storage(chunks)
            
            return [chunk['id'] for chunk in chunks]
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def _fallback_to_simple_storage(self, chunks):
        """Fallback to simple in-memory storage"""
        self.simple_storage.extend(chunks)
        logger.info(f"✅ Added {len(chunks)} chunks to simple storage (fallback mode)")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search using DB2 or simple storage"""
        try:
            if self.vectorstore:
                # Use DB2 vectorstore
                results = self.vectorstore.similarity_search(query, k=k)
                formatted_results = []
                for i, doc in enumerate(results):
                    formatted_results.append({
                        'id': f'result_{i}',
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'source': doc.metadata.get('source', 'unknown')
                    })
                logger.info(f"🔍 DB2 search found {len(formatted_results)} results")
                return formatted_results
            else:
                # Use simple text search
                results = []
                query_lower = query.lower()
                
                for chunk in self.simple_storage:
                    if query_lower in chunk['content'].lower():
                        results.append(chunk)
                        if len(results) >= k:
                            break
                
                logger.info(f"🔍 Simple search found {len(results)} results")
                return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_retriever_tool(self):
        """Get retriever tool or create simple fallback"""
        if self.retriever_tool:
            return self.retriever_tool
        
        # Create simple retriever tool for fallback
        def simple_retrieve(query: str):
            results = self.similarity_search(query, k=3)
            if results:
                return "\n\n".join([result['content'] for result in results])
            return "No relevant documents found."
        
        class SimpleRetrieverTool:
            def __init__(self, func):
                self.func = func
                self.name = "retrieve_blog_posts"
                self.description = "Search and return information about Shaikh's ML blog posts."
            
            def invoke(self, args):
                if isinstance(args, dict):
                    query = args.get('query', '')
                else:
                    query = str(args)
                return self.func(query)
        
        logger.info("📋 Created simple retriever tool (fallback mode)")
        return SimpleRetrieverTool(simple_retrieve)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats"""
        return {
            "embeddings_model": "granite-embedding-30m-english-Q6_K.gguf",
            "embeddings_loaded": True,
            "db2_available": self.db2_available,
            "vectorstore_type": "DB2VS" if self.db2_available else "SimpleStorage",
            "storage_mode": "DB2" if self.vectorstore else "Simple",
            "total_chunks": len(self.simple_storage),
            "retriever_ready": self.get_retriever_tool() is not None,
        }
    
    def health_check(self) -> bool:
        """Health check focusing on what's working"""
        try:
            # Test embeddings (this is working)
            test_embedding = self.embeddings.embed_query("test query")
            embeddings_ok = len(test_embedding) > 0
            
            logger.info(f"Health: Embeddings={embeddings_ok}, DB2={self.db2_available}")
            return embeddings_ok  # Service is healthy if embeddings work
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Singleton instance
_granite_store = None

def get_granite_db2_store() -> GraniteDB2Store:
    """Get the singleton store instance"""
    global _granite_store
    if _granite_store is None:
        _granite_store = GraniteDB2Store()
    return _granite_store