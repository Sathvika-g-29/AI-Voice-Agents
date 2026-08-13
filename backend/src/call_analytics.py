from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(
    os.getenv("CALL_ANALYTICS_DB_PATH", Path(__file__).resolve().parent.parent / "call_analytics.db")
)
EXPORT_PATH = Path(
    os.getenv(
        "CALL_ANALYTICS_EXPORT_PATH",
        Path(__file__).resolve().parent.parent / "call_analytics.json",
    )
)


@dataclass(frozen=True)
class CallRecord:
    call_id: str
    started_at: str
    ended_at: str
    duration_seconds: float
    status: str
    channel: str
    success_reason: str
    outcome_reason: str
    participant_identity: str
    room_name: str


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS call_analytics (
            call_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            status TEXT NOT NULL,
            channel TEXT NOT NULL,
            success_reason TEXT NOT NULL,
            outcome_reason TEXT NOT NULL,
            participant_identity TEXT NOT NULL,
            room_name TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    export_calls()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CallAnalyticsTracker:
    def __init__(
        self,
        *,
        channel: str,
        participant_identity: str,
        room_name: str,
    ) -> None:
        timestamp = datetime.now(timezone.utc)
        self.call_id = f"CALL-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        self.started_at = timestamp
        self.channel = channel
        self.participant_identity = participant_identity
        self.room_name = room_name
        self.success_reason = ""
        self.outcome_reason = ""
        self._finished = False

    def mark_success(self, reason: str) -> None:
        self.success_reason = reason.strip()
        self.outcome_reason = reason.strip()

    def mark_outcome(self, reason: str) -> None:
        self.outcome_reason = reason.strip()

    def finish(self) -> CallRecord:
        if self._finished:
            return self._read_record()

        status = "successful" if self.success_reason else "failed"
        ended_at = datetime.now(timezone.utc)
        duration_seconds = max((ended_at - self.started_at).total_seconds(), 0.0)
        record = CallRecord(
            call_id=self.call_id,
            started_at=self.started_at.isoformat(),
            ended_at=ended_at.isoformat(),
            duration_seconds=round(duration_seconds, 2),
            status=status,
            channel=self.channel,
            success_reason=self.success_reason,
            outcome_reason=self.outcome_reason or status,
            participant_identity=self.participant_identity,
            room_name=self.room_name,
        )

        conn = get_connection()
        conn.execute(
            """
            INSERT OR REPLACE INTO call_analytics
            (call_id, started_at, ended_at, duration_seconds, status, channel,
             success_reason, outcome_reason, participant_identity, room_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.call_id,
                record.started_at,
                record.ended_at,
                record.duration_seconds,
                record.status,
                record.channel,
                record.success_reason,
                record.outcome_reason,
                record.participant_identity,
                record.room_name,
            ),
        )
        conn.commit()
        conn.close()
        self._finished = True
        export_calls()
        return record

    def _read_record(self) -> CallRecord:
        conn = get_connection()
        row = conn.execute(
            """
            SELECT call_id, started_at, ended_at, duration_seconds, status, channel,
                   success_reason, outcome_reason, participant_identity, room_name
            FROM call_analytics
            WHERE call_id = ?
            """,
            (self.call_id,),
        ).fetchone()
        conn.close()
        if row is None:
            return CallRecord(
                call_id=self.call_id,
                started_at=self.started_at.isoformat(),
                ended_at=self.started_at.isoformat(),
                duration_seconds=0.0,
                status="failed",
                channel=self.channel,
                success_reason=self.success_reason,
                outcome_reason=self.outcome_reason or "failed",
                participant_identity=self.participant_identity,
                room_name=self.room_name,
            )
        return CallRecord(*row)


def start_call(
    *,
    channel: str,
    participant_identity: str,
    room_name: str,
) -> CallAnalyticsTracker:
    return CallAnalyticsTracker(
        channel=channel,
        participant_identity=participant_identity,
        room_name=room_name,
    )


def list_calls() -> list[dict[str, str | float]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT call_id, started_at, ended_at, duration_seconds, status, channel,
               success_reason, outcome_reason, participant_identity, room_name
        FROM call_analytics
        ORDER BY started_at DESC
        """
    ).fetchall()
    conn.close()
    return [
        {
            "call_id": row[0],
            "started_at": row[1],
            "ended_at": row[2],
            "duration_seconds": row[3],
            "status": row[4],
            "channel": row[5],
            "success_reason": row[6],
            "outcome_reason": row[7],
            "participant_identity": row[8],
            "room_name": row[9],
        }
        for row in rows
    ]


def get_stats() -> dict[str, int]:
    calls = list_calls()
    total = len(calls)
    successful = sum(1 for call in calls if call["status"] == "successful")
    failed = total - successful
    return {
        "total_calls": total,
        "successful_calls": successful,
        "failed_calls": failed,
    }


def export_calls() -> None:
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    recent_calls = list_calls()[:10]
    sanitized_recent_calls = [
        {
            "call_id": call["call_id"],
            "started_at": call["started_at"],
            "ended_at": call["ended_at"],
            "duration_seconds": call["duration_seconds"],
            "status": call["status"],
            "channel": call["channel"],
            "success_reason": call["success_reason"],
            "outcome_reason": call["outcome_reason"],
        }
        for call in recent_calls
    ]
    payload = {
        "stats": get_stats(),
        "recent_calls": sanitized_recent_calls,
    }
    EXPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
