import os
from pathlib import Path


class Config:
    """Lightweight env-based config so the service has no heavy settings dependency."""

    def __init__(self) -> None:
        self.storage_path = Path(os.environ.get("STORAGE_PATH", "./data/storage"))
        self.max_upload_mb = int(os.environ.get("MAX_UPLOAD_MB", "50"))

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


config = Config()
