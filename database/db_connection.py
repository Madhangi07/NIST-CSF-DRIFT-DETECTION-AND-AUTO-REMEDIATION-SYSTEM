import sqlite3

DB_PATH = "database/evidence.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        control TEXT,
        severity TEXT,
        before_state TEXT,
        after_state TEXT,
        collected_at TEXT
    )
    """)

    conn.commit()
    conn.close()