import sqlite3
from datetime import datetime

DB_PATH = "cv_analyzer.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cv_text     TEXT NOT NULL,
            job_desc    TEXT NOT NULL,
            score       TEXT NOT NULL,
            matched     TEXT NOT NULL,
            missing     TEXT NOT NULL,
            suggestions TEXT NOT NULL,
            summary     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(cv_text, job_desc, score, matched, missing, suggestions, summary):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses
            (cv_text, job_desc, score, matched, missing, suggestions, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cv_text,
        job_desc,
        score,
        ", ".join(matched),
        ", ".join(missing),
        " | ".join(suggestions),
        summary,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()


def get_all_analyses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
