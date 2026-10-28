"""
RAG Chunker Testleri
Metin parcalamanin dogru calistigini test eder.
"""
from src.rag.chunker import TextChunker


class TestTextChunker:

    def test_kisa_metin_tek_chunk(self):
        """Kisa metin tek parca olmali."""
        chunker = TextChunker(chunk_size=100, overlap=10)
        chunks = chunker.chunk("Bu kisa bir metindir.", document_id=1)
        assert len(chunks) == 1

    def test_uzun_metin_birden_fazla_chunk(self):
        """Uzun metin birden fazla parcaya bolunmeli."""
        chunker = TextChunker(chunk_size=10, overlap=2)
        text = " ".join([f"kelime{i}" for i in range(50)])
        chunks = chunker.chunk(text, document_id=1)
        assert len(chunks) > 1

    def test_chunk_id_formati(self):
        """Chunk ID'si dogru formatlanmali."""
        chunker = TextChunker(chunk_size=10, overlap=0)
        text = " ".join([f"kelime{i}" for i in range(30)])
        chunks = chunker.chunk(text, document_id=5)
        assert chunks[0].chunk_id == "doc_5_chunk_00000"
        assert chunks[1].chunk_id == "doc_5_chunk_00001"

    def test_bos_metin_bos_liste(self):
        """Bos metin icin bos liste donmeli."""
        chunker = TextChunker()
        chunks = chunker.chunk("", document_id=1)
        assert chunks == []

    def test_overlap_cakisma_saglar(self):
        """Overlap ile ardisik chunklar ortak kelime icermeli."""
        chunker = TextChunker(chunk_size=5, overlap=2)
        words = [f"k{i}" for i in range(15)]
        text = " ".join(words)
        chunks = chunker.chunk(text, document_id=1)

        first_words = chunks[0].text.split()
        second_words = chunks[1].text.split()
        overlap_words = first_words[-2:]
        assert overlap_words[0] in second_words

    def test_chunk_by_pages_global_sayac(self):
        """Sayfalar arasi chunk_index sifirlanmamali, artarak devam etmeli."""
        from src.rag.pdf_extractor import PageContent

        chunker = TextChunker(chunk_size=5, overlap=0)
        pages = [
            PageContent(page_number=1, text=" ".join(f"a{i}" for i in range(8)), word_count=8),
            PageContent(page_number=2, text=" ".join(f"b{i}" for i in range(8)), word_count=8),
        ]
        chunks = chunker.chunk_by_pages(pages, document_id=1)
        indices = [c.chunk_index for c in chunks]
        assert indices == sorted(indices)
        assert len(set(indices)) == len(indices)
