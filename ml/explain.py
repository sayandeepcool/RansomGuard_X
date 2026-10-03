import shap
import joblib
import pandas as pd
import os
import sys

sys.path.append("/kaggle/working/RansomGuard_X")

def init_explainer(model_path="/kaggle/working/RansomGuard_X/ml/model.joblib"):
    print("Loading base Random Forest for SHAP Explainability...")
    payload = joblib.load(model_path)
    rf = payload["rf"]
    
    # Initialize TreeExplainer
    explainer = shap.TreeExplainer(rf)
    
    out_path = "/kaggle/working/RansomGuard_X/ml/explainer.joblib"
    joblib.dump(explainer, out_path)
    print(f"SHAP Explainer saved to {out_path}")
        
if __name__ == "__main__":
    init_explainer()
