from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile, HTTPException


# Store uploaded files in the backend/uploads folder.
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_document(file: UploadFile):

    """Check the uploaded file and save it locally."""

    # Make sure the uploaded file has a name.
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    filename = Path(file.filename).name

    # For now, we only allow PDF and text files.
    if Path(filename).suffix.lower() not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    # Give each document a unique ID to prevent overwriting files.
    document_id = str(uuid4())

    stored_filename = f"{document_id}{Path(filename).suffix.lower()}"  # so stored filename as uniqueid.pdf/txt

    file_path = UPLOAD_DIR / stored_filename

    # Copy the uploaded file into our uploads folder  (wb -> write binary)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return the ID and original name to the user.
    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": filename
    }