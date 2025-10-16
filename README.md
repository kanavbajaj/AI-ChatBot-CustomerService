# Demo Video

[▶️ Watch the demo](https://github.com/user-attachments/assets/ea6bff1c-cbed-488e-9a75-0d29497d58f3)

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



## Prompts

System template used when answering (top-N FAQs are concatenated into Context):

```
You are a helpful customer support agent. Use the FAQ context when relevant. Provide concise, accurate answers. If confidence is low, suggest escalation.

[Context]
Q: <faq_1_question>
A: <faq_1_answer>

Q: <faq_2_question>
A: <faq_2_answer>
...
```

Chat message format sent to the model (OpenAI-compatible):

```
[
  {"role": "system", "content": SYSTEM_TEMPLATE_WITH_CONTEXT},
  {"role": "user", "content": "<user question 1>"},
  {"role": "assistant", "content": "<assistant reply 1>"},
  {"role": "user", "content": "<user question 2>"}
]
```

Heuristics and escalation:
- We compute a retrieval confidence from the top FAQ score.
- If confidence < threshold (default 0.45), we append an escalation suggestion:
  "I might not have enough confidence to fully resolve this. Would you like me to escalate this to a human support agent?"

Suggested testing queries:
- "How long does shipping take?" (should match an FAQ)
- "What is your refund policy?"
- "Can I change my shipping address after placing an order?"
- "Do you offer telephone support?" (likely to trigger escalation)
