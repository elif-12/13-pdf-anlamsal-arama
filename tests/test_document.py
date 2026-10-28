"""Document entity testleri."""
from src.domain.entities.document import Document, DocumentStatus


class TestDocument:

    def test_varsayilan_durum_pending(self):
        doc = Document(title="Rapor", original_filename="rapor.pdf", file_path="/uploads/rapor.pdf")
        assert doc.status == DocumentStatus.PENDING

    def test_file_size_kb_hesaplanir(self):
        doc = Document(title="Rapor", file_size_bytes=2048)
        assert doc.file_size_kb == 2.0
