from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import sys
import os
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search_pipeline.core import SimpleSearchCore
from shared.simple_db import SimpleDB
from shared.config import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Pipeline API")

# Use shared database
from shared.db_manager import get_shared_db
db = get_shared_db()

search_core = SimpleSearchCore(db)

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class SearchResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    status: str
    timestamp: datetime
    error: Optional[str] = None

@app.get("/")
def root():
    return {
        "service": "Search Pipeline API",
        "status": "running",
        "database_stats": db.get_stats()
    }

@app.get("/health")
def health():
    health_status = search_core.health_check()
    return {
        "status": "healthy" if all(health_status.values()) else "degraded",
        "components": health_status,
        "timestamp": datetime.now()
    }

@app.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    """Search for information in ingested documents"""
    try:
        logger.info(f"Processing search request: {request.query}")
        
        # Perform search
        result = search_core.search(request.query, request.max_results)
        
        response = SearchResponse(
            answer=result["answer"],
            sources=result["sources"],
            query=result["query"],
            status=result["status"],
            timestamp=datetime.now(),
            error=result.get("error")
        )
        
        logger.info("Search request completed")
        return response
        
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/debug")
def debug_info():
    """Debug endpoint to see database contents"""
    return {
        "total_documents": len(db.data),
        "documents": [
            {
                "id": doc["id"],
                "source": doc["source"],
                "content_length": len(doc["content"]),
                "content_preview": doc["content"][:100]
            }
            for doc in db.data
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)