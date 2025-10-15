from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
	role: str = Field(pattern=r"^(user|assistant|system)$")
	content: str
	confidence: Optional[float] = None
	needs_escalation: Optional[bool] = None


class MessageRead(BaseModel):
	id: int
	role: str
	content: str
	created_at: datetime
	confidence: Optional[float] = None
	needs_escalation: Optional[bool] = None

	class Config:
		from_attributes = True


class SessionCreate(BaseModel):
	external_id: Optional[str] = None


class SessionRead(BaseModel):
	id: int
	external_id: str
	created_at: datetime
	updated_at: datetime
	user_summary: Optional[str] = None

	class Config:
		from_attributes = True


class SessionWithMessages(SessionRead):
	messages: List[MessageRead] = []
