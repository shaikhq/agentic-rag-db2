
# 🛠️ LangGraph Agentic RAG – Setup Guide (macOS)

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

Open `.env` in your editor and add the following:

```
WATSONX_PROJECT=
WATSONX_APIKEY=
```

> 🔒 Replace the values with your actual Watsonx project and API key.

## 4. 🧠 Install Language Model and spaCy Dependencies

```bash
python -m ensurepip --upgrade
python -m spacy download en_core_web_sm
```

## 5. ⬇️ Download Embedding Model (Granite)

```bash
wget -O granite-embedding-30m-english-Q6_K.gguf \
  https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf
```

---

## 🧪 Optional: Use .venv with Jupyter and VS Code

### 6. 🧰 Install Jupyter & Kernel Support

```bash
uv pip install jupyter ipykernel
```

### 7. 🧠 Register Jupyter Kernel

```bash
python -m ipykernel install --user --name=myenv --display-name "Python (.venv)"
```

---

## 💻 Set Up VS Code for .venv (macOS)

### Select the Interpreter:

1. Open Command Palette: `Cmd + Shift + P`
2. Run: **Python: Select Interpreter**
3. If `.venv` is hidden, press `Cmd + Shift + .` to reveal it
4. Navigate to `.venv/bin` and select `python` or `python3`

### Select Interpreter for Jupyter Server:

1. Open Command Palette: `Cmd + Shift + P`
2. Run: **Jupyter: Select Interpreter to Start Jupyter Server**
3. Choose `.venv/bin/python`

### \[Troubleshooting]

If the kernel doesn't appear:

* Temporarily select another environment
* Re-select `.venv` to trigger refresh
* Run: `Cmd + Shift + P → Developer: Reload Window`

Then open/create a notebook and select **"Python (.venv)"** as the kernel.
