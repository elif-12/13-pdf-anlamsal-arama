"""
Document entity.
Kullanicinin yukledigi ve uzerinde anlamsal arama yapilan PDF.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Document:
    id: Optional[int] = None
    title: str = ""
    original_filename: str = ""
    file_path: str = ""
    file_size_bytes: int = 0
    total_pages: int = 0
    chunk_count: int = 0
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: Optional[datetime] = field(default=None)

    @property
    def file_size_kb(self) -> float:
        return round(self.file_size_bytes / 1024, 1)
