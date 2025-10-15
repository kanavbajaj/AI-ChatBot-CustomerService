import os
import streamlit as st

from app.faq_loader import FAQRepository
from app.retriever import BM25FAQRetriever
from app.llm import LLMClient
from app.config import settings

st.set_page_config(page_title=settings.app_name, page_icon="🤖", layout="centered")
st.title(settings.app_name)

# Secrets to env (OpenRouter)
if "OPENROUTER_API_KEY" in st.secrets:
	os.environ.setdefault("OPENROUTER_API_KEY", st.secrets["OPENROUTER_API_KEY"]) 
if "OR_MODEL_NAME" in st.secrets:
	os.environ.setdefault("OR_MODEL_NAME", st.secrets["OR_MODEL_NAME"]) 
if "OR_BASE_URL" in st.secrets:
	os.environ.setdefault("OR_BASE_URL", st.secrets["OR_BASE_URL"]) 

if "messages" not in st.session_state:
	st.session_state.messages = []

repo = FAQRepository(path="data/faqs.jsonl")
retriever = BM25FAQRetriever(repo)
llm = LLMClient()

with st.sidebar:
	st.markdown("### Settings")
	model = st.text_input("Model", os.getenv("OR_MODEL_NAME", settings.openrouter_model_name))
	if model:
		os.environ["OR_MODEL_NAME"] = model
	st.caption("OpenRouter key is read from secrets or env.")

for m in st.session_state.messages:
	role = m.get("role", "assistant")
	with st.chat_message(role):
		st.markdown(m.get("content", ""))

prompt = st.chat_input("Ask a question…")
if prompt:
	st.session_state.messages.append({"role": "user", "content": prompt})
	with st.chat_message("user"):
		st.markdown(prompt)

	# Retrieve top FAQs as context
	retrieved = retriever.retrieve(prompt, top_k=settings.retriever_top_k)
	context = "\n\n".join([f"Q: {r.faq.question}\nA: {r.faq.answer}" for r in retrieved])
	system = {
		"role": "system",
		"content": (
			"You are a helpful customer support agent. Use the FAQ context when relevant. "
			"Provide concise, accurate answers. If confidence is low, suggest escalation.\n\n" + context
		),
	}
	messages_llm = [system] + st.session_state.messages

	with st.chat_message("assistant"):
		with st.spinner("Thinking…"):
			answer = st.session_state.get("_last_answer")
			try:
				answer = st.session_state.get("_last_answer") or st.run_async(llm.chat(messages_llm))
			except Exception:
				# Fallback to sync call (Streamlit Cloud may not support experimental async)
				answer = st.session_state.get("_last_answer")
				if not answer:
					import asyncio
					answer = asyncio.run(llm.chat(messages_llm))
			st.markdown(answer)
			st.session_state.messages.append({"role": "assistant", "content": answer})
			st.session_state["_last_answer"] = answer
