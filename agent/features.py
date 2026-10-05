import numpy as np
import os
from agent.entropy import shannon

def extract_v2(events, io_deltas, proc_records, ent_records, scope_files, hp_dirs, base, prior_entropy, t0, t1):
    win_evs = [e for e in events if t0 <= e[0] < t1]
    win_io = [d for d in io_deltas if t0 <= d[0] < t1]
    W = t1 - t0
    feats = {}
    
    # 1. Event Rates & Ratios
    mod_c = sum(1 for e in win_evs if e[1] in ["modified"])
    cre_c = sum(1 for e in win_evs if e[1] == "created")
    del_c = sum(1 for e in win_evs if e[1] == "deleted")
    ren_c = sum(1 for e in win_evs if e[1] == "moved")
    
    feats["mod_rate"] = mod_c / W
    feats["create_rate"] = cre_c / W
    feats["delete_rate"] = del_c / W
    feats["rename_rate"] = ren_c / W
    feats["rename_to_mod_ratio"] = (ren_c / mod_c) if mod_c > 0 else np.nan
    
    historical_cre = set(e[2] for e in events if e[1] == "created" and e[0] < t1)
    del_after_cre = sum(1 for e in win_evs if e[1] == "deleted" and e[2] in historical_cre)
    feats["delete_after_create_ratio"] = (del_after_cre / cre_c) if cre_c > 0 else np.nan
    
    # 2. Scope Breadth
    unique_files = set(e[2] for e in win_evs if e[2]) | set(e[3] for e in win_evs if e[3])
    unique_dirs = set(os.path.dirname(p) for p in unique_files if p)
    feats["breadth"] = len(unique_files) / max(scope_files, 1)
    feats["dirs_touched"] = len(unique_dirs)
    
    evs_30s = [e for e in events if (t1 - 30) <= e[0] < t1]
    feats["affected_30s"] = len(set(e[2] for e in evs_30s if e[2]) | set(e[3] for e in evs_30s if e[3]))
    
    # 3. Extensions
    exts = set(os.path.splitext(p)[1] for p in unique_files if p)
    feats["ext_change_ratio"] = (len(exts) / len(unique_files)) if unique_files else np.nan
    feats["new_unique_ext_count"] = len(exts)
    
    # 4. Storage Write Metrics
    total_write = sum(d[3] for d in win_io)
    feats["write_bytes_rate"] = total_write / W
    feats["write_bytes_per_file"] = (total_write / len(unique_files)) if unique_files else np.nan
    
    # 5. Shannon Entropy Jump
    win_ent = [e for e in ent_records if t0 <= e[0] < t1] if ent_records else []
    if win_ent:
        feats["mean_entropy_sampled"] = float(np.mean([e[2] for e in win_ent]))
        deltas = [e[2] - prior_entropy.get(e[1], 0) for e in win_ent if e[1] in prior_entropy]
        feats["entropy_delta"] = float(np.mean(deltas)) if deltas else np.nan
        feats["high_entropy_frac"] = sum(1 for e in win_ent if e[2] >= 7.2) / len(win_ent)
    else:
        feats["mean_entropy_sampled"] = np.nan
        feats["entropy_delta"] = np.nan
        feats["high_entropy_frac"] = np.nan
        
    # 6. Honeypot Decoys
    hp_touched = sum(1 for p in unique_files if any(hp in p for hp in hp_dirs))
    feats["honeypot_touched"] = 1 if hp_touched > 0 else 0
    feats["honeypot_count"] = hp_touched
    
    # 7. Process Attribution
    pids = set(d[1] for d in win_io)
    win_proc = [p for p in proc_records if t0 <= p[0] < t1] if proc_records else []
    feats["proc_new_rate"] = len(win_proc) / W if proc_records else np.nan
    if win_io:
        top_pid_write = max([sum(d[3] for d in win_io if d[1] == pid) for pid in pids] + [0])
        feats["top_proc_write_share"] = (top_pid_write / total_write) if total_write > 0 else np.nan
        top_pid_ops = max([sum(1 for d in win_io if d[1] == pid) for pid in pids] + [0])
        feats["top_proc_fileop_share"] = top_pid_ops / len(win_io)
    else:
        feats["top_proc_write_share"] = np.nan
        feats["top_proc_fileop_share"] = np.nan
        
    # 8. Adaptive Baseline Z-Scores
    base_mod = base.get("mod_rate_mean", 0) if base else 0
    base_mod_std = max(base.get("mod_rate_std", 1), 1.0) if base else 1.0
    feats["mod_rate_z"] = (feats["mod_rate"] - base_mod) / base_mod_std
    
    base_w = base.get("write_rate_mean", 0) if base else 0
    base_w_std = max(base.get("write_rate_std", 1), 100000.0) if base else 100000.0
    feats["write_rate_z"] = (feats["write_bytes_rate"] - base_w) / base_w_std
    
    return feats
