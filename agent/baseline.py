import numpy as np
from data.schema import W, STEP

def get_default_baseline():
    return {"mod_rate_mean": 0.0, "mod_rate_std": 1.0, "write_rate_mean": 0.0, "write_rate_std": 100000.0}

def fit_simulator_baseline(events, io_deltas, t_start, t_end):
    mod_rates, write_rates = [], []
    t = t_start
    while t + W <= t_end:
        win_evs = [e for e in events if t <= e[0] < t + W]
        win_io = [d for d in io_deltas if t <= d[0] < t + W]
        mod_rates.append(sum(1 for e in win_evs if e[1] in ["modified"]) / W)
        write_rates.append(sum(d[3] for d in win_io) / W)
        t += STEP
    return {
        "mod_rate_mean": float(np.mean(mod_rates)) if mod_rates else 0.0,
        "mod_rate_std": float(np.std(mod_rates)) if mod_rates and np.std(mod_rates) > 0 else 1.0,
        "write_rate_mean": float(np.mean(write_rates)) if write_rates else 0.0,
        "write_rate_std": float(np.std(write_rates)) if write_rates and np.std(write_rates) > 0 else 100000.0
    }
