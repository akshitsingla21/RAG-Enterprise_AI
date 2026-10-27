
from pathlib import Path
import shutil

from fastapi import UploadFile, HTTPException


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_document(file: UploadFile):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    filename = Path(file.filename).name

    if Path(filename).suffix.lower() not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Document uploaded successfully",
        "filename": filename
    }
