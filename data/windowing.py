import json, os
import pandas as pd
from agent.features import extract_v2
from data.schema import W, STEP, WARMUP_S
from data.labeling import assign_label
from data.weights import calculate_sample_weight
from agent.baseline import fit_simulator_baseline

SCOPES = {"system": "", "Documents": "Documents", "Projects": "Projects", "Database": "Database", "Honeypot": "Honeypot"}

def filter_events(events, scope_match):
    if not scope_match: return events
    return [e for e in events if (e[2] and scope_match in e[2]) or (e[3] and scope_match in e[3])]

def process_run(run_id, raw_path, gt_path):
    events, io_deltas, proc_records, ent_records = [], [], [], []
    with open(raw_path, "r") as f:
        for line in f:
            rec = json.loads(line.strip())
            if rec["type"] == "ev": events.append((rec["ts"], rec["op"], rec.get("src_id", ""), rec.get("dest_id", "")))
            elif rec["type"] == "io": io_deltas.append((rec["ts"], rec["pid"], rec["pname"], rec["dwrite"]))
            elif rec["type"] == "proc": proc_records.append((rec["ts"], rec["pid"], rec["op"]))
            elif rec["type"] == "ent": ent_records.append((rec["ts"], rec["file"], rec["entropy"]))
            
    with open(gt_path, "r") as f: gt = json.loads(f.readline().strip())
    if not gt.get("valid", True): return pd.DataFrame()
        
    start_time = gt.get("onset_ts", 32.0) - 32.0
    actual_max = max([e[0] for e in events] + [d[0] for d in io_deltas] + [gt.get("end_ts", 0) + 3.0]) if events else gt.get("end_ts", 0) + 3.0
    warmup_end = start_time + WARMUP_S
    baseline = fit_simulator_baseline(events, io_deltas, start_time, warmup_end)
    windows = []
    
    actual_style = gt.get("style", "unknown") if gt.get("mode") == "attack" else "benign"
    actual_mode = gt.get("style", "unknown") if gt.get("mode") == "benign" else gt.get("mode", "unknown")
    
    for scope_name, scope_path in SCOPES.items():
        scope_events = filter_events(events, scope_path) if scope_path else events
        scope_ent = [e for e in ent_records if scope_path in e[1]] if scope_path else ent_records
        t = start_time
        prior_entropy = {}
        
        while t + W <= actual_max:
            if t >= warmup_end:
                f_scope = extract_v2(
                    events=scope_events, io_deltas=io_deltas, proc_records=proc_records, ent_records=scope_ent,
                    scope_files=1000 if not scope_path else 250, hp_dirs=["Honeypot"],
                    base=baseline, prior_entropy=prior_entropy, t0=t, t1=t+W
                )
                label, quality = assign_label(t, W, gt.get("gt_events", []), gt.get("onset_ts", 0), gt.get("end_ts", 0), gt.get("phase", "encrypt"))
                if label is not None:
                    windows.append({
                        "run_id": run_id, "group_id": run_id, "source": "simulator",
                        "style": actual_style, "mode": actual_mode, "phase": gt.get("phase", "unknown"),
                        "scope": scope_name, "scope_type": "folder" if scope_path else "system",
                        "ts": t, "label": label, "label_quality": quality,
                        "weight": calculate_sample_weight(label, actual_style, actual_mode), "family": "synthetic",
                        **f_scope
                    })
            t += STEP
    return pd.DataFrame(windows)
