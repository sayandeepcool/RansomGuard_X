import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

def split_dataset(df):
    TEST_STYLES = {"intermittent", "honeypot_avoid", "sync_client"}
    is_test = df['style'].isin(TEST_STYLES)
    test = df[is_test].copy()
    dev = df[~is_test].reset_index(drop=True)

    unique_groups = dev['group_id'].nunique()
    if unique_groups < 7:
        raise RuntimeError(f"CRITICAL ERROR: Only {unique_groups} groups found. The campaign must complete successfully to ensure leak-free splits.")

    strat = dev['source'] + "_" + dev['label'].astype(str)
    sgkf = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=42)
    folds = list(sgkf.split(dev, strat, dev['group_id']))

    val_idx = folds[0][1]
    calib_idx = folds[1][1]
    train_idx = np.setdiff1d(np.arange(len(dev)), np.r_[val_idx, calib_idx])

    train = dev.iloc[train_idx].copy()
    calib = dev.iloc[calib_idx].copy()
    val = dev.iloc[val_idx].copy()

    assert len(set(train['group_id']) & set(val['group_id'])) == 0, "Leakage detected!"
    assert len(set(train['group_id']) & set(calib['group_id'])) == 0, "Leakage detected!"

    return train, calib, val, test
