import os
import pickle
import numpy as np
import faiss
from app.engine.embedding_model import get_embedding_model


class RAGEngine:
    def __init__(self, vectorstore_dir: str = "./storage/vectorstore"):
        self.vectorstore_dir = vectorstore_dir
        self.model = get_embedding_model()
        self.embedding_dim = 384

    def _subject_dir(self, subject_id: int) -> str:
        path = os.path.join(self.vectorstore_dir, f"subject_{subject_id}")
        os.makedirs(path, exist_ok=True)
        return path

    def _index_path(self, subject_id: int) -> str:
        return os.path.join(self._subject_dir(subject_id), "index.faiss")

    def _metadata_path(self, subject_id: int) -> str:
        return os.path.join(self._subject_dir(subject_id), "metadata.pkl")

    def build_index(self, subject_id: int, chunks: list[dict]) -> dict:
        if not chunks:
            raise ValueError("No chunks provided to build the knowledge base")

        texts = [c["text"] for c in chunks]
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)

        faiss.write_index(index, self._index_path(subject_id))

        metadata_list = [c["metadata"] for c in chunks]
        with open(self._metadata_path(subject_id), "wb") as f:
            pickle.dump({"metadata": metadata_list, "texts": texts}, f)

        counts: dict[str, int] = {}
        for m in metadata_list:
            src = m.get("document_type", "unknown")
            counts[src] = counts.get(src, 0) + 1

        return {
            "total_chunks_indexed": len(chunks),
            "breakdown": counts,
        }

    def load_index(self, subject_id: int):
        index_path = self._index_path(subject_id)
        metadata_path = self._metadata_path(subject_id)
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            return None, None, None
        index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            data = pickle.load(f)
        return index, data["metadata"], data["texts"]

    def retrieve(self, subject_id: int, query: str, top_k: int = 5) -> list[dict]:
        index, metadata_list, texts_list = self.load_index(subject_id)
        if index is None:
            raise ValueError("No knowledge base found for this subject — run build-knowledge-base first")

        query_embedding = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, indices = index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "text": texts_list[idx],
                "metadata": metadata_list[idx],
            })
        return results

    def retrieve_for_topic(self, subject_id: int, topic_name: str, top_k: int = 8) -> dict:
        all_results = self.retrieve(subject_id, topic_name, top_k=top_k * 3)

        academic_context = [
            r for r in all_results if r["metadata"].get("document_type") in ("study_material", "syllabus")
        ][:top_k]

        historical_pyqs = [
            r for r in all_results if r["metadata"].get("document_type") == "previous_year_question"
        ][:top_k]

        return {
            "topic": topic_name,
            "academic_context": academic_context,
            "historical_pyqs": historical_pyqs,
        }