import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def lookup_user(user_id: str):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT user_id, name, language_preference, facts, last_interaction
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "name": row[1],
        "language_preference": row[2],
        "facts": json.loads(row[3]) if row[3] else {},
        "last_interaction": row[4],
    }


def save_user(
    user_id: str,
    name: str,
    language_preference: str = "",
    facts: dict | None = None,
):
    facts = facts or {}

    existing_user = lookup_user(user_id)

    if existing_user:
        merged_facts = existing_user["facts"]
        merged_facts.update(facts)

        if not language_preference:
            language_preference = existing_user["language_preference"]

        conn = get_connection()

        conn.execute(
            """
            UPDATE users
            SET name = ?,
                language_preference = ?,
                facts = ?,
                last_interaction = ?
            WHERE user_id = ?
            """,
            (
                name,
                language_preference,
                json.dumps(merged_facts),
                datetime.now(timezone.utc).isoformat(),
                user_id,
            ),
        )

    else:
        conn = get_connection()

        conn.execute(
            """
            INSERT INTO users
            (user_id, name, language_preference, facts, last_interaction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                language_preference,
                json.dumps(facts),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")