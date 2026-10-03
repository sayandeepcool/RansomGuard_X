from fastapi import FastAPI, Header, HTTPException
from api.db import init_db, get_incidents

app = FastAPI(title="RansomGuard X Local API")
init_db()

# Hardcoded for hackathon prototype
API_TOKEN = "ransomguard_demo_token"

def auth(token: str):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/incidents")
def fetch_incidents(x_token: str = Header(default=None)):
    auth(x_token)
    return get_incidents()

@app.get("/status")
def status():
    return {"status": "Active", "agent": "Monitoring Filesystem & Processes"}
