from sqlalchemy.orm import Session

from app.models.domain import AuditLog


def write_audit(
    db: Session,
    action: str,
    actor_user_id: int | None = None,
    target: str | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target=target,
            metadata_json=metadata or {},
        )
    )
    db.commit()
