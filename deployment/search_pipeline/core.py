import logging
import sys
import os
from typing import List, Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.simple_db import SimpleDB

logger = logging.getLogger(__name__)

class SimpleSearchCore:
    """Simple search system without embeddings for now"""
    
    def __init__(self, database: SimpleDB):
        self.db = database
        logger.info("Simple search core initialized")
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search documents and generate simple response"""
        try:
            logger.info(f"Searching for: {query}")
            
            # Get relevant documents
            docs = self.db.search(query)[:max_results]
            
            if not docs:
                return {
                    "answer": f"I couldn't find any documents related to '{query}'. Please make sure relevant documents have been ingested first.",
                    "sources": [],
                    "query": query,
                    "status": "no_results"
                }
            
            # Generate simple response
            answer = self._generate_response(query, docs)
            
            # Prepare sources
            sources = [
                {
                    "doc_id": doc["id"],
                    "source": doc["source"],
                    "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                }
                for doc in docs
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "answer": "I encountered an error while processing your query.",
                "sources": [],
                "query": query,
                "status": "error",
                "error": str(e)
            }
    
    def _generate_response(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """Generate a simple response based on found documents"""
        
        response_parts = [
            f"Based on {len(docs)} document(s) I found, here's what I can tell you about '{query}':\n"
        ]
        
        for i, doc in enumerate(docs[:3], 1):  # Use top 3 documents
            content = doc["content"]
            # Extract relevant snippet around the query
            snippet = self._extract_snippet(content, query)
            response_parts.append(f"{i}. From {doc['source']}: {snippet}")
        
        if len(docs) > 3:
            response_parts.append(f"\n(Found {len(docs)} total documents related to your query)")
        
        return "\n\n".join(response_parts)
    
    def _extract_snippet(self, content: str, query: str, snippet_length: int = 200) -> str:
        """Extract relevant snippet from content around query terms"""
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Find where query appears in content
        query_words = query_lower.split()
        best_start = 0
        best_score = 0
        
        # Simple scoring: find position with most query words nearby
        for i in range(0, len(content), 50):
            window = content_lower[i:i+snippet_length]
            score = sum(1 for word in query_words if word in window)
            if score > best_score:
                best_score = score
                best_start = i
        
        # Extract snippet
        snippet = content[best_start:best_start+snippet_length]
        if best_start > 0:
            snippet = "..." + snippet
        if best_start + snippet_length < len(content):
            snippet = snippet + "..."
            
        return snippet.strip()
    
    def health_check(self) -> Dict[str, Any]:
        """Check search system health"""
        return {
            "database": self.db.health_check(),
            "search_core": True,
            "total_documents": len(self.db.data)
        }