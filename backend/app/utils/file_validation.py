import os

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".xls", ".xlsx", ".zip",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def validate_upload_file(filename: str | None, content: bytes, *, image_only: bool = False) -> None:
    from fastapi import HTTPException

    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit")
    ext = os.path.splitext(filename or "")[1].lower()
    allowed = IMAGE_EXTENSIONS if image_only else ALLOWED_EXTENSIONS
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext or 'unknown'}'. Allowed: {', '.join(sorted(allowed))}",
        )
