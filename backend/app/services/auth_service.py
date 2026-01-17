"""Authentication service for user registration and login."""
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    """Handles user authentication operations."""

    @staticmethod
    def register(db: Session, request: RegisterRequest) -> User:
        """
        Register a new user account.

        Raises:
            ValueError: If email is already registered.
        """
        if db.query(User).filter(User.email == request.email).first():
            raise ValueError(f"Email {request.email} is already registered")

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
    def login(db: Session, request: LoginRequest) -> TokenResponse:
        """
        Authenticate user and generate access token.

        Raises:
            ValueError: If credentials are invalid.
        """
        user = db.query(User).filter(User.email == request.email).first()

        if not user or not verify_password(request.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
        )

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """
        Retrieve user by ID.

        Raises:
            ValueError: If user not found.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    # Backward-compatible aliases
    register_user = register
    login_user = login
    get_user_by_id = get_user
