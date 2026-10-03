import pandas as pd
import numpy as np
import joblib
import hashlib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
try:
    from sklearn.frozen import FrozenEstimator
    use_frozen = True
except ImportError:
    use_frozen = False
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.schema import X_COLS, SCHEMA_HASH

def train_model(train, calib, out_dir="/kaggle/working/RansomGuard_X/ml"):
    os.makedirs(out_dir, exist_ok=True)
    
    X_train, y_train = train[X_COLS], train['label']
    X_calib, y_calib = calib[X_COLS], calib['label']
    
    rf = RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_depth=14,
                                class_weight="balanced_subsample", n_jobs=-1, random_state=7)
    rf.fit(X_train, y_train)
    
    # Safety Check: Calibration requires >1 class
    if y_calib.nunique() > 1:
        if use_frozen:
            calibrated_rf = CalibratedClassifierCV(estimator=FrozenEstimator(rf), method="isotonic")
        else:
            calibrated_rf = CalibratedClassifierCV(estimator=rf, cv="prefit", method="isotonic")
        calibrated_rf.fit(X_calib, y_calib)
    else:
        print("\n[WARNING] Calibration set contains only 1 class. Skipping probability calibration for prototype.\n")
        calibrated_rf = rf # Fallback to uncalibrated RF
    
    model_payload = {"cal": calibrated_rf, "rf": rf, "feats": X_COLS, "schema_hash": SCHEMA_HASH}
    model_path = os.path.join(out_dir, "model.joblib")
    joblib.dump(model_payload, model_path)
    
    with open(model_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(out_dir, "model.sha256"), "w") as f:
        f.write(file_hash)
        
    print(f"Model saved to {model_path} (SHA-256: {file_hash})")
