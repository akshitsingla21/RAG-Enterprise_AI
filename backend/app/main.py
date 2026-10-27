
from fastapi import FastAPI
from app.api.documents import router as document_router

app = FastAPI(title="Enterprise AI Assistant")

app.include_router(document_router)


@app.get("/")
def home():
    return {"message": "Enterprise AI Assistant is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
