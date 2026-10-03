import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

def split_dataset(df):
    TEST_STYLES = {"intermittent", "honeypot_avoid", "sync_client"}
    is_test = df['style'].isin(TEST_STYLES)
    test = df[is_test]
    dev = df[~is_test].reset_index(drop=True)

    unique_groups = dev['group_id'].nunique()

    # Strict Preprocessing Spec: StratifiedGroupKFold
    if unique_groups >= 7:
        strat = dev['source'] + "_" + dev['label'].astype(str)
        sgkf = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=7)
        folds = list(sgkf.split(dev, strat, dev['group_id']))

        val_idx = folds[0][1]
        calib_idx = folds[1][1]
        train_idx = np.setdiff1d(np.arange(len(dev)), np.r_[val_idx, calib_idx])

        train = dev.iloc[train_idx]
        calib = dev.iloc[calib_idx]
        val = dev.iloc[val_idx]
    else:
        print(f"\n[PROTOTYPE SMOKE-TEST FALLBACK] Only {unique_groups} groups found. Minimum 7 required by Phase H.")
        print("Using row-level stratified split for prototype testing only. NOT FOR FINAL METRICS.\n")
        
        strat = dev['label'] if dev['label'].nunique() > 1 else None
        train, rest = train_test_split(dev, train_size=0.7, random_state=7, stratify=strat)
        
        strat_rest = rest['label'] if rest['label'].nunique() > 1 else None
        calib, val = train_test_split(rest, train_size=0.5, random_state=7, stratify=strat_rest)

    return train, calib, val, test
