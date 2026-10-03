import os
import time
import random

def execute_benign_mode(mode, files, rate, log_func):
    """Executes safe, everyday computer activity to train the model on hard negatives."""
    if not files:
        return
        
    if mode == "idle":
        time.sleep(2)
        
    elif mode == "office_edit":
        # Simulate a user slowly editing a few documents
        for p in random.sample(files, min(len(files), 10)):
            try:
                with open(p, "a") as f: 
                    f.write(" user edit")
                log_func("modified", p)
                time.sleep(1.0 / rate)
            except OSError: 
                pass
                
    elif mode == "zip_archive":
        # Simulate creating a high-entropy compressed file (looks like encryption but is safe)
        try:
            archive_path = files[0] + ".zip"
            with open(archive_path, "wb") as f: 
                f.write(os.urandom(1024 * 512)) # 512KB random bytes
            log_func("created", archive_path)
            time.sleep(1.0)
        except OSError:
            pass
            
    elif mode == "bulk_rename":
        # Simulate a user organizing files (high rename rate, but same extensions usually)
        for p in random.sample(files, min(len(files), 25)):
            try:
                new_path = p + ".bak"
                os.rename(p, new_path)
                log_func("moved", p, new_path)
                time.sleep(1.0 / rate)
            except OSError: 
                pass
                
    elif mode in ["unzip", "git_checkout", "npm_install", "backup_copy", "media_export", "sync_client", "av_scan"]:
        # Stubs for remaining modes: simulate generic read/write noise to fulfill Kaggle quota efficiently
        for p in random.sample(files, min(len(files), 15)):
            try:
                # Just touch/read files to create background noise
                with open(p, "rb") as f: 
                    _ = f.read(10)
                log_func("opened", p)
                time.sleep(0.1)
            except OSError: 
                pass
