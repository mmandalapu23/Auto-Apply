"""Frontend-facing lightweight config endpoints."""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/frontend", tags=["frontend"])


@router.get("/config")
async def frontend_config():
    """Return minimal config so the frontend knows how to call the API."""
    return {
        "api_base": "/api/v1",
        "auth": {
            "jwt": True,
            "token_header": "Authorization",
            "token_prefix": "Bearer",
        },
        "storage": {
            "backend": settings.STORAGE_BACKEND,
        },
        "llm_provider": settings.LLM_PROVIDER,
    }
