import os, time, random, shutil
def execute_benign_mode(mode, files, rate, log_func=None):
    if not files: return
    if mode == "idle": time.sleep(4)
    elif mode == "office_edit":
        for p in random.sample(files, min(len(files), 12)):
            try:
                with open(p, "ab") as f: f.write(b"\n[auto-saved draft entry]")
                time.sleep(1.0 / rate)
            except OSError: pass
    elif mode == "zip_archive":
        try:
            with open(files[0] + ".archive.zip", "wb") as f: f.write(os.urandom(1024 * 256))
            time.sleep(0.5)
        except OSError: pass
    elif mode == "unzip":
        for p in random.sample(files, min(len(files), 10)):
            try:
                with open(p + ".unpacked", "wb") as f: f.write(b"decompressed payload data")
                time.sleep(0.05)
            except OSError: pass
    elif mode == "git_checkout":
        for p in random.sample(files, min(len(files), 25)):
            try:
                with open(p, "r+b") as f:
                    content = f.read(); f.seek(0); f.write(content)
                time.sleep(0.02)
            except OSError: pass
    elif mode == "npm_install":
        node_dir = os.path.join(os.path.dirname(files[0]), "node_modules_sim")
        os.makedirs(node_dir, exist_ok=True)
        for i in range(15):
            with open(os.path.join(node_dir, f"pkg_{i}.js"), "wb") as f: f.write(b"module.exports = {};")
            time.sleep(0.03)
    elif mode == "backup_copy":
        for p in random.sample(files, min(len(files), 15)):
            try:
                shutil.copy2(p, p + ".bak_copy"); time.sleep(0.05)
            except OSError: pass
    elif mode == "media_export":
        for p in random.sample(files, min(len(files), 5)):
            try:
                with open(p + ".mp4_sim", "wb") as f: f.write(os.urandom(1024 * 128))
                time.sleep(0.2)
            except OSError: pass
    elif mode == "bulk_rename":
        for p in random.sample(files, min(len(files), 30)):
            try:
                os.rename(p, p + ".renamed"); time.sleep(1.0 / rate)
            except OSError: pass
    elif mode == "sync_client":
        for p in random.sample(files, min(len(files), 15)):
            try:
                with open(p, "rb") as f: _ = f.read(512)
                time.sleep(0.05)
            except OSError: pass
    elif mode == "av_scan":
        for p in files[:40]:
            try:
                with open(p, "rb") as f: _ = f.read()
                time.sleep(0.01)
            except OSError: pass
