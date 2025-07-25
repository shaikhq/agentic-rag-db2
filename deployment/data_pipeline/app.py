from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import sys
import os
import logging

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.simple_db import SimpleDB
from shared.config import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Data Pipeline API")

# Use shared database
from shared.db_manager import get_shared_db
db = get_shared_db()

class IngestRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {
        "service": "Data Pipeline API",
        "status": "running",
        "database_stats": db.get_stats()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "database": db.health_check(),
        "stats": db.get_stats()
    }

@app.post("/ingest")
def ingest_url(request: IngestRequest):
    """Simple URL ingestion"""
    try:
        logger.info(f"Ingesting URL: {request.url}")
        
        # Download webpage
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(request.url, timeout=10, headers=headers)
        response.raise_for_status()
        
        # Parse content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Extract main content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content size
        content = f"{title_text}\n\n{text[:2000]}"
        
        # Store in database
        doc_id = f"doc_{len(db.data) + 1}"
        db.add_document(doc_id, content, request.url)
        
        return {
            "success": True,
            "message": f"Successfully ingested document from {request.url}",
            "doc_id": doc_id,
            "title": title_text,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "total_documents": len(db.data)
        }
        
    except Exception as e:
        logger.error(f"Failed to ingest {request.url}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/documents")
def list_documents():
    """List all ingested documents"""
    return {
        "total": len(db.data),
        "documents": [
            {
                "id": doc["id"],
                "source": doc["source"],
                "preview": doc["content"][:100] + "..." if len(doc["content"]) > 100 else doc["content"]
            }
            for doc in db.data
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)