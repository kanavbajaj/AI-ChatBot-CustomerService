from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class ChatSession(Base):
	__tablename__ = "chat_sessions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
	user_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

	messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"))
	role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant" | "system"
	content: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
	needs_escalation: Mapped[bool | None] = mapped_column(Integer, nullable=True)  # 0/1 for SQLite

	session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")
