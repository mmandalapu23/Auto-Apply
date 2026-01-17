"""Authentication service."""
from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from datetime import timedelta


class AuthService:
    """Authentication business logic."""
    
    @staticmethod
    def register_user(db: Session, request: RegisterRequest) -> User:
        """Register new user."""
        # Check if email exists
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise ValueError(f"Email {request.email} already registered")
        
        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def login_user(db: Session, request: LoginRequest) -> TokenResponse:
        """Authenticate and return token."""
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not verify_password(request.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            email=user.email
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user
