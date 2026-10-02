import time
import json
import os
import hmac
import hashlib
from agent.collectors import EVENTS, PROC_DELTA

def hmac_path(path, secret="ransomguard_seed"):
    if not path:
        return None
    ext = os.path.splitext(path)[1]
    hashed = hmac.new(secret.encode(), path.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{hashed}{ext}"

def flush_logs(out_path, run_id, source="simulator"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a") as f:
        meta_record = {"type": "meta", "run_id": run_id, "source": source, "ts": time.time()}
        f.write(json.dumps(meta_record) + "\n")
        
        while EVENTS:
            ts, op, src, dest = EVENTS.popleft()
            rec = {
                "type": "ev",
                "ts": ts,
                "op": op,
                "src_id": hmac_path(src),
                "dest_id": hmac_path(dest),
                "hp": "Honeypot" in src
            }
            f.write(json.dumps(rec) + "\n")
            
        while PROC_DELTA:
            ts, pid, pname, dwrite = PROC_DELTA.popleft()
            rec = {"type": "io", "ts": ts, "pid": pid, "pname": pname, "dwrite": dwrite}
            f.write(json.dumps(rec) + "\n")
