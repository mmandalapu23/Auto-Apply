"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user."""
    try:
        user = AuthService.register_user(db, request)
        token = AuthService.login_user(db, LoginRequest(email=request.email, password=request.password))
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user."""
    try:
        token = AuthService.login_user(db, request)
        return token
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
