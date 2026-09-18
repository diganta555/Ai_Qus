from app.database.connection import SessionLocal
from app.models.subject import Subject   # needed so SQLAlchemy can resolve the FK
from app.models.document import Document

db = SessionLocal()
doc = db.query(Document).filter(Document.id == 10).first()

if doc:
    print("Deleting:", doc.file_name, doc.document_type)
    db.delete(doc)
    db.commit()
    print("Done.")
else:
    print("No document with id=10 found")

db.close()