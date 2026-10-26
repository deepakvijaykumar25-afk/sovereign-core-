"""
core/vault.py
Local Private Vault — SQLite-backed persistent storage (MCP layer).
All data stays on-device. Nothing leaves the local machine.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "vault.db"


def init_vault():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            content     TEXT    NOT NULL,
            created_at  TEXT    NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            query       TEXT    NOT NULL,
            results     TEXT    NOT NULL,
            created_at  TEXT    NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            date        TEXT,
            created_at  TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ── Memories ──────────────────────────────────────────────────────────────────

def save_memory(category: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO memories (category, content, created_at) VALUES (?, ?, ?)",
        (category, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_memories(category: str = None) -> list:
    conn = sqlite3.connect(DB_PATH)
    if category:
        rows = conn.execute(
            "SELECT * FROM memories WHERE category=? ORDER BY created_at DESC",
            (category,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM memories ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return rows


# ── Searches ──────────────────────────────────────────────────────────────────

def save_search(query: str, results: list):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO searches (query, results, created_at) VALUES (?, ?, ?)",
        (query, json.dumps(results), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# ── Schedule ──────────────────────────────────────────────────────────────────

def save_schedule(title: str, description: str, date: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO schedule (title, description, date, created_at) VALUES (?, ?, ?, ?)",
        (title, description, date, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_schedule() -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM schedule ORDER BY date ASC"
    ).fetchall()
    conn.close()
    return rows
