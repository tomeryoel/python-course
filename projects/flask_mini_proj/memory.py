"""
LEGACY — superseded by chat_store.py (SQLite conversations + messages).

This module used an older messages-only schema (session_id). Do not import
for new code. Kept only for reference during migration.
"""

import sqlite3
from datetime import datetime

DB_NAME = "chat_memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_message(session_id, role, message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (session_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, message, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_conversation_history(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()

    conn.close()

    history = []

    for role, message in rows:
        history.append({
            "role": role,
            "message": message
        })

    return history


def clear_conversation(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()
