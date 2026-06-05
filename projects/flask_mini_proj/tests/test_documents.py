import io
import json
import os

import pytest

from documents import DocumentError, list_documents, save_upload


@pytest.fixture
def isolated_docs(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    registry = tmp_path / "registry.json"
    monkeypatch.setattr("documents.UPLOAD_DIR", str(upload_dir))
    monkeypatch.setattr("documents.REGISTRY_PATH", str(registry))
    return upload_dir, registry


def test_upload_pdf(isolated_docs):
    data = b"%PDF-1.4 fake"
    f = io.BytesIO(data)
    f.filename = "test.pdf"

    class FakeFile:
        filename = "test.pdf"

        def seek(self, pos, whence=0):
            f.seek(pos, whence)

        def tell(self):
            return f.tell()

        def save(self, path):
            with open(path, "wb") as out:
                out.write(data)

    doc = save_upload(FakeFile())
    assert doc["type"] == "PDF"
    assert doc["status"] == "uploaded"
    assert len(list_documents()) == 1


def test_upload_rejects_invalid_extension(isolated_docs):
    class FakeFile:
        filename = "virus.exe"

        def seek(self, *a, **k):
            pass

        def tell(self):
            return 10

        def save(self, path):
            pass

    with pytest.raises(DocumentError):
        save_upload(FakeFile())
