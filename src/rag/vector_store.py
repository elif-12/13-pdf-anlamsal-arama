"""
ChromaDB ile vektor veritabani islemleri.
PDF chunklari buraya kaydedilir ve anlamsal benzerlik aramasi yapilir.

Embedding modeli: local/ucretsiz sentence-transformers, coklu dil destekli
(paraphrase-multilingual-MiniLM-L12-v2). Bu sayede dokuman Ingilizce,
sorgu Turkce (veya tam tersi) olsa bile anlamsal eslesme calisir: model
ayni anlami tasiyan farkli dillerdeki cumleleri vektor uzayinda birbirine
yakin yerlestirir. API key gerektirmez, internet olmadan da calisir
(model bir kere indirilir, ~420MB).
"""
from dataclasses import dataclass
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions
from loguru import logger


def _load_embedding_function(model_name: str):
    """
    Model diskte cache'liyse HF Hub'a sormadan yukler: hub her baslangicta
    "guncel mi" diye sorup saniyeler suren bir ag cagrisi yapar, oysa model
    pratikte hic degismez. Cache yoksa (ilk calistirma) internetten indirir.

    HF_HUB_OFFLINE ortam degiskeni burada kullanilamaz: huggingface_hub onu
    import aninda bir kez okur, sonradan geri almak ayni process'te etkisizdir
    ve ilk calistirmada indirme hic yapilamaz.
    """
    try:
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name, local_files_only=True
        )
    except Exception:
        logger.info("Model cache'de bulunamadi, internetten indiriliyor...")
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)


@dataclass
class SearchResult:
    chunk_id: str
    text: str
    document_id: int
    page_number: int
    chunk_index: int
    similarity_score: float


class VectorStore:
    """
    ChromaDB uzerinde embed + arama islemlerini yonetir.

    Kullanim:
        store = VectorStore()
        store.add_chunks(chunks, document_id=1)
        results = store.search("motor bakim periyodu nedir", document_id=1, top_k=5)
    """

    COLLECTION_NAME = "pdf_chunks"
    EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, persist_dir: str = "./chroma_db"):
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._embedding_fn = _load_embedding_function(self.EMBEDDING_MODEL)
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"VectorStore hazir. Koleksiyon: {self.COLLECTION_NAME}")

    def add_chunks(self, chunks: list, document_id: int) -> None:
        """Chunklari ChromaDB'ye ekler. Ayni dokumana ait eski chunklari once siler."""
        if not chunks:
            logger.warning("Eklenecek chunk yok.")
            return

        self.delete_by_document(document_id)

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "page_number": c.page_number,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ]

        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            self._collection.add(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

        logger.info(f"document_id={document_id}: {len(chunks)} chunk ChromaDB'ye eklendi.")

    def search(
        self,
        query: str,
        document_id: Optional[int] = None,
        top_k: int = 8,
    ) -> List[SearchResult]:
        """Sorguya en yakin chunklari bulur (Ctrl+F'in anlamsal karsiligi)."""
        where = {"document_id": document_id} if document_id is not None else None

        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
        )

        search_results = []
        if not results["ids"] or not results["ids"][0]:
            return []

        for i, chunk_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            text = results["documents"][0][i]
            distance = results["distances"][0][i]
            similarity = round(1 - (distance / 2), 4)

            search_results.append(SearchResult(
                chunk_id=chunk_id,
                text=text,
                document_id=metadata["document_id"],
                page_number=metadata["page_number"],
                chunk_index=metadata["chunk_index"],
                similarity_score=similarity,
            ))

        logger.info(f"'{query[:50]}' icin {len(search_results)} sonuc bulundu.")
        return search_results

    def delete_by_document(self, document_id: int) -> None:
        """Bir dokumana ait tum chunklari siler."""
        try:
            existing = self._collection.get(where={"document_id": document_id})
            if existing and existing["ids"]:
                logger.info(f"document_id={document_id}: {len(existing['ids'])} eski chunk siliniyor...")
                ids = existing["ids"]
                batch_size = 100
                for i in range(0, len(ids), batch_size):
                    self._collection.delete(ids=ids[i:i + batch_size])
        except Exception as e:
            logger.warning(f"Eski chunk silerken hata (devam ediliyor): {e}")

    def get_chunk_count(self) -> int:
        return self._collection.count()


_singleton: Optional[VectorStore] = None


def get_vector_store(persist_dir: str = "./chroma_db") -> VectorStore:
    """
    Paylasilan VectorStore ornegini dondurur (process icinde tek sefer kurulur).

    VectorStore her kurulusta embedding modelini belleğe yukler; bu islem ilk
    seferinde saniyeler surebilir (bkz. main.py startup - modeli onceden isitir).
    Her istekte yeni VectorStore olusturmak bu maliyeti tekrar tekrar odetir ve
    ChromaDB baglantisini gereksiz yere yeniden acar; bu yuzden tek instance
    process boyunca paylasilir.
    """
    global _singleton
    if _singleton is None:
        _singleton = VectorStore(persist_dir)
    return _singleton
