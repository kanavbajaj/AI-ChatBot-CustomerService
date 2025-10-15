from __future__ import annotations
from typing import List

from .config import settings


def should_escalate(confidence: float) -> bool:
	return confidence < settings.escalation_threshold


def build_escalation_message() -> str:
	return (
		"I might not have enough confidence to fully resolve this. "
		"Would you like me to escalate this to a human support agent?"
	)


def summarize_conversation(messages: List[dict]) -> str:
	# Lightweight extractive summary: last user + assistant condensed
	user_latest = next((m for m in reversed(messages) if m["role"] == "user"), None)
	assistant_latest = next((m for m in reversed(messages) if m["role"] == "assistant"), None)
	parts = []
	if user_latest:
		parts.append(f"User asked: {user_latest['content'][:200]}")
	if assistant_latest:
		parts.append(f"Agent replied: {assistant_latest['content'][:200]}")
	return " | ".join(parts) if parts else ""
