import os
import time
import collections
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

EVENTS = collections.deque(maxlen=200_000)
PROC_DELTA = collections.deque(maxlen=5000)

class FileEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        dest = getattr(event, "dest_path", None)
        EVENTS.append((time.time(), event.event_type, event.src_path, dest))

def start_file_observer(paths):
    observer = Observer()
    handler = FileEventHandler()
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        observer.schedule(handler, path, recursive=True)
    observer.start()
    return observer

def sample_process_io(stop_event):
    prev_io = {}
    while not stop_event.is_set():
        now = time.time()
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                wb = proc.io_counters().write_bytes
                delta = wb - prev_io.get(proc.pid, wb)
                prev_io[proc.pid] = wb
                if delta > 0:
                    PROC_DELTA.append((now, proc.pid, proc.info["name"], delta))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        time.sleep(1.0)
