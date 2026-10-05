import os, warnings
import pandas as pd, numpy as np
from data.schema import X_COLS, FEATURES
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

def load_ransap():
    base_path = "/kaggle/input/ransap"
    if not os.path.exists(base_path): return pd.DataFrame()
    windows = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.csv'):
                try:
                    df_raw = pd.read_csv(os.path.join(root, file), on_bad_lines='skip')
                    if 'UNIX time in sec' in df_raw.columns and 'size' in df_raw.columns:
                        df_raw['ts_window'] = (df_raw['UNIX time in sec'] // 2) * 2
                        win_df = df_raw.groupby('ts_window').agg(write_bytes_rate=('size', lambda x: x.sum() / 2.0)).reset_index()
                        if 'Entropy #1' in df_raw.columns:
                            ent_df = df_raw.groupby('ts_window').agg(mean_entropy_sampled=('Entropy #1', 'mean'))
                            win_df = win_df.merge(ent_df, on='ts_window', how='left')
                        is_ransomware = 1 if 'ransomware' in root.lower() or 'ransomware' in file.lower() else 0
                        
                        df_mapped = pd.DataFrame(columns=X_COLS + ["run_id", "group_id", "source", "style", "mode", "phase", "scope", "scope_type", "ts", "label", "label_quality", "weight", "family"])
                        df_mapped['write_bytes_rate'] = win_df['write_bytes_rate']
                        if 'mean_entropy_sampled' in win_df.columns: df_mapped['mean_entropy_sampled'] = win_df['mean_entropy_sampled']
                        df_mapped['ts'] = win_df['ts_window']
                        df_mapped['label'] = is_ransomware
                        df_mapped['source'] = "ransap"
                        df_mapped['run_id'] = f"RANSAP_{file}"
                        df_mapped['group_id'] = f"RANSAP_{file}"
                        df_mapped['style'] = "ransap_malware" if is_ransomware else "ransap_benign"
                        df_mapped['mode'] = "attack" if is_ransomware else "benign"
                        df_mapped['label_quality'] = "weak"
                        df_mapped['weight'] = 0.5 
                        for col in FEATURES:
                            if col not in df_mapped.columns: df_mapped[col] = np.nan
                        windows.append(df_mapped)
                except Exception: pass
    return pd.concat(windows, ignore_index=True) if windows else pd.DataFrame()

def load_all_adapters():
    return load_ransap()
