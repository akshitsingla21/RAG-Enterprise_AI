from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
import shutil




app = FastAPI()

@app.get("/")
def home():
    return {"message": "Enterprise AI Assistant is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):

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

