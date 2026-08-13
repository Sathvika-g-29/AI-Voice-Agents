import json
from pathlib import Path

import pytest

import call_analytics


@pytest.fixture()
def analytics_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "call_analytics.db"
    export_path = tmp_path / "call_analytics.json"
    monkeypatch.setattr(call_analytics, "DB_PATH", db_path)
    monkeypatch.setattr(call_analytics, "EXPORT_PATH", export_path)
    call_analytics.init_db()
    return db_path, export_path


def test_records_successful_call(analytics_env) -> None:
    _, export_path = analytics_env

    tracker = call_analytics.start_call(
        channel="browser",
        participant_identity="sathvika",
        room_name="demo-room",
    )
    tracker.mark_success("learning recommendation delivered")
    record = tracker.finish()

    assert record.status == "successful"
    assert record.success_reason == "learning recommendation delivered"

    stats = call_analytics.get_stats()
    assert stats == {
        "total_calls": 1,
        "successful_calls": 1,
        "failed_calls": 0,
    }

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["stats"] == stats
    assert payload["recent_calls"][0]["status"] == "successful"
    assert "participant_identity" not in payload["recent_calls"][0]
    assert "room_name" not in payload["recent_calls"][0]


def test_records_failed_call(analytics_env) -> None:
    _, export_path = analytics_env

    tracker = call_analytics.start_call(
        channel="sip",
        participant_identity="anon",
        room_name="practice-room",
    )
    record = tracker.finish()

    assert record.status == "failed"
    assert record.success_reason == ""

    stats = call_analytics.get_stats()
    assert stats == {
        "total_calls": 1,
        "successful_calls": 0,
        "failed_calls": 1,
    }

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["stats"] == stats
    assert payload["recent_calls"][0]["status"] == "failed"
