from fastapi.testclient import TestClient

from app.main import app
from app.services import document_service
import pymupdf

# Create a client that can send requests to our FastAPI app.
client = TestClient(app)



#------------------TEST 1 : happy path for txt file ------------------------

def test_valid_txt_upload(tmp_path, monkeypatch):

    # Use a temporary folder instead of our real uploads folder.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Simulate uploading a text file.
    response = client.post(
        "/documents/upload",
        files={
            "file": ("test.txt", b"Hello from our RAG project")  # b" text" is used to mimic the http request behaviour as the txt is converted to bytes( hexadecimal form)
        }
    )

    # Check whether the API accepted the upload.
    assert response.status_code == 200

    # Check whether the response contains a document ID.
    assert "document_id" in response.json()

    # Check whether one TXT file was actually saved.
    assert len(list(tmp_path.glob("*.txt"))) == 1



    #---------------- TEST 2 : Test for empty txt file ---------------------------------

def test_empty_file_upload(tmp_path, monkeypatch):

    # Use a temporary folder so real uploads are unaffected.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Simulate uploading an empty TXT file.
    response = client.post(
        "/documents/upload",
        files={
            "file": ("empty.txt", b"")
        }
    )

    # An empty file should be rejected.
    assert response.status_code == 400

    # Check that the API returns the expected error.
    assert response.json()["detail"] == "Empty files are not allowed"

    # No files, including temporary files, should remain.
    assert list(tmp_path.iterdir()) == []    




    #------------- TEST 3 : FILE EXCEEDING  MAX THRESHOLD ALLOWED --------------------------

def test_oversized_file_upload(tmp_path, monkeypatch):

    # Save test uploads in a temporary folder.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Create a file that is exactly one byte above our limit.
    oversized_content = b"a" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        files={
            "file": ("large.txt", oversized_content)
        }
    )

    # Files exceeding 10 MiB must be rejected.
    assert response.status_code == 413

    # Check that the correct error message is returned.
    assert response.json()["detail"] == "File exceeds the 10 MiB limit"

    # Verify that no incomplete file remains in storage.
    assert list(tmp_path.iterdir()) == []    



    # ---------------TEST 4 : Fake PDF------------------------------------------

def test_fake_pdf_upload(tmp_path, monkeypatch):

    # Keep test uploads separate from real documents.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Give ordinary text a PDF filename.
    fake_pdf_content = b"Hello, I am not actually a PDF!"

    response = client.post(
        "/documents/upload",
        files={
            "file": ("document.pdf", fake_pdf_content)
        }
    )

    # The API should reject the fake PDF.
    assert response.status_code == 400

    # Verify the error message.
    assert response.json()["detail"] == "Invalid or unreadable PDF file"

    # No invalid or temporary file should remain.
    assert list(tmp_path.iterdir()) == []    



    # --------------------TEST 5 : TEST actual PDF----------------------------------

def test_valid_pdf_upload(tmp_path, monkeypatch):

    # Keep test files separate from actual uploads.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Create a real PDF using PyMuPDF.
    pdf = pymupdf.open()
    pdf.new_page()
    pdf_bytes = pdf.tobytes()
    pdf.close()

    # Upload the PDF to our API.
    response = client.post(
        "/documents/upload",
        files={
            "file": ("sample.pdf", pdf_bytes)
        }
    )

    # A valid PDF should be accepted.
    assert response.status_code == 200

    # Check that the PDF was saved.
    assert len(list(tmp_path.glob("*.pdf"))) == 1    



    # ------------------------TEST 6 — Test invalid UTF-8 text files ---------------------------

def test_invalid_utf8_upload(tmp_path, monkeypatch):

    # Use a temporary folder instead of real storage.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # These bytes are not valid UTF-8.
    invalid_content = b"\xff\xfe\xfa"

    response = client.post(
        "/documents/upload",
        files={
            "file": ("invalid.txt", invalid_content)
        }
    )

    # Invalid text content should be rejected.
    assert response.status_code == 400

    # Verify the correct error message.
    assert response.json()["detail"] == (
        "TXT file must contain valid UTF-8 text"
    )

    # Rejected files must not remain in storage.
    assert list(tmp_path.iterdir()) == []    



    # ------------------------TEST 7 — Test unsupported file extensions---------------------------

def test_unsupported_file_extension(tmp_path, monkeypatch):

    # Keep test files separate from real uploads.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Attempt to upload an unsupported file type.
    response = client.post(
        "/documents/upload",
        files={
            "file": ("program.exe", b"Some file content")
        }
    )

    # Unsupported file formats must be rejected.
    assert response.status_code == 400

    # Verify that the correct error message is returned.
    assert response.json()["detail"] == (
        "Only PDF and TXT files are supported"
    )

    # No file should be stored.
    assert list(tmp_path.iterdir()) == []    


    # ------------------------TEST 8 — Test duplicate filenames--------------------------------------


def test_duplicate_filename_upload(tmp_path, monkeypatch):

    # Use temporary storage for the test.
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path)

    # Upload the first document.
    response1 = client.post(
        "/documents/upload",
        files={
            "file": ("report.txt", b"This is the first report")
        }
    )

    # Upload a different document with the same filename.
    response2 = client.post(
        "/documents/upload",
        files={
            "file": ("report.txt", b"This is the second report")
        }
    )

    # Both uploads should succeed.
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Each document should have a different UUID.
    assert (
        response1.json()["document_id"]
        != response2.json()["document_id"]
    )

    # Both files must exist in storage.
    saved_files = list(tmp_path.glob("*.txt"))
    assert len(saved_files) == 2

    # Verify that neither document's contents were overwritten.
    saved_contents = {file.read_bytes() for file in saved_files}

    assert saved_contents == {
        b"This is the first report",
        b"This is the second report"
    }    