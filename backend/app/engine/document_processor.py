import pymupdf as fitz
import re


class DocumentProcessor:
    def extract_text(self, path: str) -> str:
        """Extract raw text from a PDF, page by page."""
        text_parts = []
        with fitz.open(path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "\n".join(text_parts)

    def clean_text(self, text: str) -> str:
        """Remove excess whitespace, page-break artifacts, etc."""
        text = re.sub(r"\n{3,}", "\n\n", text)       # collapse big gaps
        text = re.sub(r"[ \t]{2,}", " ", text)         # collapse repeated spaces
        text = re.sub(r"\x0c", "", text)                  # form-feed characters PyMuPDF inserts
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
        """Split cleaned text into overlapping chunks for embedding later."""
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def process(self, path: str) -> dict:
        """Full pipeline: extract → clean → chunk."""
        raw = self.extract_text(path)
        cleaned = self.clean_text(raw)
        chunks = self.chunk_text(cleaned)
        return {
            "raw_length": len(raw),
            "cleaned_length": len(cleaned),
            "num_chunks": len(chunks),
            "cleaned_text": cleaned,
            "chunks": chunks,
        }