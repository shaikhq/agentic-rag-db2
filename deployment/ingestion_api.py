import os
import sys
from pathlib import Path

# Add parent directory to path to import from main project
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import trafilatura
import spacy
import ibm_db_dbi  # Correct import
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_db2.db2vs import DB2VS

import logging
import traceback

# Add at the top of your file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from deployment directory
load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="Document Ingestion API", version="1.0.0")

class IngestRequest(BaseModel):
    url: HttpUrl
    table_name: str = "Documents_EUCLIDEAN"
    max_words: int = 200
    overlap_words: int = 50

class IngestResponse(BaseModel):
    success: bool
    message: str
    chunks_created: int = 0

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise HTTPException(status_code=500, detail="spaCy model not found. Run: python -m spacy download en_core_web_sm")

def get_db_connection():
    """Establish database connection using ibm_db_dbi"""
    conn_str = f"DATABASE={os.getenv('DB_NAME')};hostname={os.getenv('DB_HOST')};port={os.getenv('DB_PORT')};protocol={os.getenv('DB_PROTOCOL')};uid={os.getenv('DB_USER')};pwd={os.getenv('DB_PASSWORD')}"
    
    try:
        # This returns a DB-API 2.0 compatible connection with .cursor() method
        return ibm_db_dbi.connect(conn_str, '', '')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def get_embeddings():
    """Initialize LlamaCpp embeddings"""
    try:
        # Look for model in parent directory or deployment directory
        model_paths = [
            Path(__file__).parent.parent / "granite-embedding-30m-english-Q6_K.gguf",
            Path(__file__).parent / "granite-embedding-30m-english-Q6_K.gguf"
        ]
        
        model_path = None
        for path in model_paths:
            if path.exists():
                model_path = str(path)
                break
        
        if not model_path:
            raise FileNotFoundError("Embedding model file not found")
            
        return LlamaCppEmbeddings(model_path=model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize embeddings: {str(e)}")

def overlapping_sentence_chunker(text, max_words=200, overlap_words=50):
    """Chunk text into overlapping sentences"""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    chunks = []
    current_chunk = []
    current_length = 0

    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        sentence_length = len(sentence.split())

        if current_length + sentence_length <= max_words:
            current_chunk.append(sentence)
            current_length += sentence_length
            i += 1
        else:
            chunks.append(" ".join(current_chunk))
            overlap = []
            overlap_len = 0
            j = len(current_chunk) - 1
            while j >= 0 and overlap_len < overlap_words:
                s = current_chunk[j]
                overlap.insert(0, s)
                overlap_len += len(s.split())
                j -= 1
            current_chunk = overlap
            current_length = overlap_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest a document from URL into the vector store"""
    try:
        # Fetch and extract content
        downloaded = trafilatura.fetch_url(str(request.url))
        if not downloaded:
            raise HTTPException(status_code=400, detail="Failed to fetch content from URL")
        
        article = trafilatura.extract(downloaded)
        if not article:
            raise HTTPException(status_code=400, detail="Failed to extract text from URL")
        
        # Chunk the text
        chunks = overlapping_sentence_chunker(article, request.max_words, request.overlap_words)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from the document")
        
        # Get database connection and embeddings
        connection = get_db_connection()
        embeddings = get_embeddings()
        
        # Check if table exists
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM SYSCAT.TABLES 
            WHERE TABNAME = ? AND TABSCHEMA = CURRENT SCHEMA
        """, (request.table_name.upper(),))
        table_exists = cursor.fetchone()[0] > 0
        cursor.close()
        
        if table_exists:
            # Table exists - use add_texts()
            vectorstore = DB2VS(
                client=connection, 
                table_name=request.table_name,
                embedding_function=embeddings  # ✅ CORRECT parameter name
            )
            vectorstore.add_texts(texts=chunks)
            message = f"Added {len(chunks)} chunks to existing table '{request.table_name}'"
            
        else:
            # Table doesn't exist - use from_texts()
            vectorstore = DB2VS.from_texts(
                texts=chunks,
                embedding=embeddings,
                client=connection,
                table_name=request.table_name,
                distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
            )
            message = f"Created table '{request.table_name}' with {len(chunks)} chunks"
        
        connection.close()
        
        return IngestResponse(
            success=True,
            message=message,
            chunks_created=len(chunks)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Document Ingestion API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)