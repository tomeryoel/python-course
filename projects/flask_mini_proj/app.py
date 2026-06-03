"""
PTSD Companion — Flask API + React static frontend.
"""

from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session

from memory import clear_conversation, get_conversation_history, init_db, save_message
from rag_engine import answer_question
from tasks import (
    TasksError,
    TasksFileError,
    add_task,
    delete_task,
    extract_tasks_from_text,
    get_all_tasks,
    update_task,
)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static", "dist")
MAX_QUESTION_LENGTH = 8000


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")

    init_db()

    @app.before_request
    def ensure_session_id():
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())

    # --- API ---

    @app.route("/health")
    def health():
        kb = os.getenv("KNOWLEDGE_BASE_ID", "")
        return jsonify({
            "status": "ok",
            "service": "PTSD Companion",
            "knowledge_base_configured": bool(kb),
        })

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.get_json(silent=True) or {}
        question = (data.get("question") or "").strip()

        if not question:
            return jsonify({
                "error": "נא להזין שאלה.",
                "status": "error",
            }), 400

        if len(question) > MAX_QUESTION_LENGTH:
            question = question[:MAX_QUESTION_LENGTH]

        session_id = session["session_id"]
        history = get_conversation_history(session_id)
        save_message(session_id, "user", question)

        try:
            result = answer_question(question=question, conversation_history=history)
        except ValueError as exc:
            return jsonify({
                "answer": str(exc),
                "sources": [],
                "retrieved_context": "",
                "status": "error",
            }), 503

        answer = result.get("answer", "")
        save_message(session_id, "assistant", answer)

        return jsonify({
            "answer": answer,
            "sources": result.get("sources", []),
            "retrieved_context": result.get("retrieved_context", ""),
            "status": result.get("status", "success"),
        })

    @app.route("/api/clear", methods=["POST"])
    def api_clear():
        clear_conversation(session["session_id"])
        return jsonify({"message": "השיחה נמחקה.", "status": "success"})

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks_list():
        try:
            return jsonify({"tasks": get_all_tasks(), "status": "success"})
        except TasksFileError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 500

    @app.route("/api/tasks", methods=["POST"])
    def api_tasks_create():
        data = request.get_json(silent=True) or {}
        try:
            task = add_task(data)
            return jsonify({"task": task, "status": "success"}), 201
        except TasksError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 400
        except TasksFileError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 500

    @app.route("/api/tasks/<task_id>", methods=["PATCH"])
    def api_tasks_patch(task_id):
        data = request.get_json(silent=True) or {}
        try:
            task = update_task(task_id, data)
            return jsonify({"task": task, "status": "success"})
        except TasksError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 404
        except TasksFileError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 500

    @app.route("/api/tasks/<task_id>", methods=["DELETE"])
    def api_tasks_delete(task_id):
        try:
            delete_task(task_id)
            return jsonify({"message": "נמחק.", "status": "success"})
        except TasksError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 404
        except TasksFileError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 500

    @app.route("/api/extract-tasks", methods=["POST"])
    def api_extract_tasks():
        data = request.get_json(silent=True) or {}
        document_text = (data.get("document_text") or "").strip()
        source_name = (data.get("source_name") or "סיכום קליני").strip()
        if not document_text:
            return jsonify({"error": "טקסט המסמך ריק.", "status": "error"}), 400
        try:
            added = extract_tasks_from_text(document_text, source_name)
            return jsonify({
                "tasks": added,
                "count": len(added),
                "status": "success",
            })
        except TasksError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 400
        except ValueError as exc:
            return jsonify({"error": str(exc), "status": "error"}), 503
        except Exception as exc:
            return jsonify({"error": str(exc), "status": "error"}), 500

    # --- React SPA ---

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        folder = os.path.join(STATIC_DIR, "assets")
        return send_from_directory(folder, filename)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/") or path == "health":
            return jsonify({"error": "Not found"}), 404
        if path and os.path.isfile(os.path.join(STATIC_DIR, path)):
            return send_from_directory(STATIC_DIR, path)
        index = os.path.join(STATIC_DIR, "index.html")
        if os.path.isfile(index):
            return send_from_directory(STATIC_DIR, "index.html")
        return (
            "<p>Frontend not built. Run: <code>cd frontend && npm install && npm run build</code></p>",
            503,
        )

    if not debug:
        app.config["PROPAGATE_EXCEPTIONS"] = False

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=debug)
