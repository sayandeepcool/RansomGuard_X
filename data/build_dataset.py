import os, glob, sys
import pandas as pd

# Add project root to path so modules resolve correctly
sys.path.append("/kaggle/working/RansomGuard_X")

from data.windowing import process_run
from data.finalize import finalize
from agent.baseline import get_default_baseline

def build_all():
    raw_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/raw"
    gt_dir = "/kaggle/working/RansomGuard_X/data/capture/sim/gt"
    out_dir = "/kaggle/working/RansomGuard_X/data/out"
    os.makedirs(out_dir, exist_ok=True)
    
    all_windows = []
    # Using the frozen default baseline as specified for Kaggle execution
    baseline = get_default_baseline() 
    
    raw_files = glob.glob(f"{raw_dir}/*.jsonl")
    print(f"Found {len(raw_files)} raw telemetry logs. Processing windows...")
    
    for raw_path in raw_files:
        run_id = os.path.basename(raw_path).replace(".jsonl", "")
        gt_path = os.path.join(gt_dir, f"{run_id}.jsonl")
        
        if os.path.exists(gt_path):
            print(f"Windowing {run_id}...")
            run_df = process_run(run_id, raw_path, gt_path, baseline)
            all_windows.append(run_df)
            
    if all_windows:
        df = pd.concat(all_windows, ignore_index=True)
        # Apply missingness flags and final formatting once across the entire pool
        df = finalize(df)
        
        out_path = os.path.join(out_dir, "train_local.parquet")
        df.to_parquet(out_path, index=False)
        print(f"\nSUCCESS! Final dataset generated: {len(df)} windows across {len(all_windows)} distinct runs.")
        print(f"Saved to: {out_path}")
    else:
        print("ERROR: No windows generated.")

if __name__ == "__main__":
    build_all()
