import time
import json
import os
import subprocess
import threading
import sys

sys.path.append("/kaggle/working/RansomGuard_X")
from agent.collectors import start_file_observer, sample_process_io
from agent.record import flush_logs

ATTACK_STYLES = ["inplace_fast", "copy_delete", "rename_only"]
BENIGN_MODES = ["office_edit", "zip_archive", "bulk_rename"]
TEST_ROOT = "/kaggle/working/RansomGuard_X/RansomGuard_Test"

def run_campaign(base_run_id="SIM"):
    gt_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/gt"
    raw_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/raw"
    os.makedirs(gt_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    
    run_counter = 1
    # Create a schedule: 2 runs of each attack, 2 runs of each benign mode
    scenarios = [(s, "attack", "encrypt") for s in ATTACK_STYLES] * 2 + \
                [(m, "benign", "benign") for m in BENIGN_MODES] * 2
    
    for style, mode_type, phase in scenarios:
        run_id = f"{base_run_id}_{mode_type.upper()}_{run_counter:03d}"
        gt_path = os.path.join(gt_dir, f"{run_id}.jsonl")
        raw_path = os.path.join(raw_dir, f"{run_id}.jsonl")
        
        print(f"--- Starting {run_id} ({style}) ---")
        
        # 1. Start Agent Listeners
        observer = start_file_observer([
            f"{TEST_ROOT}/Documents", f"{TEST_ROOT}/Projects", 
            f"{TEST_ROOT}/Database", f"{TEST_ROOT}/Honeypot"
        ])
        stop_event = threading.Event()
        io_thread = threading.Thread(target=sample_process_io, args=(stop_event,))
        io_thread.start()
        
        # 2. Baseline Period
        print("Collecting 15s baseline noise...")
        time.sleep(15)  
        
        # 3. Execution
        onset_ts = time.time()
        print("Executing scenario subprocess...")
        proc = subprocess.Popen(["python", "/kaggle/working/RansomGuard_X/sim/run_scenario.py", style])
        proc.wait()
        end_ts = time.time()
        
        # 4. Stop Agent and Flush Telemetry
        stop_event.set()
        observer.stop()
        observer.join()
        io_thread.join()
        flush_logs(raw_path, run_id=run_id, source="simulator")
        
        # 5. Save Ground Truth Labels
        gt_record = {
            "run_id": run_id, "style": style, "onset_ts": onset_ts, 
            "end_ts": end_ts, "mode": mode_type, "phase": phase
        }
        with open(gt_path, "w") as f:
            f.write(json.dumps(gt_record) + "\n")
            
        print(f"Finished {run_id}. Telemetry and Ground Truth saved.\n")
        run_counter += 1

if __name__ == "__main__":
    run_campaign()
