"""
SQLite database layer.

Tables:
- faqs: the knowledge base (seeded once from seed_data.py if empty)
- chat_logs: every question asked, what it matched (if anything), and the
  confidence score — this is what powers the live stats and the "memory"
  panel on the frontend.

Uses Python's built-in sqlite3 module directly (no ORM) so it's easy to
read and explain in a project report or viva.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            matched_faq_id INTEGER,
            score REAL NOT NULL,
            matched INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def seed_faqs_if_empty(conn: sqlite3.Connection) -> None:
    from seed_data import FAQS

    count = conn.execute("SELECT COUNT(*) AS c FROM faqs").fetchone()["c"]
    if count > 0:
        return
    conn.executemany(
        "INSERT INTO faqs (id, category, question, answer) VALUES (?, ?, ?, ?)",
        [(f["id"], f["category"], f["question"], f["answer"]) for f in FAQS],
    )
    conn.commit()


def get_all_faqs(conn: sqlite3.Connection):
    rows = conn.execute("SELECT id, category, question, answer FROM faqs ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_categories(conn: sqlite3.Connection):
    """One sample question per category, used to render topic chips."""
    rows = conn.execute(
        """
        SELECT category, question
        FROM faqs
        WHERE id IN (SELECT MIN(id) FROM faqs GROUP BY category)
        ORDER BY category
        """
    ).fetchall()
    return [dict(r) for r in rows]


def log_chat(conn: sqlite3.Connection, question: str, matched_faq_id, score: float, matched: bool):
    conn.execute(
        "INSERT INTO chat_logs (question, matched_faq_id, score, matched, created_at) VALUES (?, ?, ?, ?, ?)",
        (question, matched_faq_id, score, int(matched), datetime.utcnow().isoformat()),
    )
    conn.commit()


def get_stats(conn: sqlite3.Connection, memory_limit: int = 3):
    asked_row = conn.execute("SELECT COUNT(*) AS c, AVG(score) AS avg FROM chat_logs").fetchone()
    asked = asked_row["c"] or 0
    avg_score = round(asked_row["avg"], 3) if asked_row["avg"] is not None else 0.0

    faqs_count = conn.execute("SELECT COUNT(*) AS c FROM faqs").fetchone()["c"]

    memory_rows = conn.execute(
        "SELECT question, matched FROM chat_logs ORDER BY id DESC LIMIT ?",
        (memory_limit,),
    ).fetchall()
    memory = [{"question": r["question"], "matched": bool(r["matched"])} for r in memory_rows]

    return {
        "asked": asked,
        "faqs_count": faqs_count,
        "avg_score": avg_score,
        "memory": memory,
        "memory_limit": memory_limit,
    }


def get_random_faqs(conn: sqlite3.Connection, n: int = 3):
    rows = conn.execute("SELECT id, category, question, answer FROM faqs ORDER BY RANDOM() LIMIT ?", (n,)).fetchall()
    return [dict(r) for r in rows]


def get_faq_by_id(conn: sqlite3.Connection, faq_id: int):
    row = conn.execute("SELECT id, category, question, answer FROM faqs WHERE id = ?", (faq_id,)).fetchone()
    return dict(row) if row else None
