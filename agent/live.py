import sys, time, json, joblib, os
import pandas as pd
import numpy as np
import threading

sys.path.append("/kaggle/working/RansomGuard_X")
from agent.collectors import start_file_observer, sample_process_io, EVENTS, PROC_DELTA
from agent.features import extract
from agent.baseline import load_baseline
from data.schema import X_COLS
from response.controller import respond

def run_live_agent():
    print("1. Loading Assets & AI Models...")
    payload = joblib.load("ml/model.joblib")
    rf, cal = payload["rf"], payload["cal"]
    explainer = joblib.load("ml/explainer.joblib")
    
    with open("ml/thresholds.json", "r") as f:
        target_threshold = json.load(f)["alert_threshold"]
    print(f"Loaded Operational Threshold: {target_threshold:.4f}")

    baseline = load_baseline()
    prior_entropy = {}
    
    print("2. Deploying Real-Time Sensors...")
    TEST_ROOT = "/kaggle/working/RansomGuard_X/RansomGuard_Test"
    observer = start_file_observer([
        f"{TEST_ROOT}/Documents", f"{TEST_ROOT}/Projects", 
        f"{TEST_ROOT}/Database", f"{TEST_ROOT}/Honeypot"
    ])
    stop_event = threading.Event()
    io_thread = threading.Thread(target=sample_process_io, args=(stop_event,))
    io_thread.start()

    # Enforce active mitigation (dry_run = False) for the demo
    config = {"allowlist_proc": ["bash", "systemd"], "dry_run": False}
    
    print("3. Starting Continuous 2-Second Sliding Window Monitoring...")
    try:
        while True:
            time.sleep(1.0) # Step size
            now = time.time()
            
            # Extract live features
            feats = extract(list(EVENTS), list(PROC_DELTA), scope_files=1000, 
                            hp_dirs=["Honeypot"], base=baseline, prior_entropy=prior_entropy, 
                            t0=now-2.0, t1=now)
            
            # Format for the ML model
            df_feats = pd.DataFrame([feats]).replace([np.inf, -np.inf], np.nan).fillna(0)
            for col in X_COLS:
                if col not in df_feats.columns: df_feats[col] = 0
            X_live = df_feats[X_COLS]
            
            # Inference
            risk_score = cal.predict_proba(X_live)[0][1]
            
            if risk_score >= target_threshold:
                print(f"\n[!] CRITICAL ALERT: Risk Score {risk_score:.4f} exceeded limit ({target_threshold:.4f})")
                
                # 4. Explainable Alerting via SHAP
                shap_vals = explainer.shap_values(X_live)
                v = shap_vals[1][0] if isinstance(shap_vals, list) else shap_vals[0, :, 1]
                top_idx = np.argsort(np.abs(v))[-3:]
                reasons = [f"{X_COLS[i]} (+{v[i]:.3f})" for i in top_idx]
                print(f"[*] Behavioral Context: {', '.join(reasons)}")
                
                # 5. Automated Mitigation
                recent_io = [d for d in list(PROC_DELTA) if d[0] >= now - 2.0]
                if recent_io:
                    # Isolate the top writing PID
                    pid_map = {}
                    for d in recent_io:
                        pid_map[d[1]] = pid_map.get(d[1], 0) + d[3]
                    top_pid = max(pid_map, key=pid_map.get)
                    
                    touched_files = list({e[2] for e in list(EVENTS) if e[1] == "modified" and e[0] >= now - 2.0})
                    action_result = respond(top_pid, touched_files, config)
                    print(f"[*] Response Action: {action_result}")
                
                print("[*] Threat Contained. Shutting down sensors.")
                break 
                
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        observer.stop()
        observer.join()
        io_thread.join()

if __name__ == "__main__":
    run_live_agent()
