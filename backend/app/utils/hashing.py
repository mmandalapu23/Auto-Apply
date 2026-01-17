"""Hashing utilities."""
from hashlib import sha256


def hash_file_content(content: bytes) -> str:
    """Generate SHA256 hash of file content."""
    return sha256(content).hexdigest()


def hash_string(text: str) -> str:
    """Generate SHA256 hash of string."""
    return sha256(text.encode()).hexdigest()
