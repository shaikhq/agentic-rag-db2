# 1. Initialize UV project
uv init --no-readme --no-workspace .

# 2. Add core FastAPI dependencies (remove duplicates)
uv add fastapi uvicorn httpx pydantic

# 3. Add text processing dependencies
uv add trafilatura spacy

# 4. Add LangChain dependencies
uv add langchain-community langchain-text-splitters langchain-core
uv add langchain_ibm langchain-db2
uv add langgraph

# 5. Add IBM and database dependencies
uv add ibm_db python-dotenv

# 6. Add ML/embedding dependencies
uv add llama-cpp-python

# 7. Install spaCy model
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# 8. Download embedding model
wget -O granite-embedding-30m-english-Q6_K.gguf \
  https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf