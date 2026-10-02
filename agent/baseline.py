import json
import os

def get_default_baseline():
    return {
        "mod_mu": 4.0,
        "mod_sd": 3.0,
        "wr_mu": 1024 * 50,
        "wr_sd": 1024 * 200
    }

def save_baseline(base_dict, path="baseline.json"):
    with open(path, "w") as f:
        json.dump(base_dict, f)

def load_baseline(path="baseline.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return get_default_baseline()
