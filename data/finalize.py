import numpy as np
import pandas as pd
from data.schema import FEATURES, NA_GROUPS

def finalize(df):
    # Replace inf with NaN so the model can handle it natively
    df[FEATURES] = df[FEATURES].replace([np.inf, -np.inf], np.nan)
    
    # Generate binary flags for missing groups
    for g, cols in NA_GROUPS.items():
        df[g] = df[cols].isna().any(axis=1).astype("int8")
        
    return df
