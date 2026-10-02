import math
import collections

def shannon(path, n=4096):
    try:
        with open(path, "rb") as f:
            b = f.read(n)
    except OSError:
        return None
    if len(b) < 256:
        return None
        
    c = collections.Counter(b)
    L = len(b)
    return -sum(v/L * math.log2(v/L) for v in c.values())
