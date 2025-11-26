import time
import os
import sys
from rich.console import Console
from .config import settings

console = Console()

def wait_for_rules():
    """
    Blocks execution until a new rule is detected in steer_rules.yaml.
    Used for interactive demos.
    """
    filepath = settings.rules_file
    
    console.print("\n[yellow]👀 Watching for rules...[/yellow] (Go to Dashboard)")
    
    last_mtime = 0
    if filepath.exists():
        last_mtime = os.path.getmtime(filepath)
    
    while True:
        time.sleep(1)
        if filepath.exists():
            current_mtime = os.path.getmtime(filepath)
            if current_mtime > last_mtime:
                console.print("\n[bold green]✨ Rule Change Detected! Rerunning...[/bold green]\n")
                return
