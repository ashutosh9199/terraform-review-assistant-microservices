from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.domain import User
from app.schemas import LoginRequest, TokenResponse
from app.services.audit import write_audit

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        write_audit(db, "auth.login_failed", target=payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    roles = [role.role for role in user.roles]
    write_audit(db, "auth.login_success", actor_user_id=user.id, target=user.email)
    return TokenResponse(access_token=create_access_token(user.email, roles), roles=roles)
