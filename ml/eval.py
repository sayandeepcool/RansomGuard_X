import pandas as pd
import numpy as np
import joblib
import os
import json
from sklearn.metrics import roc_curve
import sys

sys.path.append("/kaggle/working/RansomGuard_X")
from data.schema import X_COLS

def evaluate_model(val_path="/kaggle/working/RansomGuard_X/ml/val_holdout.parquet", model_path="/kaggle/working/RansomGuard_X/ml/model.joblib"):
    print(f"Loading validation set and model...")
    val = pd.read_parquet(val_path)
    payload = joblib.load(model_path)
    calibrated_rf = payload["cal"]
    
    X_val, y_val = val[X_COLS], val['label']
    
    # Predict calibrated probabilities
    y_prob = calibrated_rf.predict_proba(X_val)[:, 1]
    
    # Calculate False Positive Rate, True Positive Rate, and Thresholds
    fpr, tpr, thresholds = roc_curve(y_val, y_prob)
    
    # Operational Threshold: Maximize TPR while keeping False Positives <= 0.1%
    target_fpr = 0.001 
    idx = np.where(fpr <= target_fpr)[0][-1] if len(np.where(fpr <= target_fpr)[0]) > 0 else 0
    op_threshold = thresholds[idx]
    op_tpr = tpr[idx]
    
    print(f"--- OPERATIONAL THRESHOLDS ---")
    print(f"Strict False Alert Budget (FPR): {fpr[idx]*100:.3f}%")
    print(f"Resulting Detection Rate (TPR): {op_tpr*100:.2f}%")
    print(f"Required Risk Score Threshold: {op_threshold:.4f}")
    
    # Save threshold configuration for the live Day 4 agent
    config = {"alert_threshold": float(op_threshold)}
    with open("/kaggle/working/RansomGuard_X/ml/thresholds.json", "w") as f:
        json.dump(config, f)
        
if __name__ == "__main__":
    evaluate_model()
