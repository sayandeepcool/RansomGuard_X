from data.schema import A_MIN

def assign_label(t, w, gt_events, onset_ts, end_ts, phase):
    if phase == "benign": return 0, "clean"
    actor_evs = sum(1 for e in gt_events if t <= e[0] < (t + w) and e[1] == "attack_actor")
    if (abs(t - onset_ts) < 1.0) or (abs((t + w) - end_ts) < 1.0): return None, "ambiguous"
    if (t >= onset_ts) and ((t + w) <= end_ts + 2.0):
        return (1, "clean") if actor_evs >= A_MIN else (None, "ambiguous")
    if (t + w) <= onset_ts or t > (end_ts + 2.0): return 0, "clean"
    return None, "ambiguous"
