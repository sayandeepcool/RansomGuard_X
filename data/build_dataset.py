import sys, os, glob, json, datetime
import pandas as pd
sys.path.append("/kaggle/working/RansomGuard_X")
from data.schema import SCHEMA_HASH, W, STEP, WARMUP_S
from data.windowing import process_run
from data.finalize import finalize
from data.validate import run_validation_gates
from data.split import split_dataset
from data.adapters import load_all_adapters

def main():
    raw_files = glob.glob("data/capture/sim/raw/SIM_PROD_*.jsonl")
    out_dir = f"data/out/v{SCHEMA_HASH}"
    os.makedirs(out_dir, exist_ok=True)

    windows = []
    for rf in raw_files:
        run_id = os.path.basename(rf).replace(".jsonl", "")
        gt_path = os.path.join("data/capture/sim/gt", f"{run_id}.jsonl")
        if os.path.exists(gt_path):
            run_df = process_run(run_id, rf, gt_path)
            if not run_df.empty: windows.append(run_df)

    synthetic_df = pd.concat(windows, ignore_index=True) if windows else pd.DataFrame()
    real_df = load_all_adapters()
    
    combined_df = pd.concat([synthetic_df, real_df], ignore_index=True) if not real_df.empty else synthetic_df
    df = finalize(combined_df)
    
    gate_results = run_validation_gates(df, SCHEMA_HASH)
    train, calib, val, test = split_dataset(df)

    for name, s_df in zip(["train", "calib", "val", "test", "full"], [train, calib, val, test, df]):
        s_df.to_parquet(f"{out_dir}/{name}.parquet", index=False)

    manifest = {"schema_hash": SCHEMA_HASH, "total_windows": len(df), "gates": gate_results}
    with open(f"{out_dir}/manifest.json", "w") as f: json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
