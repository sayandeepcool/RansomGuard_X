import os, sys, json, hashlib, joblib
import pandas as pd, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
sys.path.append("/kaggle/working/RansomGuard_X")
from data.schema import X_COLS, SCHEMA_HASH

def compute_thresholds(val_df, cal_model):
    X_val = val_df[X_COLS].fillna(0); y_val = val_df["label"].values
    if hasattr(cal_model, "predict_proba"):
        probs_raw = cal_model.predict_proba(X_val)
        probs = probs_raw[:, 1] if probs_raw.shape[1] > 1 else np.zeros(len(y_val))
    else: probs = np.zeros(len(y_val))
    benign_probs = probs[y_val == 0]
    t_warn = float(np.percentile(benign_probs, 99.0)) if len(benign_probs) > 0 else 0.30
    t_crit = float(max(np.percentile(benign_probs, 99.9), 0.75)) if len(benign_probs) > 0 else 0.80
    return {"T_warn": round(t_warn, 4), "T_high": round((t_warn + t_crit) / 2.0, 4), "T_crit": round(t_crit, 4), "alert_threshold": round((t_warn + t_crit) / 2.0, 4)}

def train():
    data_dir = f"/kaggle/working/RansomGuard_X/data/out/v{SCHEMA_HASH}"
    out_dir = "/kaggle/working/RansomGuard_X/ml"
    os.makedirs(out_dir, exist_ok=True)
    
    train_df = pd.read_parquet(f"{data_dir}/train.parquet")
    calib_df = pd.read_parquet(f"{data_dir}/calib.parquet")
    val_df   = pd.read_parquet(f"{data_dir}/val.parquet")

    X_train, y_train = train_df[X_COLS].fillna(0), train_df["label"]
    X_calib, y_calib = calib_df[X_COLS].fillna(0), calib_df["label"]
    w_train = train_df["weight"].values if "weight" in train_df.columns else None

    rf = RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_depth=14, class_weight="balanced_subsample", n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train, sample_weight=w_train) if y_train.nunique() > 1 else rf.fit(X_train, y_train)

    if y_calib.nunique() > 1 and y_train.nunique() > 1:
        cal = CalibratedClassifierCV(estimator=rf, cv="prefit", method="isotonic")
        cal.fit(X_calib, y_calib)
    else: cal = rf

    thresholds = compute_thresholds(val_df, cal)
    with open(f"{out_dir}/thresholds.json", "w") as f: json.dump(thresholds, f, indent=2)

    payload = {"cal": cal, "rf": rf, "feats": X_COLS, "schema_hash": SCHEMA_HASH}
    joblib.dump(payload, f"{out_dir}/model.joblib")
    with open(f"{out_dir}/model.joblib", "rb") as f: sha = hashlib.sha256(f.read()).hexdigest()
    with open(f"{out_dir}/model.sha256", "w") as f: f.write(sha)
        
if __name__ == "__main__": train()
