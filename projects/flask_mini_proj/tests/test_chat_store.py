"""Tests for chat_store SQLite persistence."""

import chat_store


def test_create_and_list_conversation(tmp_path, monkeypatch):
    db_path = tmp_path / "chat_memory.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()
    conv = chat_store.create_conversation(title="Test chat")
    assert conv["conversation_id"]
    chat_store.add_message(conv["conversation_id"], "user", "שלום")
    chat_store.add_message(conv["conversation_id"], "assistant", "היי")
    listed = chat_store.list_conversations()
    assert any(c["conversation_id"] == conv["conversation_id"] for c in listed)
    loaded = chat_store.get_conversation(conv["conversation_id"])
    assert len(loaded["messages"]) == 2
    chat_store.delete_conversation(conv["conversation_id"])
