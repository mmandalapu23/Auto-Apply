"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.web.router import router as web_router

setup_logging()

app = FastAPI(
    title="AutoApply ATS",
    description="AI-powered job application management system",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(web_router)


@app.get("/health")
async def health():
    """Service health check."""
    return {"status": "ok"}
