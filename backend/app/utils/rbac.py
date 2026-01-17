"""RBAC (Role-Based Access Control) utilities."""
from typing import Dict
from fastapi import HTTPException, status


class RBACError(HTTPException):
    """Raised when user lacks required role."""
    def __init__(self, required_role: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires '{required_role}' role"
        )


def require_admin(user: Dict) -> None:
    """
    Check if user has admin role.
    
    Args:
        user: Current user dict from auth
    
    Raises:
        RBACError: If user is not admin
    """
    user_role = user.get("role", "user")
    if user_role != "admin":
        raise RBACError("admin")


def require_user(user: Dict) -> None:
    """
    Check if user is authenticated (any role).
    This is a basic check - already handled by auth but useful for clarity.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


def is_admin(user: Dict) -> bool:
    """Check if user is admin without raising exception."""
    return user.get("role") == "admin"


def get_user_role(user: Dict) -> str:
    """Get user's role, defaulting to 'user'."""
    return user.get("role", "user")
