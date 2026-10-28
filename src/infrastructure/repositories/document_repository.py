"""DocumentRepository: ORM model <-> domain entity cevirisi."""
from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities.document import Document, DocumentStatus
from src.domain.interfaces.document_repository import IDocumentRepository
from src.infrastructure.models.orm_models import DocumentModel


class DocumentRepository(IDocumentRepository):

    def __init__(self, db: Session):
        self._db = db

    def save(self, document: Document) -> Document:
        model = DocumentModel(
            title=document.title,
            original_filename=document.original_filename,
            file_path=document.file_path,
            file_size_bytes=document.file_size_bytes,
            total_pages=document.total_pages,
            chunk_count=document.chunk_count,
            status=document.status.value,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, document_id: int) -> Optional[Document]:
        model = self._db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        return self._to_entity(model) if model else None

    def get_all(self) -> List[Document]:
        models = self._db.query(DocumentModel).order_by(DocumentModel.created_at.desc()).all()
        return [self._to_entity(m) for m in models]

    def update_status(
        self,
        document_id: int,
        status: DocumentStatus,
        total_pages: Optional[int] = None,
        chunk_count: Optional[int] = None,
    ) -> None:
        model = self._db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not model:
            return
        model.status = status.value
        if total_pages is not None:
            model.total_pages = total_pages
        if chunk_count is not None:
            model.chunk_count = chunk_count
        self._db.commit()

    def delete(self, document_id: int) -> None:
        model = self._db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if model:
            self._db.delete(model)
            self._db.commit()

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            title=model.title,
            original_filename=model.original_filename,
            file_path=model.file_path,
            file_size_bytes=model.file_size_bytes,
            total_pages=model.total_pages,
            chunk_count=model.chunk_count,
            status=DocumentStatus(model.status),
            created_at=model.created_at,
        )
