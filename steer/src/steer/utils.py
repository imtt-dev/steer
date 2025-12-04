import time
import os
import sys
from .config import settings

def wait_for_rules():
    """
    Blocks execution until a new rule is detected in steer_rules.yaml.
    Used for interactive demos.
    """
    filepath = settings.rules_file
    
    print("\nWaiting for rules... (Go to Dashboard)")
    
    last_mtime = 0
    if filepath.exists():
        last_mtime = os.path.getmtime(filepath)
    
    while True:
        time.sleep(1)
        if filepath.exists():
            current_mtime = os.path.getmtime(filepath)
            if current_mtime > last_mtime:
                print("\nRule Change Detected. Rerunning...\n")
                return