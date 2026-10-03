import pandas as pd
import numpy as np
import joblib
import hashlib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupShuffleSplit, train_test_split
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.schema import X_COLS, SCHEMA_HASH

def train_model(data_path="/kaggle/working/RansomGuard_X/data/out/train_local.parquet", out_dir="/kaggle/working/RansomGuard_X/ml"):
    print(f"Loading dataset from {data_path}...")
    df = pd.read_parquet(data_path)
    
    unique_runs = df['run_id'].nunique()
    
    # 1. Split Data (Adaptive: Group-level if >=3 runs exist, Row-level fallback if 1-2 runs)
    if unique_runs >= 3:
        print(f"Detected {unique_runs} unique runs. Using GroupShuffleSplit...")
        gss = GroupShuffleSplit(n_splits=1, train_size=0.7, random_state=7)
        train_idx, rest_idx = next(gss.split(df, groups=df['run_id']))
        train, rest = df.iloc[train_idx], df.iloc[rest_idx]
        
        gss2 = GroupShuffleSplit(n_splits=1, train_size=0.5, random_state=7)
        cal_idx, val_idx = next(gss2.split(rest, groups=rest['run_id']))
        calib, val = rest.iloc[cal_idx], rest.iloc[val_idx]
    else:
        print(f"Detected {unique_runs} run_id ({df['run_id'].unique()}). Using stratified row split...")
        strat = df['label'] if df['label'].nunique() > 1 else None
        train, rest = train_test_split(df, train_size=0.7, random_state=7, stratify=strat)
        
        strat_rest = rest['label'] if rest['label'].nunique() > 1 else None
        calib, val = train_test_split(rest, train_size=0.5, random_state=7, stratify=strat_rest)
    
    print(f"Split sizes -> Train: {len(train)} | Calib: {len(calib)} | Val: {len(val)}")
    
    X_train, y_train = train[X_COLS], train['label']
    X_calib, y_calib = calib[X_COLS], calib['label']
    
    # 2. Train Base Random Forest
    print("Training Random Forest baseline...")
    rf = RandomForestClassifier(
        n_estimators=300, 
        min_samples_leaf=5, 
        max_depth=14,
        class_weight="balanced_subsample", 
        n_jobs=-1, 
        random_state=7
    )
    rf.fit(X_train, y_train)
    
    # 3. Probability Calibration
    print("Calibrating probabilities...")
    calibrated_rf = CalibratedClassifierCV(estimator=rf, cv="prefit", method="isotonic")
    calibrated_rf.fit(X_calib, y_calib)
    
    # 4. Export Artifacts
    model_payload = {
        "cal": calibrated_rf,
        "rf": rf,
        "feats": X_COLS,
        "schema_hash": SCHEMA_HASH
    }
    
    model_path = os.path.join(out_dir, "model.joblib")
    joblib.dump(model_payload, model_path)
    
    with open(model_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        
    with open(os.path.join(out_dir, "model.sha256"), "w") as f:
        f.write(file_hash)
        
    print(f"Model saved to {model_path}")
    print(f"Model SHA-256: {file_hash}")
    
    # Save validation set for Surjakana
    val.to_parquet(os.path.join(out_dir, "val_holdout.parquet"))
    
if __name__ == "__main__":
    train_model()
