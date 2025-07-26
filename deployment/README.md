uv init --no-readme --no-workspace .

uv add fastapi uvicorn httpx pydantic

# Add FastAPI dependencies
uv add fastapi uvicorn trafilatura spacy

# Add your existing project dependencies that are needed
uv add langchain-community langchain-text-splitters
uv add langchain_ibm python-dotenv langchain-db2
uv add langchain-core ibm_db llama-cpp-python

uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

wget -O granite-embedding-30m-english-Q6_K.gguf \
  https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf

uv add ibm_db_dbi