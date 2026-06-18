import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _local_fernet() -> Fernet:
    settings = get_settings()
    if settings.fernet_key:
        return Fernet(settings.fernet_key.encode("utf-8"))
    digest = hashlib.sha256(settings.jwt_secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str) -> str:
    return _local_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    return _local_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
