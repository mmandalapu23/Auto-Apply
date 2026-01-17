"""Storage adapters to allow swapping local disk for S3/R2."""
from pathlib import Path
from typing import Protocol, runtime_checkable, Optional

from app.core.config import settings


@runtime_checkable
class StorageAdapter(Protocol):
    def store_text(self, key: str, content: str) -> str:
        ...


class LocalStorageAdapter:
    """Store files on local filesystem."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def store_text(self, key: str, content: str) -> str:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        # Return relative key for consumers
        return str(key)


class S3StorageAdapter:
    """S3-compatible storage (works for AWS S3 or R2/MinIO via endpoint URL)."""

    def __init__(self, bucket: str, region: Optional[str] = None, endpoint_url: Optional[str] = None):
        try:
            import boto3  # type: ignore
        except ImportError as exc:
            raise RuntimeError("boto3 is required for S3 storage backend") from exc

        self.bucket = bucket
        session = boto3.session.Session()
        self.client = session.client("s3", region_name=region, endpoint_url=endpoint_url)

    def store_text(self, key: str, content: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content.encode("utf-8"), ContentType="text/html")
        # Return the object key; caller can prepend CDN/endpoint if desired
        return key


def get_storage_adapter() -> StorageAdapter:
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        if not settings.STORAGE_S3_BUCKET:
            raise RuntimeError("STORAGE_S3_BUCKET must be set for s3 backend")
        return S3StorageAdapter(
            bucket=settings.STORAGE_S3_BUCKET,
            region=settings.STORAGE_S3_REGION or None,
            endpoint_url=settings.STORAGE_S3_ENDPOINT_URL or None,
        )
    # default: local
    return LocalStorageAdapter(settings.STORAGE_PATH)
