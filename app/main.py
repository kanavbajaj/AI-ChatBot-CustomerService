from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path

from .config import settings
from .database import engine, Base
from .routers import router as api_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def on_startup():
	Base.metadata.create_all(bind=engine)

app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def index():
	index_path = Path("static/index.html")
	return index_path.read_text(encoding="utf-8")


@app.get("/health")
async def health():
	return {"status": "ok", "app": settings.app_name}
