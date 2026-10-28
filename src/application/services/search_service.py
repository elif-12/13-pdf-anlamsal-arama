"""
SearchService
PDF yukleme, indeksleme ve anlamsal arama ("semantic Ctrl+F") is mantigi.
"""
from typing import List, Optional

from loguru import logger
from sqlalchemy.orm import Session

from src.domain.entities.document import Document, DocumentStatus
from src.infrastructure.repositories.document_repository import DocumentRepository
from src.rag.chunker import TextChunker
from src.rag.pdf_extractor import PDFExtractor
from src.rag.vector_store import SearchResult, get_vector_store


class SearchService:

    def __init__(self, db: Session):
        self._repo = DocumentRepository(db)
        self._extractor = PDFExtractor()
        self._chunker = TextChunker()
        self._vector_store = get_vector_store()

    def upload_document(
        self,
        title: str,
        file_path: str,
        original_filename: str,
        file_size_bytes: int,
    ) -> Document:
        """PDF'i kaydeder, metnini cikarir, parcalar ve vektor veritabanina indeksler."""
        document = Document(
            title=title,
            original_filename=original_filename,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.PENDING,
        )
        saved = self._repo.save(document)

        try:
            self._repo.update_status(saved.id, DocumentStatus.PROCESSING)

            extracted = self._extractor.extract(file_path)
            chunks = self._chunker.chunk_by_pages(extracted.pages, document_id=saved.id)
            self._vector_store.add_chunks(chunks, document_id=saved.id)

            self._repo.update_status(
                saved.id,
                DocumentStatus.COMPLETED,
                total_pages=extracted.total_pages,
                chunk_count=len(chunks),
            )
            logger.info(f"Dokuman indekslendi: '{title}' (id={saved.id}, {len(chunks)} chunk)")
        except Exception as e:
            self._repo.update_status(saved.id, DocumentStatus.FAILED)
            logger.error(f"Dokuman islenirken hata: {e}")
            raise

        return self._repo.get_by_id(saved.id)

    def search(self, document_id: int, query: str, top_k: int = 8) -> List[SearchResult]:
        """Dokuman icinde anlamsal arama yapar (Ctrl+F'in anlamsal karsiligi)."""
        document = self._repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Dokuman bulunamadi: id={document_id}")
        if document.status != DocumentStatus.COMPLETED:
            raise ValueError(f"Dokuman henuz hazir degil (durum={document.status.value}).")

        if not query or not query.strip():
            raise ValueError("Arama sorgusu bos olamaz.")

        return self._vector_store.search(query=query, document_id=document_id, top_k=top_k)

    def list_documents(self) -> List[Document]:
        return self._repo.get_all()

    def get_document(self, document_id: int) -> Optional[Document]:
        return self._repo.get_by_id(document_id)

    def delete_document(self, document_id: int) -> None:
        self._vector_store.delete_by_document(document_id)
        self._repo.delete(document_id)
