from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import encrypt_secret
from app.core.database import get_db
from app.dependencies import require_role
from app.models.domain import LlmSettings, User
from app.schemas import LlmSettingsRead, LlmSettingsUpsert
from app.services.audit import write_audit
from app.services.provider_detect import detect_provider

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/llm", response_model=LlmSettingsRead | None)
def get_llm_settings(
    user: Annotated[User, Depends(require_role("admin", "reviewer"))],
    db: Annotated[Session, Depends(get_db)],
) -> LlmSettingsRead | None:
    settings = db.scalar(select(LlmSettings).where(LlmSettings.is_active.is_(True)))
    if not settings:
        return None
    return LlmSettingsRead(
        provider=settings.provider,
        endpoint=settings.endpoint,
        model=settings.model,
        has_api_key=True,
        updated_at=settings.updated_at,
    )


@router.put("/llm", response_model=LlmSettingsRead)
def upsert_llm_settings(
    payload: LlmSettingsUpsert,
    user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> LlmSettingsRead:
    provider = payload.provider or detect_provider(payload.api_key, payload.endpoint, payload.model)
    if provider == "unknown":
        raise HTTPException(status_code=400, detail="Could not detect provider. Specify provider or endpoint.")
    db.query(LlmSettings).update({"is_active": False})
    settings = LlmSettings(
        provider=provider,
        endpoint=payload.endpoint,
        model=payload.model,
        encrypted_api_key=encrypt_secret(payload.api_key),
        is_active=True,
        updated_at=datetime.now(UTC),
    )
    db.add(settings)
    db.commit()
    write_audit(db, "settings.llm.updated", actor_user_id=user.id, target=provider)
    return LlmSettingsRead(
        provider=settings.provider,
        endpoint=settings.endpoint,
        model=settings.model,
        has_api_key=True,
        updated_at=settings.updated_at,
    )
