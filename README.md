# AI Bug Reproduction Assistant (Streamlit)

A production-ready Streamlit web app that takes **error logs + code** and outputs:

- Root cause analysis
- Deterministic reproduction steps
- Suggested fixes (with patch guidance)
- A minimal test case to prevent regressions

It uses a **local Ollama model** (default: `llama3`) and is designed for easy deployment (Docker or any container platform that can reach your Ollama host).

## Features

- **Clean UI**: structured input areas, settings sidebar, downloadable report
- **Safety**: optional secret redaction for logs/code before sending to the model
- **Reliability**: structured JSON output with schema validation + fallback parsing
- **Modular**: `app.py` plus `utils/` modules for prompts, parsing, OpenAI client, UI helpers

## Quickstart (local)

1) Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Ensure Ollama is running

- Install Ollama and pull the model:

```bash
ollama pull llama3
```

- Start Ollama (it typically listens on `http://localhost:11434`)

4) Run the app

```bash
streamlit run app.py
```

## Configuration

Environment variables:

- `OLLAMA_BASE_URL` (optional, default: `http://localhost:11434`)
- `OLLAMA_MODEL` (optional, default: `llama3`)

You can also set these in Streamlit Community Cloud “Secrets” or a platform-specific secret manager.

## Deployment

### Streamlit Community Cloud

- Push this repository to GitHub.
- Ensure the deployed app can reach your Ollama host (not typical for Streamlit Cloud).
- Deploy using `app.py`.

### Docker

```bash
docker build -t ai-bug-assistant .
docker run -p 8501:8501 -e OLLAMA_BASE_URL="http://host.docker.internal:11434" -e OLLAMA_MODEL="llama3" ai-bug-assistant
```

## Project structure

```
.
├─ app.py
├─ requirements.txt
├─ Dockerfile
├─ .streamlit/
│  └─ config.toml
├─ .env.example
└─ utils/
   ├─ __init__.py
   ├─ ollama_client.py
   ├─ prompting.py
   ├─ parsing.py
   ├─ redaction.py
   ├─ report.py
   └─ ui.py
```

## Notes

- This app is intended to generate *actionable engineering output*. Always validate suggested changes before applying them in production code.

