"""File utility helpers — upload and delete."""

import os

from app.config import settings


def save_upload_file(content: bytes, filename: str) -> str:
    """Save file content to the upload directory and return the file path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def delete_file(file_path: str) -> None:
    """Delete a file from disk, ignoring if it doesn't exist."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass


def get_file_extension(filename: str) -> str:
    """Get the file extension (lowercase, without dot)."""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")


def validate_pdf(filename: str) -> bool:
    """Check if a filename has a PDF extension."""
    return get_file_extension(filename) == "pdf"
