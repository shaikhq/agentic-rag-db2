# Agentic RAG with IBM Db2

This repository demonstrates how to build an **agentic Retrieval-Augmented Generation (RAG)** workflow using IBM Db2 and the `langchain-db2` connector. The project begins with a prototype in a Jupyter notebook and evolves into a modular, production-aligned implementation.

## Project Structure

```
agentic-rag-db2/
├── prototype/
├── document-ingestion-api/
└── README.md
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

### `document-ingestion-api/`

This folder initiates the transition toward production. It extracts the document ingestion logic from the prototype and exposes it as a FastAPI service. Features include:

* Ingesting documents from URLs
* Chunking and embedding
* Storing vectors into Db2’s vector index
* Modular design for deployment and testing
* Docker support for containerized execution

Refer to `document-ingestion-api/README.md` for setup instructions and API usage.

## Roadmap

This repo is evolving from a prototype to a set of deployable services. Next planned steps:

* Build the Agentic RAG Search API
* Add observability, error handling, and deployment 

## Getting Started

To try out the prototype:

```bash
cd prototype/
# Open and run agent.ipynb in Jupyter
```

To run the document engineering API:

```bash
cd document-ingestion-api/
# Follow README instructions to set up and start the FastAPI service
```

## About

This project is part of an effort to show how AI agents can interact with structured and unstructured data using relational databases like IBM Db2. It combines vector search, local embeddings, and LangGraph-based query refinement into a cohesive RAG pipeline.
