from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
	pass


engine = create_engine(
	settings.database_url,
	connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
	pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_initialized = False


def _ensure_tables_once():
	global _initialized
	if _initialized:
		return
	# Import models here to avoid circular import at module load
	from . import models  # noqa: F401
	Base.metadata.create_all(bind=engine)
	_initialized = True


def get_db():
	_ensure_tables_once()
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
