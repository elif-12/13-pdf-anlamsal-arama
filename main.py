"""
PDF Semantic Search ("Anlamsal Ctrl+F")
Ana uygulama dosyasi. Buradan baslatilir.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from src.api.routes.documents_router import router as documents_router
from src.infrastructure.database.connection import create_tables

app = FastAPI(
    title="PDF Semantic Search",
    description="PDF icinde anlamsal arama yapan Ctrl+F benzeri arac",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)


@app.on_event("startup")
def startup():
    logger.info("Uygulama baslatiliyor...")
    create_tables()
    logger.info("PDF Semantic Search hazir!")


@app.get("/")
def root():
    return FileResponse("ui.html")


@app.get("/health")
def health():
    return {"status": "healthy"}
