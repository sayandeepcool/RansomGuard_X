import time, json, os, subprocess, threading, sys
sys.path.append("/kaggle/working/RansomGuard_X")
from agent.collectors import start_file_observer, sample_process_io
from agent.record import flush_logs

ATTACK_STYLES = ["inplace_fast", "copy_delete", "rename_only", "intermittent", "slow_low", "burst_throttled", "honeypot_avoid"]
BENIGN_MODES = ["idle", "office_edit", "zip_archive", "unzip", "git_checkout", "npm_install", "backup_copy", "media_export", "bulk_rename", "sync_client", "av_scan"]
TEST_ROOT = "/kaggle/working/RansomGuard_X/RansomGuard_Test"

def run_campaign():
    gt_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/gt"
    raw_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/raw"
    os.makedirs(gt_dir, exist_ok=True); os.makedirs(raw_dir, exist_ok=True)
    
    # 43 Runs (3 per attack, 2 per benign) to guarantee >7 groups for StratifiedGroupKFold
    plan = [(s, "attack", "encrypt") for s in ATTACK_STYLES] * 3 + [(m, "benign", "benign") for m in BENIGN_MODES] * 2
    print(f"Starting Fast-Track Production Campaign: {len(plan)} runs.")

    for idx, (name, mode_type, phase) in enumerate(plan, 1):
        run_id = f"SIM_PROD_{mode_type.upper()}_{idx:03d}_{name}"
        gt_path = os.path.join(gt_dir, f"{run_id}.jsonl")
        raw_path = os.path.join(raw_dir, f"{run_id}.jsonl")
        if os.path.exists(raw_path) and os.path.exists(gt_path): continue

        subprocess.run(["python", "/kaggle/working/RansomGuard_X/sim/seed_tree.py"], check=False)
        observer = start_file_observer([f"{TEST_ROOT}/Documents", f"{TEST_ROOT}/Projects", f"{TEST_ROOT}/Database", f"{TEST_ROOT}/Honeypot"])
        stop_event = threading.Event()
        io_thread = threading.Thread(target=sample_process_io, args=(stop_event,))
        io_thread.daemon = True; io_thread.start()

        time.sleep(32) # WARMUP_S + buffer
        onset_ts = time.time(); seed = 42 + idx
        proc = subprocess.Popen(["python", "/kaggle/working/RansomGuard_X/sim/run_scenario.py", name, str(seed)])
        try: proc.wait(timeout=35)
        except subprocess.TimeoutExpired: proc.kill()
            
        end_ts = time.time(); time.sleep(3)
        stop_event.set()
        try: observer.stop()
        except: pass

        flush_logs(raw_path, run_id=run_id, source="simulator")
        gt_events = [(onset_ts + (i * 0.1), "attack_actor") for i in range(max(10, int((end_ts - onset_ts) * 10)))] if mode_type == "attack" else []
        gt_record = {"run_id": run_id, "style": name, "mode": mode_type, "valid": True, "onset_ts": onset_ts, "end_ts": end_ts, "phase": phase, "seed": seed, "gt_events": gt_events}
        with open(gt_path, "w") as f: f.write(json.dumps(gt_record) + "\n")
        
if __name__ == "__main__":
    run_campaign()
