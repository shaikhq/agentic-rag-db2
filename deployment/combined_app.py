from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from shared.granite_db2_store import get_granite_db2_store
from shared.langgraph_workflow import create_agentic_workflow
from shared.config import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic RAG with Granite + DB2")

# Initialize store
db2_store = get_granite_db2_store()
agentic_workflow = None

# Models
class IngestRequest(BaseModel):
    url: str

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 4

# INGESTION ENDPOINTS
@app.post("/ingest")
def ingest_url(request: IngestRequest):
    """Ingest documents using Granite embeddings"""
    global agentic_workflow
    
    try:
        logger.info(f"Ingesting URL: {request.url}")
        
        # Download and parse
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(request.url, timeout=10, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Clean content
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        content = f"{title_text}\n\n{text[:3000]}"
        
        # Create document
        doc = {
            'id': f"doc_{abs(hash(request.url)) % 10000}",
            'content': content,
            'source': request.url,
            'title': title_text,
            'metadata': {'url': request.url, 'title': title_text}
        }
        
        # Add to store (DB2 or simple storage)
        doc_ids = db2_store.add_documents([doc])
        
        # Initialize agentic workflow after first document
        if agentic_workflow is None:
            retriever_tool = db2_store.get_retriever_tool()
            if retriever_tool:
                agentic_workflow = create_agentic_workflow(retriever_tool)
                logger.info("✅ Agentic workflow initialized")
        
        return {
            "success": True,
            "message": f"Successfully ingested document from {request.url}",
            "doc_id": doc['id'],
            "title": title_text,
            "chunks_created": len(doc_ids),
            "storage_mode": "DB2" if db2_store.db2_available else "Simple",
            "agentic_workflow_ready": agentic_workflow is not None,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# SEARCH ENDPOINTS
@app.post("/search")
def search_documents(request: SearchRequest):
    """Search using agentic RAG workflow"""
    try:
        if not agentic_workflow:
            return {
                "answer": "Please ingest at least one document first to initialize the agentic workflow.",
                "query": request.query,
                "status": "not_ready",
                "timestamp": datetime.now()
            }
        
        logger.info(f"Processing agentic search: {request.query}")
        
        # Use the agentic workflow
        result = agentic_workflow.invoke(request.query)
        
        return {
            "answer": result["answer"],
            "query": request.query,
            "status": result["status"],
            "storage_mode": "DB2" if db2_store.db2_available else "Simple",
            "workflow_messages": result.get("messages", []),
            "timestamp": datetime.now(),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Agentic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
def get_system_stats():
    """Get complete system statistics"""
    return {
        "granite_embeddings": "✅ Loaded successfully",
        "storage_stats": db2_store.get_stats(),
        "agentic_workflow_ready": agentic_workflow is not None,
        "health": db2_store.health_check()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy" if db2_store.health_check() else "unhealthy",
        "components": db2_store.get_stats(),
        "timestamp": datetime.now()
    }

@app.get("/")
def root():
    return {
        "service": "Agentic RAG with Granite Embeddings",
        "description": "Production deployment with Granite embeddings and flexible storage",
        "status": {
            "granite_embeddings": "✅ Working",
            "storage_mode": "DB2" if db2_store.db2_available else "Simple (fallback)",
            "agentic_workflow": "✅ Ready" if agentic_workflow else "Waiting for first document"
        },
        "endpoints": {
            "POST /ingest": "Ingest documents",
            "POST /search": "Agentic RAG search",
            "GET /stats": "System statistics",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000, reload=True)