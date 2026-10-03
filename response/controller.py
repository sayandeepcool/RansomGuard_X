import psutil, shutil, json, time, os, hashlib

VAULT_DIR = "/kaggle/working/RansomGuard_X/response/vault"
os.makedirs(VAULT_DIR, exist_ok=True)

def respond(pid, files_touched, cfg):
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        
        # 1. Allowlist Check
        if name in cfg.get("allowlist_proc", ["explorer.exe", "svchost.exe", "python"]):
            return f"Skipped: {name} is allowlisted"

        if cfg.get("dry_run", True):
            return f"DRY-RUN: Would suspend {name} ({pid}) and quarantine {len(files_touched)} files"

        # 2. Reversible Suspension (Never Kill)
        proc.suspend() 

        # 3. Secure File Vaulting
        manifest = []
        for p in files_touched:
            if os.path.exists(p):
                dst = os.path.join(VAULT_DIR, hashlib.sha1(p.encode()).hexdigest())
                shutil.move(p, dst)
                manifest.append((p, dst))

        manifest_path = os.path.join(VAULT_DIR, f"manifest_{int(time.time())}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)

        return f"CONTAINED: Suspended {name} ({pid}). {len(manifest)} files vaulted."
    except Exception as e:
        return f"Failed to respond to PID {pid}: {str(e)}"
