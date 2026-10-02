import os
import time
import random
import sys

def inplace_fast(target_dir, rate=20):
    """Simulates rapid inplace file encryption."""
    files = []
    for root, _, filenames in os.walk(target_dir):
        if "Honeypot" not in root:
            for fn in filenames:
                files.append(os.path.join(root, fn))
    
    random.shuffle(files)
    for filepath in files:
        try:
            size = os.path.getsize(filepath)
            with open(filepath, "r+b") as f:
                f.write(os.urandom(size))
            new_path = filepath + ".locked"
            os.rename(filepath, new_path)
            time.sleep(1.0 / rate)
        except OSError:
            pass

def zip_archive_benign(target_dir):
    """Simulates a benign high-entropy file creation."""
    archive_file = os.path.join(target_dir, "Documents", "backup.zip")
    with open(archive_file, "wb") as f:
        f.write(os.urandom(1024 * 1024 * 5))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "inplace_fast"
    target = "/kaggle/working/RansomGuard_X/RansomGuard_Test"
    if mode == "inplace_fast":
        inplace_fast(target)
    elif mode == "zip_archive":
        zip_archive_benign(target)
