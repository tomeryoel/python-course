"""
PTSD Companion — Flask API + React static frontend.
"""

from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session

from documents import DocumentError, list_documents, save_upload
from memory import clear_conversation, get_conversation_history, init_db, save_message
from rag_engine import answer_question
from response_utils import api_error, format_chat_response
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
            body, code = api_error("נא להזין שאלה.", code=400)
            return jsonify(body), code

        if len(question) > MAX_QUESTION_LENGTH:
            question = question[:MAX_QUESTION_LENGTH]

        session_id = session["session_id"]
        history = get_conversation_history(session_id)
        save_message(session_id, "user", question)

        try:
            result = answer_question(question=question, conversation_history=history)
        except ValueError as exc:
            return jsonify(format_chat_response({
                "answer": str(exc),
                "sources": [],
                "retrieved_context": "",
                "status": "error",
            }, question)), 503

        formatted = format_chat_response(result, question)
        save_message(session_id, "assistant", formatted.get("answer", ""))

        return jsonify(formatted)

    @app.route("/api/clear", methods=["POST"])
    def api_clear():
        clear_conversation(session["session_id"])
        return jsonify({"message": "השיחה נמחקה.", "status": "success"})

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks_list():
        try:
            return jsonify({"tasks": get_all_tasks(), "status": "success"})
        except TasksFileError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code

    @app.route("/api/tasks", methods=["POST"])
    def api_tasks_create():
        data = request.get_json(silent=True) or {}
        try:
            task = add_task(data)
            return jsonify({"task": task, "status": "success"}), 201
        except TasksError as exc:
            body, code = api_error(str(exc), code=400)
            return jsonify(body), code
        except TasksFileError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code

    @app.route("/api/tasks/<task_id>", methods=["PATCH"])
    def api_tasks_patch(task_id):
        data = request.get_json(silent=True) or {}
        try:
            task = update_task(task_id, data)
            return jsonify({"task": task, "status": "success"})
        except TasksError as exc:
            body, code = api_error(str(exc), code=404)
            return jsonify(body), code
        except TasksFileError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code

    @app.route("/api/tasks/<task_id>", methods=["DELETE"])
    def api_tasks_delete(task_id):
        try:
            delete_task(task_id)
            return jsonify({"message": "נמחק.", "status": "success"})
        except TasksError as exc:
            body, code = api_error(str(exc), code=404)
            return jsonify(body), code
        except TasksFileError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code

    @app.route("/api/extract-tasks", methods=["POST"])
    def api_extract_tasks():
        data = request.get_json(silent=True) or {}
        document_text = (data.get("document_text") or "").strip()
        source_name = (data.get("source_name") or "סיכום קליני").strip()
        if not document_text:
            body, code = api_error("טקסט המסמך ריק.", code=400)
            return jsonify(body), code
        try:
            added = extract_tasks_from_text(document_text, source_name)
            return jsonify({
                "tasks": added,
                "count": len(added),
                "status": "success",
            })
        except TasksError as exc:
            body, code = api_error(str(exc), code=400)
            return jsonify(body), code
        except ValueError as exc:
            body, code = api_error(str(exc), code=503)
            return jsonify(body), code
        except Exception:
            body, code = api_error("שגיאה בחילוץ משימות. נסה שוב מאוחר יותר.", code=500)
            return jsonify(body), code

    @app.route("/api/documents", methods=["GET"])
    def api_documents_list():
        try:
            docs = list_documents()
            return jsonify({"documents": docs, "status": "success"})
        except DocumentError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code

    @app.route("/api/documents/upload", methods=["POST"])
    def api_documents_upload():
        if "file" not in request.files:
            body, code = api_error("לא התקבל קובץ.", code=400)
            return jsonify(body), code
        try:
            doc = save_upload(request.files["file"])
            return jsonify({
                "document": doc,
                "message": "הקובץ נשמר. סנכרון ל-Knowledge Base יבוצע בהמשך.",
                "status": "success",
            }), 201
        except DocumentError as exc:
            body, code = api_error(str(exc), code=400)
            return jsonify(body), code
        except Exception:
            body, code = api_error("שגיאה בהעלאת הקובץ. נסה שוב.", code=500)
            return jsonify(body), code

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
