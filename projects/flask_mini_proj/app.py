"""
PTSD Companion — Flask API + React static frontend.

Runtime architecture (primary):
    React → Flask → boto3 bedrock-agent-runtime.invoke_agent()
         → Bedrock Agent → Knowledge Base (S3) → Lambda Action Groups → response

Local FAISS (rag_engine.py) is legacy/optional only — NOT used by /api/chat.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

import chat_store
from agent_engine import AGENT_CONFIG_ERROR, answer_with_agent, is_agent_configured
from documents import DocumentError, save_upload
from kb_status import get_knowledge_base_status, list_s3_documents
from response_utils import api_error, detect_locale, sanitize_agent_answer
from tasks import (
    TasksError,
    TasksFileError,
    add_task,
    delete_task,
    extract_tasks_from_text,
    get_all_tasks,
    get_tasks_path,
    update_task,
)
from tools import (
    build_weekly_snapshot_payload,
    invoke_emergency_call,
    invoke_stress_check_in,
    invoke_weekly_snapshot,
)
from json_utils import json_safe
from weekly_context import (
    build_weekly_app_context,
    format_weekly_app_context_block,
    is_task_context_request,
    is_weekly_snapshot_request,
    should_inject_app_context,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("ptsd.app")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static", "dist")
MAX_MESSAGE_LENGTH = 8000
LEGACY_FAISS = os.getenv("ENABLE_LEGACY_FAISS", "false").lower() in ("1", "true", "yes")


def _log_startup() -> None:
    kb = get_knowledge_base_status()
    logger.info(
        "[app] startup | runtime=bedrock_agent_kb agent=%s kb=%s s3=%s legacy_faiss=%s",
        kb["agent_configured"],
        kb["knowledge_base_configured"],
        kb["s3_bucket_configured"],
        LEGACY_FAISS,
    )


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")

    chat_store.init_db()
    _log_startup()

    # --- Health & status ---

    @app.route("/health")
    def health():
        kb = get_knowledge_base_status()
        return jsonify({
            "status": "ok",
            "service": "PTSD Companion",
            "runtime_mode": kb["runtime_mode"],
            "agent_configured": kb["agent_configured"],
            "knowledge_base_configured": kb["knowledge_base_configured"],
        })

    @app.route("/api/knowledge-base/status")
    def api_kb_status():
        kb = get_knowledge_base_status()
        s3_files, _ = list_s3_documents() if kb["s3_bucket_configured"] else ([], None)
        return jsonify({"status": "success", **kb, "s3_documents": s3_files})

    # --- Conversations (app-level memory) ---

    @app.route("/api/conversations", methods=["GET"])
    def api_conversations_list():
        return jsonify({
            "conversations": chat_store.list_conversations(),
            "status": "success",
        })

    @app.route("/api/conversations", methods=["POST"])
    def api_conversations_create():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "שיחה חדשה").strip()
        conv = chat_store.create_conversation(title=title)
        return jsonify({"conversation": conv, "status": "success"}), 201

    @app.route("/api/conversations/<conversation_id>", methods=["GET"])
    def api_conversations_get(conversation_id):
        conv = chat_store.get_conversation(conversation_id)
        if not conv:
            body, code = api_error("שיחה לא נמצאה.", code=404)
            return jsonify(body), code
        return jsonify({"conversation": conv, "status": "success"})

    @app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
    def api_conversations_delete(conversation_id):
        if chat_store.delete_conversation(conversation_id):
            return jsonify({"message": "השיחה נמחקה.", "status": "success"})
        body, code = api_error("שיחה לא נמצאה.", code=404)
        return jsonify(body), code

    # --- Chat (Bedrock Agent — primary path) ---

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or data.get("question") or "").strip()

        if not message:
            body, code = api_error("נא להזין שאלה.", code=400)
            return jsonify(body), code

        if len(message) > MAX_MESSAGE_LENGTH:
            message = message[:MAX_MESSAGE_LENGTH]

        if not is_agent_configured():
            body, code = api_error(AGENT_CONFIG_ERROR, code=503)
            return jsonify(body), code

        conversation_id = (data.get("conversation_id") or "").strip()
        if not conversation_id:
            conv = chat_store.create_conversation(
                title=message[:60] + ("…" if len(message) > 60 else "")
            )
            conversation_id = conv["conversation_id"]
        elif not chat_store.get_conversation(conversation_id):
            body, code = api_error("שיחה לא נמצאה.", code=404)
            return jsonify(body), code

        conv = chat_store.get_conversation(conversation_id)
        agent_session_id = conv.get("agent_session_id") if conv else None
        memory_context = chat_store.get_recent_messages(conversation_id, limit=6)

        chat_store.add_message(conversation_id, "user", message)

        locale = detect_locale(message)
        weekly = is_weekly_snapshot_request(message)
        task_context = is_task_context_request(message)
        agent_input = message
        context_meta: dict = {}

        if should_inject_app_context(message):
            lang = "en" if locale == "en" else "he"
            ctx = build_weekly_app_context(conversation_id, language=lang)
            context_meta = {
                "tasks_path": ctx.get("tasks_path"),
                "tasks_file_exists": ctx.get("tasks_file_exists"),
                "completed_tasks_count": ctx.get("completed_tasks_count"),
                "open_tasks_count": ctx.get("open_tasks_count"),
                "recent_topics": ctx.get("recent_topics"),
            }
            agent_input = message + format_weekly_app_context_block(ctx)

        logger.info(
            "[app] chat | conv=%s locale=%s backend=bedrock_agent weekly=%s task_context=%s "
            "tasks_path=%s tasks_file_exists=%s completed_tasks_count=%s open_tasks_count=%s "
            "recent_topics=%s app_context_appended=%s final_agent_input_len=%s",
            conversation_id[:12],
            locale,
            weekly,
            task_context,
            context_meta.get("tasks_path", get_tasks_path() if should_inject_app_context(message) else "-"),
            context_meta.get("tasks_file_exists", False),
            context_meta.get("completed_tasks_count", 0),
            context_meta.get("open_tasks_count", 0),
            context_meta.get("recent_topics", []),
            agent_input != message,
            len(agent_input),
        )

        result = answer_with_agent(
            message=agent_input,
            conversation_id=conversation_id,
            memory_context=memory_context,
            agent_session_id=agent_session_id,
        )

        if result.get("status") != "success":
            return jsonify({
                "status": "error",
                "error": result.get("message", "שגיאה ב-Agent"),
                "conversation_id": conversation_id,
            }), 503

        answer = sanitize_agent_answer(result["answer"], message, locale)
        chat_store.add_message(conversation_id, "assistant", answer)
        chat_store.update_conversation_summary(
            conversation_id,
            last_user_question=message,
            last_assistant_answer=answer,
            title=message[:60] + ("…" if len(message) > 60 else ""),
        )

        return jsonify(json_safe({
            "status": "success",
            "answer": answer,
            "conversation_id": conversation_id,
            "agent_session_id": result.get("agent_session_id"),
            "last_user_question": message,
            "sources": result.get("sources", []),
            "tool_calls": result.get("tool_calls", []),
            "trace_summary": result.get("trace_summary", []),
            "locale": locale,
        }))

    @app.route("/api/clear", methods=["POST"])
    def api_clear():
        data = request.get_json(silent=True) or {}
        cid = (data.get("conversation_id") or "").strip()
        if cid and chat_store.delete_conversation(cid):
            return jsonify({"message": "השיחה נמחקה.", "status": "success"})
        return jsonify({"message": "אין שיחה פעילה.", "status": "success"})

    # --- MCP-style tools (optional direct Lambda demo endpoints) ---

    @app.route("/api/tools/weekly-snapshot", methods=["POST"])
    def api_weekly_snapshot():
        data = request.get_json(silent=True) or {}
        language = (data.get("language") or "he").strip()
        try:
            tasks = get_all_tasks()
        except TasksFileError as exc:
            body, code = api_error(str(exc), code=500)
            return jsonify(body), code
        payload = data if data.get("completed_tasks") else build_weekly_snapshot_payload(tasks, language)
        result = invoke_weekly_snapshot(payload)
        return jsonify({"status": "success", "snapshot": result})

    @app.route("/api/tools/stress-check-in", methods=["POST"])
    def api_stress_check_in():
        """Demo only — normal chat uses Agent Action Group via invoke_agent."""
        data = request.get_json(silent=True) or {}
        result = invoke_stress_check_in(data)
        code = 200 if result.get("classification") else 400
        return jsonify({"status": "success", "classifier": result}), code

    @app.route("/api/tools/emergency-call", methods=["POST"])
    def api_emergency_call():
        data = request.get_json(silent=True) or {}
        if not data.get("confirmed"):
            return jsonify({
                "status": "confirmation_required",
                "message": (
                    "Emergency contact call requires explicit user confirmation. "
                    "שיחת חירום דורשת אישור מפורש מהמשתמש."
                ),
            }), 400
        result = invoke_emergency_call(data)
        code = 200 if result.get("status") in ("call_started", "success") else 400
        return jsonify({"status": "success", "result": result}), code

    # --- Tasks ---

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
            return jsonify({"tasks": added, "count": len(added), "status": "success"})
        except TasksError as exc:
            body, code = api_error(str(exc), code=400)
            return jsonify(body), code
        except ValueError as exc:
            body, code = api_error(str(exc), code=503)
            return jsonify(body), code
        except Exception:
            body, code = api_error("שגיאה בחילוץ משימות. נסה שוב מאוחר יותר.", code=500)
            return jsonify(body), code

    # --- Documents (S3 + KB status; legacy FAISS optional) ---

    @app.route("/api/documents", methods=["GET"])
    def api_documents_list():
        kb = get_knowledge_base_status()
        s3_files, s3_err = list_s3_documents() if kb["s3_bucket_configured"] else ([], None)
        payload = {
            "status": "success",
            "runtime_mode": kb["runtime_mode"],
            "knowledge_base": kb,
            "s3_documents": s3_files,
            "s3_error": s3_err,
        }
        if LEGACY_FAISS:
            try:
                from rag_engine import get_index_status, scan_data_files

                payload["legacy_faiss"] = {
                    "enabled": True,
                    "index": get_index_status(),
                    "local_files": scan_data_files(),
                }
            except Exception as exc:  # noqa: BLE001
                payload["legacy_faiss"] = {"enabled": True, "error": str(exc)}
        return jsonify(payload)

    @app.route("/api/documents/upload", methods=["POST"])
    def api_documents_upload():
        if "file" not in request.files:
            body, code = api_error("לא התקבל קובץ.", code=400)
            return jsonify(body), code
        try:
            doc = save_upload(request.files["file"])
        except DocumentError as exc:
            body, code = api_error(str(exc), code=400)
            return jsonify(body), code
        except Exception:
            body, code = api_error("שגיאה בהעלאת הקובץ. נסה שוב.", code=500)
            return jsonify(body), code

        return jsonify({
            "document": doc,
            "message": (
                "הקובץ נשמר מקומית. ל-RAG בפרודקשן: העלה ל-S3 והפעל סנכרון Knowledge Base."
            ),
            "indexing_status": "s3_kb_sync_required",
            "status": "success",
        }), 201

    # Legacy FAISS endpoints (optional, disabled by default)
    if LEGACY_FAISS:
        from rag_engine import get_index_status, rebuild_index

        @app.route("/api/index/status", methods=["GET"])
        def api_index_status():
            return jsonify({"index": get_index_status(), "status": "success", "legacy": True})

        @app.route("/api/index/rebuild", methods=["POST"])
        def api_index_rebuild():
            try:
                result = rebuild_index()
                return jsonify({
                    "message": f"Legacy FAISS rebuilt ({result.get('chunk_count', 0)} chunks).",
                    "result": result,
                    "index": get_index_status(),
                    "status": "success",
                    "legacy": True,
                })
            except Exception as exc:  # noqa: BLE001
                body, code = api_error(str(exc), code=500)
                return jsonify(body), code

    # --- React SPA ---

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(os.path.join(STATIC_DIR, "assets"), filename)

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
