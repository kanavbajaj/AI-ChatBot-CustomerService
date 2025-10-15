from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models


def create_session(db: Session, external_id: Optional[str]) -> models.ChatSession:
	session = models.ChatSession(external_id=external_id or _generate_external_id())
	db.add(session)
	db.commit()
	db.refresh(session)
	return session


def get_session(db: Session, session_id: int) -> Optional[models.ChatSession]:
	return db.get(models.ChatSession, session_id)


def get_session_by_external(db: Session, external_id: str) -> Optional[models.ChatSession]:
	stmt = select(models.ChatSession).where(models.ChatSession.external_id == external_id)
	return db.scalar(stmt)


def list_messages(db: Session, session_id: int):
	stmt = select(models.Message).where(models.Message.session_id == session_id).order_by(models.Message.created_at.asc())
	return list(db.scalars(stmt))


def add_message(
	db: Session,
	session_id: int,
	role: str,
	content: str,
	confidence: Optional[float] = None,
	needs_escalation: Optional[bool] = None,
) -> models.Message:
	msg = models.Message(
		session_id=session_id,
		role=role,
		content=content,
		confidence=confidence,
		needs_escalation=needs_escalation,
	)
	db.add(msg)
	db.commit()
	db.refresh(msg)
	return msg


def update_session_summary(db: Session, session_id: int, summary: str) -> None:
	session = get_session(db, session_id)
	if not session:
		return
	session.user_summary = summary
	session.updated_at = datetime.utcnow()
	db.add(session)
	db.commit()


def _generate_external_id() -> str:
	from secrets import token_urlsafe
	return token_urlsafe(16)
