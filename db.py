from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "bot.sqlite3"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                source       TEXT NOT NULL,
                service      TEXT,
                contact      TEXT,
                problem_text TEXT,
                agent_summary TEXT,
                missing_info  TEXT,
                status       TEXT NOT NULL DEFAULT 'new',
                created_at   TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                message_text TEXT NOT NULL,
                created_at   TEXT NOT NULL
            )
        """)
        conn.commit()


def save_lead(
    session_id: str,
    source: str,
    service: str | None = None,
    contact: str | None = None,
    problem_text: str | None = None,
    agent_summary: str | None = None,
    missing_info: str | None = None,
    status: str = "new",
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads
                (session_id, source, service, contact, problem_text,
                 agent_summary, missing_info, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, source, service, contact, problem_text,
             agent_summary, missing_info, status, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid


def save_feedback(session_id: str, message_text: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (session_id, message_text, created_at) VALUES (?, ?, ?)",
            (session_id, message_text, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid
