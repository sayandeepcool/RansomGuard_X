import numpy as np
import os
from collections import Counter
from agent.entropy import shannon

def extract(events, proc_deltas, scope_files, hp_dirs, base, prior_entropy, t0, t1, W=2.0):
    ev = [e for e in events if t0 <= e[0] < t1]
    
    c = Counter(e[1] for e in ev)
    mods, ren = c["modified"], c.get("moved", 0)
    
    touched = {e[2] for e in ev} | {e[3] for e in ev if len(e) > 3 and e[3]}
    ext_chg = sum(1 for e in ev if e[1]=="moved" and len(e) > 3 and e[3] and
                  os.path.splitext(e[2])[1].lower() != os.path.splitext(e[3])[1].lower())
    
    hp = [e for e in ev if any(h in e[2] for h in hp_dirs)]
    
    wr = [d for d in proc_deltas if t0 <= d[0] < t1]
    tot = sum(d[3] for d in wr) or 0
    top = max((sum(d[3] for d in wr if d[1]==pid), pid) for pid in {d[1] for d in wr})[0] if wr else 0
    
    ds = []
    sampled_count = 0
    high_ent_count = 0
    for p in list({e[2] for e in ev if e[1]=="modified"})[:20]:
        h = shannon(p)
        if h is not None:
            if p in prior_entropy:
                ds.append(h - prior_entropy[p])
            prior_entropy[p] = h
            sampled_count += 1
            if h > 7.2:
                high_ent_count += 1
                
    n = max(len(touched), 1)
    
    f = dict(
        mod_rate=mods/W, 
        create_rate=c.get("created", 0)/W, 
        delete_rate=c.get("deleted", 0)/W, 
        rename_rate=ren/W,
        breadth=len(touched)/max(scope_files, 1), 
        dirs_touched=len({os.path.dirname(p) for p in touched}),
        rename_to_mod_ratio=ren/max(mods, 1), 
        ext_change_ratio=ext_chg/n,
        write_bytes_rate=tot/W, 
        write_bytes_per_file=tot/n,
        mean_entropy_sampled=float(np.mean(ds)) if ds else np.nan,
        entropy_delta=float(np.mean(ds)) if ds else np.nan,
        high_entropy_frac=(high_ent_count / sampled_count) if sampled_count else np.nan,
        honeypot_touched=int(bool(hp)), 
        honeypot_count=len(hp),
        top_proc_write_share=(top/tot) if tot else 0.0,
        delete_after_create_ratio=0.0,
        new_unique_ext_count=ext_chg,
        proc_new_rate=0.0,
        top_proc_fileop_share=0.0,
        affected_30s=len(touched)
    )
    
    f["mod_rate_z"] = (f["mod_rate"] - base["mod_mu"]) / max(base["mod_sd"], 1.0)
    f["write_rate_z"] = (f["write_bytes_rate"] - base["wr_mu"]) / max(base["wr_sd"], 1e5)
    
    return f
