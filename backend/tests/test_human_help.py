from pathlib import Path

import pytest

import human_help


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "human_help.db"
    export_path = tmp_path / "human_help_requests.json"
    monkeypatch.setattr(human_help, "DB_PATH", db_path)
    monkeypatch.setattr(human_help, "EXPORT_PATH", export_path)
    human_help.init_db()
    yield


def test_create_human_help_request_requires_permission() -> None:
    with pytest.raises(ValueError):
        human_help.create_human_help_request(
            requester_name="Asha",
            issue="Learner is upset",
            what_checked="I checked the learning dataset",
            permission_granted=False,
        )


def test_create_human_help_request_saves_short_summary() -> None:
    request = human_help.create_human_help_request(
        requester_name="Asha",
        issue="The learner is upset and wants a teacher",
        what_checked="I checked the local learning dataset and the request was unavailable",
        urgency="high",
        language="Telugu-English",
        follow_up_method="Phone call",
        permission_granted=True,
    )

    assert request.request_id.startswith("HR-")
    assert "Who needs help" in request.summary
    assert "How urgent it is: high" in request.summary

    requests = human_help.list_requests()
    assert len(requests) == 1
    assert requests[0]["request_id"] == request.request_id


def test_mark_request_status_updates_row() -> None:
    request = human_help.create_human_help_request(
        requester_name="Asha",
        issue="Need help from a teacher",
        what_checked="I checked the learning dataset",
        permission_granted=True,
    )

    human_help.mark_request_status(request.request_id, "in_progress")
    requests = human_help.list_requests()

    assert requests[0]["status"] == "in_progress"
