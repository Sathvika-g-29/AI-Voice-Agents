from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(
    os.getenv("HUMAN_HELP_DB_PATH", Path(__file__).resolve().parent.parent / "human_help.db")
)
EXPORT_PATH = Path(
    os.getenv(
        "HUMAN_HELP_EXPORT_PATH",
        Path(__file__).resolve().parent.parent / "human_help_requests.json",
    )
)

ALLOWED_URGENCIES = {"low", "medium", "high", "emergency"}


@dataclass(frozen=True)
class HumanHelpRequest:
    request_id: str
    created_at: str
    status: str
    requester_name: str
    issue: str
    what_checked: str
    urgency: str
    language: str
    follow_up_method: str
    summary: str
    dedupe_key: str


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS human_help_requests (
            request_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            requester_name TEXT NOT NULL,
            issue TEXT NOT NULL,
            what_checked TEXT NOT NULL,
            urgency TEXT NOT NULL,
            language TEXT NOT NULL,
            follow_up_method TEXT NOT NULL,
            summary TEXT NOT NULL,
            dedupe_key TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.commit()
    conn.close()
    export_requests()


def normalize_urgency(urgency: str) -> str:
    value = (urgency or "medium").strip().lower()
    if value not in ALLOWED_URGENCIES:
        return "medium"
    return value


def build_summary(
    requester_name: str,
    issue: str,
    what_checked: str,
    urgency: str,
    language: str,
    follow_up_method: str,
) -> str:
    pieces = [
        f"Who needs help: {requester_name or 'the caller'}",
        f"What happened: {issue.strip()}",
        f"What the agent already checked: {what_checked.strip() or 'nothing yet'}",
        f"How urgent it is: {normalize_urgency(urgency)}",
        f"Caller language: {language.strip() or 'not specified'}",
        f"Preferred follow-up: {follow_up_method.strip() or 'not specified'}",
    ]
    return " | ".join(pieces)


def _dedupe_key(
    requester_name: str,
    issue: str,
    what_checked: str,
    urgency: str,
    language: str,
    follow_up_method: str,
) -> str:
    normalized = "|".join(
        [
            requester_name.strip().lower(),
            issue.strip().lower(),
            what_checked.strip().lower(),
            normalize_urgency(urgency),
            language.strip().lower(),
            follow_up_method.strip().lower(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def list_requests() -> list[dict[str, str]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT request_id, created_at, status, requester_name, issue, what_checked,
               urgency, language, follow_up_method, summary, dedupe_key
        FROM human_help_requests
        ORDER BY created_at DESC
        """
    ).fetchall()
    conn.close()
    return [
        {
            "request_id": row[0],
            "created_at": row[1],
            "status": row[2],
            "requester_name": row[3],
            "issue": row[4],
            "what_checked": row[5],
            "urgency": row[6],
            "language": row[7],
            "follow_up_method": row[8],
            "summary": row[9],
            "dedupe_key": row[10],
        }
        for row in rows
    ]


def export_requests() -> None:
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(
        json.dumps(list_requests(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_human_help_request(
    *,
    requester_name: str,
    issue: str,
    what_checked: str,
    urgency: str = "medium",
    language: str = "",
    follow_up_method: str = "",
    permission_granted: bool = False,
) -> HumanHelpRequest:
    if not permission_granted:
        raise ValueError("Permission must be granted before sharing caller details.")

    normalized_urgency = normalize_urgency(urgency)
    summary = build_summary(
        requester_name=requester_name,
        issue=issue,
        what_checked=what_checked,
        urgency=normalized_urgency,
        language=language,
        follow_up_method=follow_up_method,
    )
    dedupe_key = _dedupe_key(
        requester_name=requester_name,
        issue=issue,
        what_checked=what_checked,
        urgency=normalized_urgency,
        language=language,
        follow_up_method=follow_up_method,
    )
    created_at = datetime.now(timezone.utc).isoformat()
    request_id = f"HR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    conn = get_connection()
    existing = conn.execute(
        """
        SELECT request_id, created_at, status, requester_name, issue, what_checked,
               urgency, language, follow_up_method, summary, dedupe_key
        FROM human_help_requests
        WHERE dedupe_key = ? AND status != 'resolved'
        """,
        (dedupe_key,),
    ).fetchone()

    if existing:
        conn.close()
        export_requests()
        return HumanHelpRequest(
            request_id=existing[0],
            created_at=existing[1],
            status=existing[2],
            requester_name=existing[3],
            issue=existing[4],
            what_checked=existing[5],
            urgency=existing[6],
            language=existing[7],
            follow_up_method=existing[8],
            summary=existing[9],
            dedupe_key=existing[10],
        )

    request = HumanHelpRequest(
        request_id=request_id,
        created_at=created_at,
        status="open",
        requester_name=requester_name.strip() or "unknown",
        issue=issue.strip(),
        what_checked=what_checked.strip(),
        urgency=normalized_urgency,
        language=language.strip(),
        follow_up_method=follow_up_method.strip(),
        summary=summary,
        dedupe_key=dedupe_key,
    )

    conn.execute(
        """
        INSERT INTO human_help_requests
        (request_id, created_at, status, requester_name, issue, what_checked, urgency,
         language, follow_up_method, summary, dedupe_key)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.request_id,
            request.created_at,
            request.status,
            request.requester_name,
            request.issue,
            request.what_checked,
            request.urgency,
            request.language,
            request.follow_up_method,
            request.summary,
            request.dedupe_key,
        ),
    )
    conn.commit()
    conn.close()
    export_requests()
    return request


def mark_request_status(request_id: str, status: str) -> None:
    normalized_status = status.strip().lower()
    conn = get_connection()
    conn.execute(
        """
        UPDATE human_help_requests
        SET status = ?
        WHERE request_id = ?
        """,
        (normalized_status, request_id),
    )
    conn.commit()
    conn.close()
    export_requests()
