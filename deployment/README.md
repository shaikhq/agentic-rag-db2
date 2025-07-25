uv init --name agentic-rag-deployment --python 3.13

uv add fastapi "uvicorn[standard]" requests beautifulsoup4 pydantic

# Start it the proper way for development
cd data_pipeline
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000


bash# Make sure you're in the deployment directory
cd ~/coding/agentic-rag-db2/deployment

# Create search pipeline files
touch search_pipeline/__init__.py
touch search_pipeline/app.py
touch search_pipeline/core.py

uv add langchain langgraph langchain-core

# Add your exact dependencies
# Install all your notebook dependencies
uv add langgraph langchain-community langchain-text-splitters ipykernel jupyter tiktoken langchain_ibm python-dotenv "langchain-ollama>=0.1.0" trafilatura spacy llama-cpp-python huggingface-hub pygraphviz langchain-db2 langchain-core ibm_db