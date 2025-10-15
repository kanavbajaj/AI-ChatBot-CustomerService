from __future__ import annotations
from typing import List
import os
import sys

import httpx

from .config import settings

try:
	from huggingface_hub import InferenceClient  # type: ignore
except Exception:  # pragma: no cover
	InferenceClient = None  # type: ignore


HF_API_BASE = "https://api-inference.huggingface.co/models"
FALLBACK_MODELS = [
	"huggingfaceh4/zephyr-7b-beta",
	"tinyllama/tinyllama-1.1b-chat-v1.0",
]


class LLMClient:
	def __init__(self):
		# OpenRouter first
		self._or_api_key = settings.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
		self._or_model = (settings.openrouter_model_name or os.getenv("OR_MODEL_NAME") or "").strip()
		self._or_base = (settings.openrouter_base_url or os.getenv("OR_BASE_URL") or "https://openrouter.ai/api/v1").strip()

		# HF fallback
		self._hf_api_key = settings.hf_api_key or os.getenv("HUGGINGFACE_API_KEY")
		self._hf_model = (settings.hf_model_name or os.getenv("HF_MODEL_NAME") or "").strip().lower()
		self._hf_client = None
		if InferenceClient is not None and self._hf_model:
			self._hf_client = InferenceClient(model=self._hf_model, token=self._hf_api_key)

	async def chat(self, messages: List[dict]) -> str:
		# 1) OpenRouter (OpenAI-compatible)
		try:
			text = await self._openrouter_chat(messages)
			if text:
				return text
		except Exception as e:
			print(f"[OpenRouter failed] {type(e).__name__}: {e}", file=sys.stderr)

		# 2) HF models endpoint with fallbacks
		prompt = self._to_text_prompt(messages)
		models_to_try = [m for m in [self._hf_model] + FALLBACK_MODELS if m]
		for model_name in models_to_try:
			try:
				text = await self._call_hf_inference_api(prompt, model_name)
				if text:
					return text.strip()
			except Exception as e:
				print(f"[HF models endpoint failed:{model_name}] {type(e).__name__}: {e}", file=sys.stderr)

		# 3) Mock
		return self._mock_reply(messages)

	async def _openrouter_chat(self, messages: List[dict]) -> str | None:
		if not self._or_model:
			return None
		url = f"{self._or_base}/chat/completions"
		headers = {
			"Authorization": f"Bearer {self._or_api_key}" if self._or_api_key else "",
			"Content-Type": "application/json",
			"HTTP-Referer": "http://localhost:8000",
			"X-Title": settings.app_name,
		}
		payload = {
			"model": self._or_model,
			"messages": [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages],
			"temperature": 0.2,
			"max_tokens": 400,
		}
		async with httpx.AsyncClient(timeout=60) as client:
			resp = await client.post(url, headers=headers, json=payload)
			if resp.status_code == 200:
				j = resp.json()
				return (j["choices"][0]["message"]["content"] or "").strip()
			# surface error
			try:
				err = resp.json()
				raise RuntimeError(f"{resp.status_code}: {err}")
			except Exception:
				raise RuntimeError(f"{resp.status_code}: {resp.text}")

	async def _call_hf_inference_api(self, prompt: str, model_name: str) -> str | None:
		model_name = (model_name or "").strip().lower()
		headers = {"Accept": "application/json"}
		if self._hf_api_key:
			headers["Authorization"] = f"Bearer {self._hf_api_key}"
		payload = {
			"inputs": prompt,
			"parameters": {
				"max_new_tokens": 400,
				"temperature": 0.2,
				"return_full_text": False,
			},
		}
		url = f"{HF_API_BASE}/{model_name}"
		async with httpx.AsyncClient(timeout=60) as client:
			resp = await client.post(url, headers=headers, json=payload)
			if resp.status_code == 200:
				data = resp.json()
				if isinstance(data, list) and data:
					item = data[0]
					if isinstance(item, dict):
						return item.get("generated_text") or item.get("summary_text") or ""
					return str(item)
				if isinstance(data, dict):
					return data.get("generated_text") or data.get("summary_text") or data.get("text") or ""
				if isinstance(data, str):
					return data
			try:
				err = resp.json()
				raise RuntimeError(f"{resp.status_code}: {err}")
			except Exception:
				raise RuntimeError(f"{resp.status_code}: {resp.text}")

	def _to_text_prompt(self, messages: List[dict]) -> str:
		lines: List[str] = [
			"You are a helpful customer support agent. Use the provided context when relevant. Provide concise, accurate answers. If confidence is low, suggest escalation.",
		]
		for m in messages:
			role = m.get("role", "user")
			content = m.get("content", "")
			prefix = "User:" if role == "user" else ("Assistant:" if role == "assistant" else "System:")
			lines.append(f"{prefix} {content}")
		lines.append("Assistant:")
		return "\n".join(lines)

	def _mock_reply(self, messages: List[dict]) -> str:
		last_user = next((m for m in reversed(messages) if m.get("role") == "user"), {"content": ""})
		return f"[Mock AI] I understand your question: '{last_user['content']}'. Here is a helpful answer based on our FAQs."
