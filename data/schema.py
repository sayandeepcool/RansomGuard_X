import hashlib, json, numpy as np

W, STEP, WARMUP_S = 2.0, 1.0, 30
HIGH_ENT = 7.2
A_MIN = 5
SIGMA_FLOOR = {"mod": 1.0, "write": 1e5}

NA_GROUPS = {
 "na_events":  ["mod_rate", "create_rate", "delete_rate", "rename_rate", "rename_to_mod_ratio"],
 "na_scope":   ["breadth", "dirs_touched", "delete_after_create_ratio", "affected_30s"],
 "na_ext":     ["ext_change_ratio", "new_unique_ext_count"],
 "na_write":   ["write_bytes_rate", "write_bytes_per_file"],
 "na_entropy": ["mean_entropy_sampled", "entropy_delta", "high_entropy_frac"],
 "na_honeypot":["honeypot_touched", "honeypot_count"],
 "na_process": ["proc_new_rate", "top_proc_write_share", "top_proc_fileop_share"],
 "na_base":    ["mod_rate_z", "write_rate_z"],
}
FEATURES = [c for g in NA_GROUPS.values() for c in g]
FLAGS    = list(NA_GROUPS)
X_COLS   = FEATURES + FLAGS
META = ["run_id", "group_id", "source", "style", "mode", "phase", "scope", "scope_type",
        "ts", "label", "label_quality", "weight", "family"]
FORBIDDEN = set(META) | {"path", "hash", "folder_id", "window_id", "timestamp", "pid"}
assert not (set(X_COLS) & FORBIDDEN), "Forbidden leakage column detected in X_COLS!"
SCHEMA_HASH = hashlib.sha256(json.dumps([X_COLS, W, STEP, HIGH_ENT, SIGMA_FLOOR]).encode()).hexdigest()[:12]

def validate_model_payload(payload):
    if payload.get("schema_hash") != SCHEMA_HASH:
        raise ValueError(f"Schema mismatch: Model expects {payload.get('schema_hash')}, Runtime requires {SCHEMA_HASH}")
    return True
