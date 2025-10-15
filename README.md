# AI Customer Support Bot

A FastAPI-based backend with BM25 FAQ retrieval and LLM integration (OpenRouter primary; HF fallback) to simulate customer support interactions, including session tracking, contextual memory, and escalation simulation. Includes a minimal static chat UI.

## Deploy to Vercel
- This repo includes `api/index.py` and `vercel.json` for Vercel’s Python runtime.
- We use a lightweight BM25 retriever (pure Python) to fit the 250 MB unzipped limit for Serverless Functions.
- Set Project Environment Variables:
  - `OPENROUTER_API_KEY`, `OR_MODEL_NAME`, `OR_BASE_URL=https://openrouter.ai/api/v1`
- Deploy from the GitHub repository.

## Local Dev
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/`.

## Features
- REST API for sessions and messages
- TF-IDF FAQ retriever (scikit-learn)
- LLM integration (OpenRouter by default; HF fallback; mock if offline)
- Session persistence (SQLite + SQLAlchemy)
- Escalation suggestion when confidence is low
- Lightweight conversation summarization
- Minimal frontend for demo (`/`)

## Providers

### OpenRouter (primary)
Set env vars:
```
OPENROUTER_API_KEY=sk-or-...
OR_MODEL_NAME=meta-llama/llama-3.1-8b-instruct
OR_BASE_URL=https://openrouter.ai/api/v1
```
Notes: OpenAI-compatible; headers `HTTP-Referer` and `X-Title` are sent automatically.

### Hugging Face (fallback)
Optional envs:
```
HUGGINGFACE_API_KEY=hf_...
HF_MODEL_NAME=huggingfaceh4/zephyr-7b-beta
```
If set, used as a fallback via the models endpoint.

## API
- `POST /api/sessions`
- `GET /api/sessions/{id}`
- `GET /api/sessions/{id}/messages`
- `POST /api/sessions/{id}/messages`

## Data
`data/faqs.jsonl` JSONL with `id`, `question`, `answer`.

## Demo Video Tips
- Show session creation, a known FAQ question, and a non-FAQ to trigger escalation.

# Streamlit Deployment

Deploy on Streamlit Cloud:

1) Push repo to GitHub.
2) Go to `https://share.streamlit.io` → New app → pick this repo and set `main file` to `streamlit_app.py`.
3) In App settings → Secrets, paste:
```
OPENROUTER_API_KEY = "sk-or-..."
OR_MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"
OR_BASE_URL = "https://openrouter.ai/api/v1"
```
4) Deploy. The chat UI will be available at your Streamlit app URL.

Notes:
- Messages are stored in `st.session_state` only; persistence across sessions is not included in the Streamlit UI (the FastAPI API still provides DB-backed persistence if you run the backend).
