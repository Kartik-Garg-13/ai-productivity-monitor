from fastapi import HTTPException, status


def enforce_role(current_role: str, required_role: str) -> None:
    if current_role != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{required_role} role required")
