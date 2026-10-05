import sys, json, joblib, os, time
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

sys.path.append("/kaggle/working/RansomGuard_X")
from data.schema import X_COLS, SCHEMA_HASH, validate_model_payload

def evaluate():
    payload = joblib.load("/kaggle/working/RansomGuard_X/ml/model.joblib")
    validate_model_payload(payload)
    cal = payload["cal"]

    data_dir = f"/kaggle/working/RansomGuard_X/data/out/v{SCHEMA_HASH}"
    val_df = pd.read_parquet(f"{data_dir}/val.parquet")
    test_path = f"{data_dir}/test.parquet"
    test_df = pd.read_parquet(test_path) if os.path.exists(test_path) else pd.DataFrame()
    eval_set = pd.concat([val_df, test_df], ignore_index=True) if len(test_df) > 0 else val_df

    if len(eval_set) == 0:
        print("ERROR: Evaluation set empty.")
        return

    X = eval_set[X_COLS].fillna(0)
    y = eval_set["label"].astype(int).values

    start_time = time.perf_counter()
    
    # SAFELY handle single-class prototype models
    if hasattr(cal, "predict_proba"):
        probs_raw = cal.predict_proba(X)
        probs = probs_raw[:, 1] if probs_raw.shape[1] > 1 else np.zeros(len(y))
    else:
        probs = np.zeros(len(y))
        
    inf_time_ms = ((time.perf_counter() - start_time) / len(X)) * 1000

    with open("/kaggle/working/RansomGuard_X/ml/thresholds.json", "r") as f:
        thresh = json.load(f)
        
    t_crit = thresh.get("T_crit", 0.5)
    preds = (probs >= t_crit).astype(int)

    if len(np.unique(y)) < 2:
        p, r, f1, pr_auc, roc_auc, brier = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        cm = [[len(y), 0], [0, 0]] if y[0] == 0 else [[0, 0], [0, len(y)]]
    else:
        p, r, f1, _ = precision_recall_fscore_support(y, preds, average="binary", zero_division=0)
        pr_auc = average_precision_score(y, probs)
        roc_auc = roc_auc_score(y, probs)
        brier = brier_score_loss(y, probs)
        cm_raw = confusion_matrix(y, preds)
        cm = cm_raw.tolist() if isinstance(cm_raw, np.ndarray) else [[0, 0], [0, 0]]

    report = {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": cm,
        "eval_samples": len(eval_set),
        "inference_latency_ms": round(inf_time_ms, 4)
    }

    os.makedirs("/kaggle/working/RansomGuard_X/ml", exist_ok=True)
    with open("/kaggle/working/RansomGuard_X/ml/metrics.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== MODEL EVALUATION METRICS ===")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    evaluate()
