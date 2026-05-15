import sqlite3
import os

DB_PATH = "database/evidence.db"

def init_db():
    os.makedirs("database", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    schema_path = os.path.join("database", "schema.sql")
    
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema = f.read()
            cur.executescript(schema)
            print("Database schema created successfully")
    else:
        print(f"Warning: Schema file not found at {schema_path}")
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
    
    sample_data = [
        (1, 'Password Policy', 'HIGH', 
         '{"min_length": 6}', '{"min_length": 12}', '2024-01-15 10:30:00'),
        (2, 'Windows Firewall', 'HIGH', 
         '{"Private": false}', '{"Private": true}', '2024-01-15 10:35:00'),
        (3, 'Unauthorized Admin Users', 'CRITICAL', 
         '{"users": ["DOMAIN\\\\User1"]}', '{"users": []}', '2024-01-15 10:40:00'),
        (4, 'Critical Services', 'CRITICAL', 
         '{"WinDefend": false}', '{"WinDefend": true}', '2024-01-15 10:45:00')
    ]
    
    try:
        cur.executemany("""
        INSERT OR IGNORE INTO evidence (id, control, severity, before_state, after_state, collected_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, sample_data)
        print("Sample data inserted")
    except Exception as e:
        print(f"Note: {e}")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()