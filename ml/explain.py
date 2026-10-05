import shap, joblib, os, sys
sys.path.append("/kaggle/working/RansomGuard_X")

def init_explainer():
    payload = joblib.load("/kaggle/working/RansomGuard_X/ml/model.joblib")
    rf = payload["rf"]
    explainer = shap.TreeExplainer(rf)
    joblib.dump(explainer, "/kaggle/working/RansomGuard_X/ml/explainer.joblib")
    print("SHAP TreeExplainer saved to ml/explainer.joblib.")

if __name__ == "__main__":
    init_explainer()
