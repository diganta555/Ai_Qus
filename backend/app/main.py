import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

if settings.hf_token:
    os.environ["HF_TOKEN"] = settings.hf_token

from app.database.connection import Base, engine
from app.models import subject, document, syllabus, question, concept, pattern, generated_question, user  # noqa
from app.api import subjects, documents, analysis, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Question Generation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(analysis.router)

@app.get("/")
def root():
    return {"status": "ok"}