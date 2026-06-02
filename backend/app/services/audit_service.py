from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def log_action(
    db: Session,
    *,
    user: User | None,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.flush()
    return entry
