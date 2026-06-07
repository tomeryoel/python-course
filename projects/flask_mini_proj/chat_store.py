"""
Persistent app-level chat memory (SQLite).

Stores conversations and messages for the React UI: previous chats, titles,
last question/answer, and the stable Bedrock Agent sessionId per conversation.
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("CHAT_DB_PATH", os.path.join(BASE_DIR, "chat_memory.db"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _messages_has_conversation_id(cur: sqlite3.Cursor) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
    )
    if not cur.fetchone():
        return False
    cols = {row[1] for row in cur.execute("PRAGMA table_info(messages)")}
    return "conversation_id" in cols


def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    if not _messages_has_conversation_id(cur):
        cur.execute("DROP TABLE IF EXISTS messages")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            title TEXT,
            last_user_question TEXT,
            last_assistant_answer TEXT,
            agent_session_id TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
        )
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, created_at)"
    )
    conn.commit()
    conn.close()


def create_conversation(title: str | None = None) -> dict[str, Any]:
    cid = f"conv_{uuid.uuid4().hex[:12]}"
    agent_sid = f"agent-{uuid.uuid4().hex}"
    now = _now()
    conn = _connect()
    conn.execute(
        """INSERT INTO conversations
           (conversation_id, created_at, updated_at, title, agent_session_id)
           VALUES (?, ?, ?, ?, ?)""",
        (cid, now, now, title or "שיחה חדשה", agent_sid),
    )
    conn.commit()
    conn.close()
    return get_conversation(cid)


def list_conversations(limit: int = 50) -> list[dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        """SELECT conversation_id, created_at, updated_at, title,
                  last_user_question, last_assistant_answer, agent_session_id
           FROM conversations ORDER BY updated_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    if not row:
        conn.close()
        return None
    msgs = conn.execute(
        """SELECT message_id, role, content, created_at
           FROM messages WHERE conversation_id = ? ORDER BY created_at ASC""",
        (conversation_id,),
    ).fetchall()
    conn.close()
    conv = dict(row)
    conv["messages"] = [dict(m) for m in msgs]
    return conv


def get_agent_session_id(conversation_id: str) -> str:
    conv = get_conversation(conversation_id)
    if conv and conv.get("agent_session_id"):
        return conv["agent_session_id"]
    sid = f"agent-{uuid.uuid4().hex}"
    conn = _connect()
    conn.execute(
        "UPDATE conversations SET agent_session_id = ? WHERE conversation_id = ?",
        (sid, conversation_id),
    )
    conn.commit()
    conn.close()
    return sid


def add_message(conversation_id: str, role: str, content: str) -> dict[str, Any]:
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    now = _now()
    conn = _connect()
    conn.execute(
        """INSERT INTO messages (message_id, conversation_id, role, content, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (mid, conversation_id, role, content, now),
    )
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE conversation_id = ?",
        (now, conversation_id),
    )
    conn.commit()
    conn.close()
    return {"message_id": mid, "role": role, "content": content, "created_at": now}


def update_conversation_summary(
    conversation_id: str,
    last_user_question: str,
    last_assistant_answer: str,
    title: str | None = None,
) -> None:
    now = _now()
    conn = _connect()
    if title:
        conn.execute(
            """UPDATE conversations SET updated_at = ?, last_user_question = ?,
               last_assistant_answer = ?, title = ? WHERE conversation_id = ?""",
            (now, last_user_question, last_assistant_answer, title, conversation_id),
        )
    else:
        conn.execute(
            """UPDATE conversations SET updated_at = ?, last_user_question = ?,
               last_assistant_answer = ? WHERE conversation_id = ?""",
            (now, last_user_question, last_assistant_answer, conversation_id),
        )
    conn.commit()
    conn.close()


def get_recent_messages(conversation_id: str, limit: int = 6) -> list[dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        """SELECT role, content FROM messages
           WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?""",
        (conversation_id, limit),
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def delete_conversation(conversation_id: str) -> bool:
    conn = _connect()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    cur = conn.execute(
        "DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,)
    )
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted
