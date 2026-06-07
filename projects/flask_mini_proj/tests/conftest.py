import json
import os
import pytest


@pytest.fixture
def tasks_file(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    monkeypatch.setenv("TASKS_JSON_PATH", str(path))
    return path


@pytest.fixture
def chat_db(tmp_path, monkeypatch):
    db_path = tmp_path / "chat_memory.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    import chat_store

    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()
    return db_path


@pytest.fixture
def client(monkeypatch, tasks_file, chat_db):
    monkeypatch.setenv("KNOWLEDGE_BASE_ID", "TEST_KB_ID")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret")
    monkeypatch.delenv("FLASK_DEBUG", raising=False)

    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def sample_tasks(tasks_file):
    tasks = [
        {
            "id": "task_001",
            "title": "ציפרלקס",
            "description": "20:00",
            "category": "medication",
            "source": "test",
            "frequency": "daily",
            "time": "20:00",
            "status": "open",
            "safety_note": "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה.",
        }
    ]
    tasks_file.write_text(json.dumps(tasks, ensure_ascii=False), encoding="utf-8")
    return tasks
