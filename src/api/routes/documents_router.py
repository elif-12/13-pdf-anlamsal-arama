"""Documents API Route'lari: yukleme, listeleme, anlamsal arama, dosya servisi."""
import os
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.services.search_service import SearchService
from src.infrastructure.database.connection import get_db

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class DocumentResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_size_kb: float
    total_pages: int
    chunk_count: int
    status: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 8


class SearchResultResponse(BaseModel):
    chunk_id: str
    page: int
    similarity: float
    text: str


def _to_response(doc) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        original_filename=doc.original_filename,
        file_size_kb=doc.file_size_kb,
        total_pages=doc.total_pages,
        chunk_count=doc.chunk_count,
        status=doc.status.value,
    )


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    service = SearchService(db)
    return [_to_response(d) for d in service.list_documents()]


@router.post("/upload", status_code=201, response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyasi yuklenebilir.")

    doc_title = title or file.filename.rsplit(".", 1)[0]

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_size = os.path.getsize(file_path)

    service = SearchService(db)
    try:
        document = service.upload_document(
            title=doc_title,
            file_path=file_path,
            original_filename=file.filename,
            file_size_bytes=file_size,
        )
        return _to_response(document)
    except Exception as e:
        logger.error(f"Yukleme hatasi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    service = SearchService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Dokuman bulunamadi.")
    return _to_response(document)


@router.get("/{document_id}/file")
def get_document_file(document_id: int, db: Session = Depends(get_db)):
    service = SearchService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Dokuman bulunamadi.")
    return FileResponse(document.file_path, media_type="application/pdf")


@router.post("/{document_id}/search", response_model=list[SearchResultResponse])
def search_document(document_id: int, request: SearchRequest, db: Session = Depends(get_db)):
    service = SearchService(db)
    try:
        results = service.search(document_id=document_id, query=request.query, top_k=request.top_k)
        return [
            SearchResultResponse(
                chunk_id=r.chunk_id,
                page=r.page_number,
                similarity=r.similarity_score,
                text=r.text,
            )
            for r in results
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Arama hatasi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    service = SearchService(db)
    if not service.get_document(document_id):
        raise HTTPException(status_code=404, detail="Dokuman bulunamadi.")
    service.delete_document(document_id)
