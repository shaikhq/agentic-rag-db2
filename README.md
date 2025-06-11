uv venv --python $(which python3.13)

source .venv/bin/activate
uv pip install -r requirements.txt

Register kernel (separate step, not via uv)

bash
Copy
Edit
python -m ipykernel install --user --name=myenv --display-name "Python (.venv)"

choose the interpreter from .venv as the project interpreter at VS Code

macOS VS Code: 

n the file dialog that opens, press:

scss
Copy
Edit
Cmd + Shift + .  (Command + Shift + Period)
🔍 This reveals hidden folders like .venv.

Now you can navigate into .venv/bin and select the python or python3 interpreter file.

Using .venv with Jupyter in VS Code (macOS)
Create and activate the virtual environment

bash
Copy
Edit
uv venv .venv --python $(which python3.13)
source .venv/bin/activate
Install Jupyter and ipykernel

bash
Copy
Edit
uv pip install jupyter ipykernel
Register the kernel

bash
Copy
Edit
python -m ipykernel install --user --name=myenv --display-name "Python (.venv)"
In VS Code:

Open Command Palette (Cmd + Shift + P)

Run Python: Select Interpreter, and choose .venv/bin/python

Run Jupyter: Select Interpreter to Start Jupyter Server, and choose the same .venv

[If the kernel doesn't show up in the notebook picker immediately:]

Select any other environment temporarily

Then re-select the .venv environment

This refresh often triggers kernel discovery in VS Code

Reload the VS Code window

text
Copy
Edit
Cmd + Shift + P → Developer: Reload Window
Open or create a notebook, then select the "Python (.venv)" kernel

brew install ollama

ollama serve

ollama serve

separate terminal
ollama pull granite-embedding:30m

ollama pull mistral