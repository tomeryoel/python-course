"""
Verifies the local FAISS retrieval pipeline end-to-end WITHOUT torch/AWS.

A deterministic bag-of-words "fake embedder" stands in for sentence-transformers
so we can assert that chunking, index build/persist/load and top-k retrieval work.
"""

import numpy as np
import pytest

import rag_engine
from rag_engine import FaissRagEngine, chunk_documents, load_documents


class FakeEmbedder:
    """Hashing bag-of-words embedder → cosine similarity tracks word overlap."""

    backend = "fake"
    model_name = "fake-test-embedder"
    dim = 64

    def encode(self, texts):
        vectors = np.zeros((len(texts), self.dim), dtype="float32")
        for i, text in enumerate(texts):
            for token in text.lower().split():
                vectors[i, hash(token) % self.dim] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0:
                vectors[i] /= norm
        return vectors

    def fit_transform(self, texts):
        return self.encode(texts)

    def save(self):
        return None

    def load(self):
        return True


@pytest.fixture
def faiss_data(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sleep.txt").write_text(
        "המלצות שינה: להימנע מקפאין אחרי השעה שתיים בצהריים.\n\n"
        "לכבות מסכים בערב כדי לשפר את איכות השינה.",
        encoding="utf-8",
    )
    (data_dir / "grounding.txt").write_text(
        "תרגיל קרקוע חמש ארבע שלוש שתיים אחת לרגעים של פלאשבק ורעש חזק.",
        encoding="utf-8",
    )

    monkeypatch.setattr(rag_engine, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(rag_engine, "FAISS_INDEX_PATH", str(tmp_path / "idx.bin"))
    monkeypatch.setattr(rag_engine, "CHUNKS_PATH", str(tmp_path / "chunks.npy"))
    monkeypatch.setattr(rag_engine, "EMBEDDINGS_PATH", str(tmp_path / "emb.npy"))
    monkeypatch.setattr(rag_engine, "FAISS_META_PATH", str(tmp_path / "meta.json"))
    return data_dir


def test_load_and_chunk_documents(faiss_data):
    docs = load_documents(str(faiss_data))
    assert len(docs) == 2
    chunks = chunk_documents(docs)
    assert all("text" in c and "source" in c for c in chunks)


def test_build_and_retrieve(faiss_data):
    engine = FaissRagEngine.__new__(FaissRagEngine)
    engine.top_k = 2
    engine.embedder = FakeEmbedder()
    engine._index = None
    engine._chunks = []

    engine.ensure_index()
    results = engine.retrieve_chunks("קפאין שינה", k=1)
    assert results
    assert "שינה" in results[0]["text"] or "קפאין" in results[0]["text"]


def test_artifacts_persisted_and_reloaded(faiss_data):
    import os

    engine = FaissRagEngine.__new__(FaissRagEngine)
    engine.top_k = 2
    engine.embedder = FakeEmbedder()
    engine._index = None
    engine._chunks = []
    engine.ensure_index()

    assert os.path.isfile(rag_engine.FAISS_INDEX_PATH)
    assert os.path.isfile(rag_engine.FAISS_META_PATH)

    # A fresh engine should load persisted artifacts (no rebuild needed).
    engine2 = FaissRagEngine.__new__(FaissRagEngine)
    engine2.top_k = 2
    engine2.embedder = FakeEmbedder()
    engine2._index = None
    engine2._chunks = []
    engine2.ensure_index()
    assert engine2._chunks
