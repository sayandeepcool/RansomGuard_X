import sqlite3, json, hashlib, os

DB_PATH = "/kaggle/working/RansomGuard_X/data/incidents.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute('''CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts REAL, risk REAL, process TEXT, factors TEXT, 
                        action TEXT, prev_hash TEXT, hash TEXT)''')
        
def log_incident(ts, risk, process, factors, action):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT hash FROM incidents ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        prev_hash = row[0] if row else "0000"
        
        record = json.dumps({"ts": ts, "risk": risk, "process": process, "action": action})
        current_hash = hashlib.sha256((prev_hash + record).encode()).hexdigest()
        
        cur.execute('''INSERT INTO incidents (ts, risk, process, factors, action, prev_hash, hash)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                    (ts, risk, process, json.dumps(factors), action, prev_hash, current_hash))
        conn.commit()

def get_incidents():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM incidents ORDER BY ts DESC")
        return [dict(row) for row in cur.fetchall()]
