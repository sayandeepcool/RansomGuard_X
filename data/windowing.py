import json, os, time
import pandas as pd
from agent.features import extract
from data.schema import W, STEP, WARMUP_S

def process_run(run_id, raw_path, gt_path, baseline):
    events, io_deltas = [], []
    with open(raw_path, "r") as f:
        for line in f:
            rec = json.loads(line.strip())
            if rec["type"] == "ev":
                events.append((rec["ts"], rec["op"], rec.get("src_id", ""), rec.get("dest_id", "")))
            elif rec["type"] == "io":
                io_deltas.append((rec["ts"], rec["pid"], rec["pname"], rec["dwrite"]))
    
    with open(gt_path, "r") as f:
        gt = json.loads(f.readline().strip())
        
    start_time = min([e[0] for e in events] + [d[0] for d in io_deltas]) if events else 0
    max_time = max([e[0] for e in events] + [d[0] for d in io_deltas]) if events else 0
    
    windows = []
    t = start_time
    prior_entropy = {}
    
    while t + W <= max_time:
        if t - start_time >= WARMUP_S:
            # Process system scope
            f_sys = extract(events, io_deltas, scope_files=1000, hp_dirs=["Honeypot"], 
                            base=baseline, prior_entropy=prior_entropy, t0=t, t1=t+W)
            
            # Labeling logic
            a_sys = sum(1 for e in events if t <= e[0] < t+W and e[1] in ["modified", "moved"])
            is_attack = 1 if (t >= gt["onset_ts"] and t + W <= gt["end_ts"] + 10) else 0
            
            windows.append({"run_id": run_id, "group_id": run_id, "source": "simulator",
                            "style": gt["style"], "mode": gt["mode"], "phase": "attack" if is_attack else "benign",
                            "scope": "system", "scope_type": "system", "ts": t, "label": is_attack,
                            "label_quality": "clean", "weight": 1.0, "family": "synthetic", **f_sys})
        t += STEP
        
    return pd.DataFrame(windows)
