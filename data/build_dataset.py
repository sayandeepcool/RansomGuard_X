import sys, os, glob, json, datetime
import pandas as pd
sys.path.append("/kaggle/working/RansomGuard_X")

from data.schema import SCHEMA_HASH, W, STEP, WARMUP_S
from data.windowing import process_run
from data.finalize import finalize
from data.validate import run_validation_gates
from data.split import split_dataset

def main():
    out_dir = f"data/out/v{SCHEMA_HASH}"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Check if raw disk captures exist to parse
    raw_files = glob.glob("data/capture/sim/raw/*.jsonl")
    gt_dir = "data/capture/sim/gt"
    windows = []
    
    if raw_files:
        print(f"Parsing {len(raw_files)} raw JSONL logs from disk...")
        for rf in raw_files:
            run_id = os.path.basename(rf).replace(".jsonl", "")
            gt_path = os.path.join(gt_dir, f"{run_id}.jsonl")
            if os.path.exists(gt_path):
                run_df = process_run(run_id, rf, gt_path)
                if not run_df.empty: windows.append(run_df)

    if windows:
        df = pd.concat(windows, ignore_index=True)
    elif os.path.exists("data/out/train_local.parquet"):
        print("Using existing train_local.parquet archive...")
        df = pd.read_parquet("data/out/train_local.parquet")
    else:
        raise RuntimeError("No telemetry data found. Run simulator campaign first.")

    df = finalize(df)
    gate_results = run_validation_gates(df, SCHEMA_HASH)
    train, calib, val, test = split_dataset(df)

    train.to_parquet(f"{out_dir}/train.parquet", index=False)
    calib.to_parquet(f"{out_dir}/calib.parquet", index=False)
    val.to_parquet(f"{out_dir}/val.parquet", index=False)
    test.to_parquet(f"{out_dir}/test.parquet", index=False)
    df.to_parquet(f"{out_dir}/full.parquet", index=False)

    manifest = {
        "schema_hash": SCHEMA_HASH, "window_size": W, "step_size": STEP, "warmup_s": WARMUP_S,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_windows": len(df), "positive_windows": int(df["label"].sum()),
        "negative_windows": int((df["label"] == 0).sum()), "groups": df["group_id"].nunique(),
        "splits": {"train": len(train), "calib": len(calib), "val": len(val), "test": len(test)},
        "gates": gate_results
    }
    with open(f"{out_dir}/manifest.json", "w") as f: json.dump(manifest, f, indent=2)
    print(f"Dataset build complete. Artifacts saved in {out_dir}")

if __name__ == "__main__":
    main()
