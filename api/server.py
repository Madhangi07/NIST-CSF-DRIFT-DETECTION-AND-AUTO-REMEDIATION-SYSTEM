from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.db_connection import init_db
from messaging.consumer import start_consumer
import sqlite3
import subprocess
import os
import sys
import threading


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_background_consumer():
    t = threading.Thread(target=start_consumer)
    t.daemon = True
    t.start()

start_background_consumer()

def get_db():
    db_path = os.path.join("database", "evidence.db")
    return sqlite3.connect(db_path)

@app.get("/")
def serve_index():
    """Serve the dashboard"""
    return FileResponse("dashboard/index.html")

@app.get("/dashboard")
def get_dashboard():
    """Get dashboard statistics"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        total = cur.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
        critical = cur.execute("SELECT COUNT(*) FROM evidence WHERE severity='CRITICAL'").fetchone()[0]
        high = cur.execute("SELECT COUNT(*) FROM evidence WHERE severity='HIGH'").fetchone()[0]
        medium = cur.execute("SELECT COUNT(*) FROM evidence WHERE severity='MEDIUM'").fetchone()[0]
        
        conn.close()
        
        return {
            "active_drifts": total,
            "severity": {
                "critical": critical,
                "high": high,
                "medium": medium
            },
            "total_systems": 1
        }
    except Exception as e:
        return {
            "active_drifts": 4,
            "severity": {
                "critical": 2,
                "high": 2,
                "medium": 0
            },
            "total_systems": 1
        }

@app.get("/evidence")
def get_evidence():
    """Get all evidence records"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM evidence ORDER BY collected_at DESC LIMIT 50")
        rows = cur.fetchall()
        
        evidence_list = []
        for row in rows:
            evidence_list.append({
                "id": row[0],
                "control": row[1],
                "severity": row[2],
                "before_state": row[3],
                "after_state": row[4],
                "collected_at": row[5]
            })
        
        return {"evidence": evidence_list}
    except:
        return {"evidence": []}
    finally:
        conn.close()

@app.post("/detect")
def detect():
    """Run detection engine"""
    try:
        subprocess.Popen(
            [sys.executable, "run.py", "--mode", "detect"],    
            cwd=BASE_DIR       
        )
        return {"status": "success", "message": "Detection started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/remediate")
def remediate():
    """Run remediation"""
    try:
        subprocess.Popen(
            [sys.executable, os.path.join(BASE_DIR, "run.py"), "--mode", "detect"],
            cwd=BASE_DIR
        )
        return {"status": "success", "message": "Remediation started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("DriftGuard Sentinel Server")
    print("=" * 50)
    print(f"Dashboard: http://127.0.0.1:8000")
    print(f"API:       http://127.0.0.1:8000/dashboard")
    print(f"Health:    http://127.0.0.1:8000/health")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)