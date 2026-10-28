"""Document repository interface (soyutlama)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.document import Document, DocumentStatus


class IDocumentRepository(ABC):

    @abstractmethod
    def save(self, document: Document) -> Document:
        ...

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[Document]:
        ...

    @abstractmethod
    def get_all(self) -> List[Document]:
        ...

    @abstractmethod
    def update_status(
        self,
        document_id: int,
        status: DocumentStatus,
        total_pages: Optional[int] = None,
        chunk_count: Optional[int] = None,
    ) -> None:
        ...

    @abstractmethod
    def delete(self, document_id: int) -> None:
        ...
