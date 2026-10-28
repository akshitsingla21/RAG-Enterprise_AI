# Enterprise AI Assistant

An enterprise knowledge assistant that answers questions from uploaded company documents with source citations, and performs approved support-ticket actions through backend tool calls.

> **Status: early development.** The document upload API is implemented and tested. Text extraction, retrieval, answer generation, ticket tools and the web UI are not built yet.

## What works today

- `GET /health` returns a health check.
- `POST /documents/upload` accepts one PDF or TXT file (multipart field `file`) and:
  - stores it under a server-generated document ID, so files with the same name never overwrite each other
  - rejects empty files, files over 10 MiB, unsupported extensions, unreadable or password-protected PDFs, and TXT files that are not valid UTF-8
  - removes partially written files when an upload fails

## Tech stack

| Area | Choice |
| --- | --- |
| API | Python, FastAPI |
| PDF handling | PyMuPDF |
| Tests | Pytest |
| Planned | PostgreSQL + pgvector, React + TypeScript, Docker Compose |

## Project layout

```
backend/
  app/
    main.py                  # FastAPI app and health endpoints
    api/documents.py         # HTTP routes for documents
    services/document_service.py  # upload validation and storage
  tests/                     # Pytest tests
  uploads/                   # stored uploads (git-ignored)
```

## Getting started (Windows PowerShell)

Developed with Python 3.13.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints interactively.

Run the tests (from `backend/`):

```powershell
pytest
```

## Try an upload

```powershell
curl.exe -F "file=@sample.pdf" http://127.0.0.1:8000/documents/upload
```

Example response:

```json
{
  "message": "Document uploaded successfully",
  "document_id": "7c6aa2a7-178f-4215-bdd0-b65f7663e614",
  "filename": "sample.pdf"
}
```

## Roadmap

1. Upload validation and tests (done)
2. PDF/TXT text extraction and source-aware chunking
3. PostgreSQL document metadata, embeddings with pgvector, retry-safe uploads
4. Retrieval and grounded answers with citations
5. Support-ticket tool calls with user confirmation and audit records
6. React frontend, access control, evaluation and Docker Compose setup

## Data

Use only public, properly licensed or synthetic documents with this project. Do not upload confidential work documents.
