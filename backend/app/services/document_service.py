import pymupdf


from pathlib import Path
from uuid import uuid4


from fastapi import UploadFile, HTTPException



# Store uploaded files in the backend/uploads folder.
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Maximum allowed upload size is 10 MB.
MAX_FILE_SIZE = 10 * 1024 * 1024

# Read files in smaller pieces to control memory usage.
CHUNK_SIZE = 1024 * 1024

# These are the document types our application supports.
ALLOWED_EXTENSIONS = {".pdf", ".txt"}




def validate_document(file_path: Path, extension: str) -> None:
    """Check whether a document contains readable content."""

    if extension == ".pdf":
        try:
            # Try opening the PDF and loading its pages.
            with file_path.open("rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:



                #checking if pdf is valid and can be opened and also has atleast some content and isn't empty
                if pdf.needs_pass or pdf.page_count == 0:
                    raise ValueError("PDF cannot be read")


                # Loading each page helps detect some damaged PDF files.

                for page_number in range(pdf.page_count):
                    pdf.load_page(page_number)

        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail="Invalid or unreadable PDF file"
            ) from error

    elif extension == ".txt":
        try:
            # Read the text file and verify UTF-8 encoding.
            with file_path.open("r", encoding="utf-8") as text_file:
                while text_file.read(CHUNK_SIZE):
                    pass

        except UnicodeError as error:
            raise HTTPException(
                status_code=400,
                detail="TXT file must contain valid UTF-8 text"
            ) from error


        

def save_document(file: UploadFile):
    """Validate an uploaded file and save it with a unique ID."""

    # Reject uploads that do not have a filename.
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    # Only PDF and TXT documents are supported.
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )


    # Generate a unique ID so files cannot overwrite each other.
    document_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{document_id}{extension}"
    temp_path = UPLOAD_DIR / f"{document_id}.upload"

    file_size = 0

    try:
        # Save the upload temporarily while checking its size.
        with temp_path.open("xb") as buffer:

            while chunk := file.file.read(CHUNK_SIZE):
                file_size += len(chunk)

                # Stop immediately if the upload exceeds our limit.
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 10 MiB limit"
                    )

                buffer.write(chunk)

        # Empty documents should not be accepted.
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty files are not allowed"
            )

        # Verify the actual contents before accepting the document.
        validate_document(temp_path, extension)

        # Move the validated document to its final filename.
        temp_path.replace(file_path)

    finally:
        # Remove any temporary file left after a failed upload.
        temp_path.unlink(missing_ok=True)

    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": filename
    }

