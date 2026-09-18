from fastapi import FastAPI
from app.database.connection import Base, engine
from app.models import subject, document, syllabus, question, concept, pattern, generated_question, user  # noqa
from app.api import subjects, documents, analysis, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Question Generation Engine")

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(analysis.router)

@app.get("/")
def root():
    return {"status": "ok"}