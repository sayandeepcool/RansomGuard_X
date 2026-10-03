import sys
import os
import random

# Add project root to path so 'sim' module resolves correctly
sys.path.append("/kaggle/working/RansomGuard_X")

# Import the modes
from sim.attacks import inplace_fast, copy_delete
from sim.benign import execute_benign_mode

def get_test_files():
    target_dir = "/kaggle/working/RansomGuard_X/RansomGuard_Test"
    files = []
    for root, _, filenames in os.walk(target_dir):
        for fn in filenames:
            files.append(os.path.join(root, fn))
    random.shuffle(files)
    return files

def dummy_log(op, src, dest=None):
    pass 

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "inplace_fast"
    files = get_test_files()
    
    if mode == "inplace_fast":
        inplace_fast(files, rate=20, log_func=dummy_log)
    elif mode == "copy_delete":
        copy_delete(files, rate=20, log_func=dummy_log)
    elif mode == "rename_only":
        for p in files[:100]:
            try:
                os.rename(p, p + ".crypto")
            except OSError: 
                pass
    else:
        execute_benign_mode(mode, files, rate=5, log_func=dummy_log)
