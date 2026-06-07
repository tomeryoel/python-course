import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / "aws" / "lambda" / "weekly_wellness_snapshot"
EMERGENCY = ROOT / "aws" / "lambda" / "emergency_contact_voice_call"


def _load_lambda_module(directory: Path, module_name: str):
    path = directory / "lambda_function.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_weekly_snapshot_lambda_direct():
    weekly = _load_lambda_module(WEEKLY, "weekly_wellness_snapshot_lambda")
    with open(WEEKLY / "test_event.json", encoding="utf-8") as f:
        event = json.load(f)
    resp = weekly.lambda_handler(event, None)
    body = json.loads(resp["body"]) if "body" in resp else resp
    assert body.get("week_summary")
    assert body.get("completed_tasks") == 3


def test_emergency_call_requires_confirmation():
    emergency = _load_lambda_module(EMERGENCY, "emergency_contact_voice_call_lambda")
    resp = emergency.lambda_handler({"confirmed": False}, None)
    body = json.loads(resp["body"])
    assert body["status"] == "confirmation_required"
