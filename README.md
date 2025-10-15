# AI Customer Support Bot

A FastAPI-based backend with TF-IDF FAQ retrieval and LLM integration to simulate customer support interactions, including session tracking, contextual memory, and escalation simulation. Includes a minimal static chat UI.

## Features
- REST API for sessions and messages
- TF-IDF FAQ retriever (scikit-learn)
- LLM integration (OpenRouter by default; HF fallback; mock if offline)
- Session persistence (SQLite + SQLAlchemy)
- Escalation suggestion when confidence is low
- Lightweight conversation summarization
- Minimal frontend for demo (`/`)

## Getting Started

### Prerequisites
- Python 3.11+

### Install
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000/`.

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
