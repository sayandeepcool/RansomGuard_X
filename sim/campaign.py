import time
import json
import subprocess
import os

def run_campaign(run_id="SIM_001", attack_style="inplace_fast"):
    gt_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/gt"
    os.makedirs(gt_dir, exist_ok=True)
    gt_path = os.path.join(gt_dir, f"{run_id}.jsonl")
    
    print(f"Starting Campaign {run_id}: Baseline Period (10s)...")
    time.sleep(10)  # Wait 10 seconds to collect "normal" background noise
    
    onset_ts = time.time()
    print(f"Executing Attack Style: {attack_style} at timestamp {onset_ts}")
    
    # Launch the attack script we wrote in Phase 2
    proc = subprocess.Popen(["python", "/kaggle/working/RansomGuard_X/sim/run_scenario.py", attack_style])
    proc.wait()
    end_ts = time.time()
    
    # Save the exact timing to our ground truth log
    gt_record = {
        "run_id": run_id,
        "style": attack_style,
        "onset_ts": onset_ts,
        "end_ts": end_ts,
        "mode": "attack"
    }
    
    with open(gt_path, "w") as f:
        f.write(json.dumps(gt_record) + "\n")
    print(f"Campaign {run_id} complete. Ground truth saved to {gt_path}")

if __name__ == "__main__":
    run_campaign()
