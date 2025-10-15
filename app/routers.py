from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from . import crud, schemas
from .faq_loader import FAQRepository
from .retriever import BM25FAQRetriever
from .llm import LLMClient
from .config import settings
from .escalation import should_escalate, build_escalation_message, summarize_conversation

router = APIRouter(prefix="/api")


@router.post("/sessions", response_model=schemas.SessionRead)
def create_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
	sess = crud.create_session(db, payload.external_id)
	return sess


@router.get("/sessions/{session_id}", response_model=schemas.SessionWithMessages)
def get_session(session_id: int, db: Session = Depends(get_db)):
	sess = crud.get_session(db, session_id)
	if not sess:
		raise HTTPException(status_code=404, detail="Session not found")
	messages = crud.list_messages(db, session_id)
	return schemas.SessionWithMessages(
		id=sess.id,
		external_id=sess.external_id,
		created_at=sess.created_at,
		updated_at=sess.updated_at,
		user_summary=sess.user_summary,
		messages=[schemas.MessageRead.model_validate(m) for m in messages],
	)


@router.get("/sessions/{session_id}/messages", response_model=List[schemas.MessageRead])
def list_messages(session_id: int, db: Session = Depends(get_db)):
	return [schemas.MessageRead.model_validate(m) for m in crud.list_messages(db, session_id)]


@router.post("/sessions/{session_id}/messages", response_model=schemas.MessageRead)
async def send_message(session_id: int, payload: schemas.MessageCreate, db: Session = Depends(get_db)):
	sess = crud.get_session(db, session_id)
	if not sess:
		raise HTTPException(status_code=404, detail="Session not found")
	if payload.role != "user":
		raise HTTPException(status_code=400, detail="Only user messages can be sent to this endpoint")

	# Save user message
	crud.add_message(db, session_id, role="user", content=payload.content)

	# Retrieve FAQs
	repo = FAQRepository(path="data/faqs.jsonl")
	retriever = BM25FAQRetriever(repo)
	retrieved = retriever.retrieve(payload.content, top_k=settings.retriever_top_k)

	# Compose system prompt with top FAQs
	context = "\n\n".join([f"Q: {r.faq.question}\nA: {r.faq.answer}" for r in retrieved])
	system = {
		"role": "system",
		"content": (
			"You are a helpful customer support agent. Use the FAQ context when relevant. "
			"Provide concise, accurate answers. If confidence is low, suggest escalation.\n\n" + context
		),
	}

	# Build LLM messages
	history_models = crud.list_messages(db, session_id)
	history = [
		{"role": m.role, "content": m.content} for m in history_models
	]
	messages_llm = [system] + history + [{"role": "user", "content": payload.content}]

	# Call LLM
	llm = LLMClient()
	answer = await llm.chat(messages_llm)

	# Simple heuristic for confidence using top FAQ score
	confidence = float(retrieved[0].score) if retrieved else 0.0
	needs_escalation = should_escalate(confidence)

	if needs_escalation:
		answer = f"{answer}\n\n{build_escalation_message()}"

	assistant_msg = crud.add_message(
		db,
		session_id,
		role="assistant",
		content=answer,
		confidence=confidence,
		needs_escalation=needs_escalation,
	)

	# Optional periodic summary
	if len(history_models) + 2 >= settings.summary_after_messages:  # +2 for user+assistant we just added
		conv_for_summary = [
			{"role": m.role, "content": m.content} for m in crud.list_messages(db, session_id)
		]
		summary = summarize_conversation(conv_for_summary)
		if summary:
			crud.update_session_summary(db, session_id, summary)

	return schemas.MessageRead.model_validate(assistant_msg)
