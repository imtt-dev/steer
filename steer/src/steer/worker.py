import threading
import queue
import httpx
import json
import os
import atexit  # <--- NEW
from typing import Optional

from .config import settings

# Configuration
API_URL = "https://api.steer.ai/v1/capture"
API_KEY: Optional[str] = None

class BackgroundWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self._stop_event = threading.Event()
        # Ensure local storage exists (using settings from config)
        if not settings.steer_dir.exists():
            settings.steer_dir.mkdir(parents=True, exist_ok=True)
            
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()
        
        # AUTOMATIC CLEANUP: Ensures logs are flushed when script ends
        atexit.register(self.wait)

    def submit(self, payload: dict):
        self.queue.put(payload)

    def wait(self):
        """Block until all queued logs are processed."""
        if not self.queue.empty():
            print("\n[Steer] ⏳ Flushing logs to disk...")
            self.queue.join()

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                payload = self.queue.get(timeout=0.1) # Lower timeout for snappiness
                self._process_payload(payload)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Steer] Worker Error: {e}")

    def _process_payload(self, payload: dict):
        """Handles both local saving and remote transmission."""
        
        # 1. Save Locally (The Sidecar)
        try:
            with open(settings.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
                f.flush() # Force write to disk
                os.fsync(f.fileno()) # Force OS to commit to disk
        except Exception as e:
            print(f"[Steer] Failed to save local log: {e}")

        # 2. Send to API (if configured)
        if API_KEY:
            try:
                httpx.post(API_URL, json=payload, timeout=2.0)
            except Exception:
                pass 

_worker = BackgroundWorker()

def get_worker():
    return _worker