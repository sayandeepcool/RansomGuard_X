import os

ADAPTER_SPECS = {
    "RanSAP": {"path": "/kaggle/input/ransap-2022-ransomware-behavioral-features"},
    "SILRAD": {"path": "/kaggle/input/silrad-dataset"},
    "MLRan":  {"path": "/kaggle/input/mlran-dataset"}
}

def report_adapters():
    return {name: ("AVAILABLE" if os.path.exists(spec["path"]) else "NOT_AVAILABLE") for name, spec in ADAPTER_SPECS.items()}
