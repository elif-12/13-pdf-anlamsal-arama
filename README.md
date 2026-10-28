# PDF Semantic Search

PDF'ler icin anlamsal arama araci — kisaca, **Ctrl+F'in anlamsal hali**.

Klasik Ctrl+F sadece birebir ayni kelimeyi bulur. Bu arac yerine "ne aradigini"
dogal dilde yazarsin (orn. *"motor bakim periyodu nedir"*), PDF'teki en yakin
anlamli bolumleri sayfa numarasiyla birlikte getirir ve o sayfada ilgili
metni gorsel olarak vurgular.

## Nasil calisir

1. PDF yuklenir -> metni sayfa sayfa cikarilir (PyMuPDF).
2. Metin kucuk parcalara (chunk) bolunur.
3. Her parca bir embedding vektorune cevrilir ve ChromaDB'ye kaydedilir
   (yerel/ucretsiz `sentence-transformers` modeli — API key gerekmez).
4. Arama sorgusu da vektore cevrilir, en yakin parcalar kosinus benzerligine
   gore siralanir.
5. Arayuz, en alakali sonuca tikladiginda PDF'i o sayfaya gotirur ve
   eslesen metni vurgular.

## Ozellikler
- Dogal dilde sorguyla PDF icinde anlamsal arama
- Sonuc -> sayfaya atlama + metin vurgulama (tarayicida, pdf.js ile)
- Birden fazla PDF yukleyip aralarinda gecis yapma
- Clean Architecture + Repository Pattern (domain / application / infrastructure / api / rag)
- FastAPI REST API, SQLite (doküman metadata), ChromaDB (vektorler)
- Unit testler (chunker, entity)

## Kurulum

### 1. Gereksinimler
- Python 3.10+

### 2. Projeyi kur
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

İlk calistirmada `sentence-transformers` embedding modelini (~90MB) bir kere
indirir, sonrasinda internet gerekmez.

### 3. Calistir
```bash
python -m uvicorn main:app --reload
```

Tarayicida ac: http://127.0.0.1:8000

### 4. API dokumantasyonu
```
http://127.0.0.1:8000/docs
```

## Testleri calistir
```bash
python -m pytest tests/ -v
```

## Proje yapisi
```
pdf-semantic-search/
├── src/
│   ├── domain/          # Document entity, repository interface
│   ├── infrastructure/  # SQLAlchemy ORM, repository implementasyonu
│   ├── application/     # SearchService (yukleme + arama is mantigi)
│   ├── api/             # FastAPI route'lari
│   └── rag/             # PDF okuma, chunking, ChromaDB vektor arama
├── tests/               # Unit testler
├── uploads/             # Yuklenen PDF'ler (git'e girmez)
├── ui.html              # Tek sayfalik arayuz (pdf.js ile PDF goruntuleme + vurgulama)
└── main.py              # Uygulama giris noktasi
```

## API ozeti
| Method | Endpoint | Aciklama |
|---|---|---|
| POST | `/api/documents/upload` | PDF yukle ve indeksle |
| GET | `/api/documents/` | Yuklenen dokumanlari listele |
| GET | `/api/documents/{id}` | Doküman detayi |
| GET | `/api/documents/{id}/file` | Ham PDF dosyasi (goruntuleyici icin) |
| POST | `/api/documents/{id}/search` | Dokuman icinde anlamsal arama |
| DELETE | `/api/documents/{id}` | Dokumani ve vektorlerini sil |

## Notlar
- Bu proje, [aerospace_compliance](../aerospace_compliance) projesindeki RAG
  altyapisindan (PDF extractor, chunker, vector store) ilham alinarak, tek bir
  odaga (tek PDF icinde anlamsal Ctrl+F) indirgenerek yeniden yazilmistir.
  Standart/uyumluluk analizi, LLM tabanli karar verme gibi ozellikler bu
  projede yoktur — amaci sadece "bunu bul" demek.
