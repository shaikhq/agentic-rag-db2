# Agentic RAG with IBM Db2

This repository demonstrates how to build an **agentic Retrieval-Augmented Generation (RAG)** workflow using IBM Db2 and the `langchain-db2` connector. The project begins with a prototype in a Jupyter notebook and evolves into a production-ready implementation with a unified API service.

## Project Structure

```
agentic-rag-db2/
├── prototype/
├── ingestion-api/
├── search-api/
├── gateway-api/
├── models/
├── README.md
└── .env
```

### `prototype/`

A single-notebook prototype that implements the full agentic RAG pipeline:

* Loads and chunks documents
* Embeds them using a local LLM (`llama.cpp`)
* Stores vectors in Db2 using `langchain-db2`
* Performs semantic retrieval
* Uses LangGraph to rewrite queries and guide agent decisions

This is intended as a reference implementation to experiment with the overall workflow end-to-end.

### `ingestion-api/`

Core module that handles document ingestion and vector storage. Features include:

* Web document extraction from URLs using Trafilatura
* Intelligent text chunking with sentence-aware splitting
* Local embedding generation using Granite models
* Vector storage in Db2's vector database
* Table management (create, clear, validate)
* Health monitoring and error handling

### `search-api/`

Core module that provides intelligent question-answering using Agentic RAG. This module implements a multi-step reasoning workflow orchestrated by LangGraph:

* Semantic document retrieval from Db2 vector database
* Document relevance grading using IBM Watsonx
* Automatic query rewriting for improved results
* Context-aware answer generation
* Fallback mechanisms for robust operation

### `gateway-api/`

The main API service that provides a unified interface for the complete RAG pipeline:

* Single startup command for complete RAG functionality
* Embedded ingestion and search capabilities
* Unified API endpoints for all operations
* Simplified deployment and development workflow
* Production-ready with proper error handling

**Port:** 8000  
Refer to `gateway-api/README.md` for setup instructions and API usage.

### `models/`

Shared directory containing local AI models:

* **Granite Embedding Model**: `granite-embedding-30m-english-Q6_K.gguf` for semantic search
* **Language Models**: Additional models as needed for local inference

The API uses these models to ensure consistency and reduce storage overhead.

## Quick Start

### Prerequisites

* Python 3.13+
* UV package manager
* IBM Db2 database with vector support
* IBM Watsonx account (for search functionality)

### Setup

1. **Configure environment**:
   ```bash
   # Create .env file in root directory
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Download models**:
   ```bash
   mkdir -p models
   wget -O models/granite-embedding-30m-english-Q6_K.gguf \
     https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf
   ```

3. **Start the API service**:
   ```bash
   cd gateway-api
   uv sync
   uv run uvicorn gateway_api:app --reload --host 0.0.0.0 --port 8000
   ```

### Usage Example

```bash
# 1. Ingest a document
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article", "table_name": "AI_KNOWLEDGE"}'

# 2. Search and get answers
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "table_name": "AI_KNOWLEDGE"}'
```

## When to Use the Gateway API

The all-in-one gateway provides:
* **Simple deployment** - single command starts everything
* **Unified interface** - all RAG operations through one endpoint
* **Easy development** - faster iteration and debugging
* **Resource efficient** - lower memory and CPU overhead

## Roadmap

This repo is evolving from a prototype to a production-ready service. Planned enhancements:

* **Observability**: Logging, metrics, and tracing
* **Authentication**: API security and access control
* **Scalability**: Performance optimization and scaling patterns
* **UI Interface**: Web frontend for document management and search
* **Advanced RAG**: Multi-modal content, citation tracking, and source verification
* **Container Support**: Docker images and Kubernetes manifests

## Development

### Prototype Development
```bash
cd prototype/
# Open and run agent.ipynb in Jupyter
```

### API Development

```bash
cd gateway-api/
uv sync
# Modify gateway_api.py or underlying service code
```

### Testing

```bash
# Health check
curl "http://localhost:8000/health"

# Service info
curl "http://localhost:8000/services"
```

## About

This project demonstrates how AI agents can interact with structured and unstructured data using relational databases like IBM Db2. It combines vector search, local embeddings, IBM Watsonx AI, and LangGraph-based query refinement into a cohesive, production-ready RAG pipeline delivered through a unified API service.