from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import encrypt_secret
from app.core.database import get_db
from app.dependencies import require_role
from app.models.domain import LlmSettings, User
from app.schemas import LlmSettingsRead, LlmSettingsUpsert, LlmTestRequest, LlmTestResponse
from app.services import clients
from app.services.audit import write_audit
from app.services.clients import ServiceError
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


@router.post("/llm/test", response_model=LlmTestResponse)
async def test_llm_settings(
    payload: LlmTestRequest,
    user: Annotated[User, Depends(require_role("admin"))],
) -> LlmTestResponse:
    """Tests credentials live (before saving) by sending a real request to the provider."""
    try:
        result = await clients.test_llm_credentials(payload.provider, payload.api_key, payload.endpoint, payload.model)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return LlmTestResponse(**result)


@router.delete("/llm", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_settings(
    user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Deactivates the current LLM key. Reviews fall back to the offline heuristic
    until a new key is configured; the onboarding modal reappears on next load."""
    active = db.scalar(select(LlmSettings).where(LlmSettings.is_active.is_(True)))
    if not active:
        return None
    db.query(LlmSettings).update({"is_active": False})
    db.commit()
    write_audit(db, "settings.llm.removed", actor_user_id=user.id, target=active.provider)
    return None


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
