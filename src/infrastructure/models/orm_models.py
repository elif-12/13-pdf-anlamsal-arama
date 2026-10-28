"""SQLAlchemy ORM modelleri."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.infrastructure.database.connection import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    total_pages = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
