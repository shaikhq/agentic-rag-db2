# 🔍 Local Agentic RAG Pipeline (macOS) – README

## 🎯 Use Case

This project demonstrates a clean, beginner-friendly implementation of an **Agentic RAG (Retrieval-Augmented Generation)** pipeline using **LangGraph**. My goal was to build a system that:

* Runs **fully locally** on macOS
* Avoids cloud dependencies and costs
* Allows the **LLM to take intelligent actions**: rewrite failed queries, guide search, and iterate before answering

It’s designed for developers and researchers who want to prototype **multi-step, agentic LLM workflows** with full transparency and local control — no hosted APIs or vector services required.

---

## 🙏 Acknowledgment

This implementation builds on the excellent LangChain tutorial:
🔗 [Agentic RAG with LangGraph](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)
from the LangChain team.

---

## ✨ What I’ve Added

I extended the original tutorial with the following improvements:

* **Local Embeddings** using `llama.cpp`, eliminating dependency on hosted embedding APIs
* **Cleaner Document Parsing** using `trafilatura` for robust HTML content extraction
* **Sentence-Aware Chunking** to ensure coherent and semantically meaningful text splits

These enhancements help make the RAG pipeline **lightweight, efficient, and more suitable for real-world macOS usage**.

---

# ⚙️ Setup Instructions (macOS)

## 1. ✅ Create and Activate Virtual Environment (Python 3.13)

```bash
uv venv --python $(which python3.13)
source .venv/bin/activate
```

## 2. 📦 Install Python Dependencies

```bash
uv pip install -r requirements.txt
```

## 3. 🔐 Create a `.env` File for API Credentials

In the project root, create a file named `.env`:

```bash
touch .env
```

Then add:

```
WATSONX_PROJECT=
WATSONX_APIKEY=
```

> 🔒 Replace the values with your actual Watsonx credentials.

## 4. 🧠 Install spaCy and Required Language Model

```bash
python -m ensurepip --upgrade
python -m spacy download en_core_web_sm
```

## 5. ⬇️ Download Local Embedding Model (Granite)

```bash
wget -O granite-embedding-30m-english-Q6_K.gguf \
  https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf
```

---

## 🧪 (Optional) Use .venv with Jupyter and VS Code

### Install Jupyter Support

```bash
uv pip install jupyter ipykernel
```

### Register Kernel

```bash
python -m ipykernel install --user --name=myenv --display-name "Python (.venv)"
```

### In VS Code

1. Open Command Palette: `Cmd + Shift + P`
2. **Select Python Interpreter:** Choose `.venv/bin/python` (press `Cmd + Shift + .` to reveal hidden `.venv`)
3. **Select Jupyter Interpreter:** Same as above
4. If needed, run `Developer: Reload Window` to refresh kernel list