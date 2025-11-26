import json
import os
import yaml
from typing import List, Dict, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .storage import rulebook

app = FastAPI(title="Steer Mission Control")

# CORS (Useful if you ever develop frontend separately again)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---

class TeachRequest(BaseModel):
    agent_name: str = "default_agent"
    rule_content: str
    category: str = "general"
    incident_id: Optional[str] = None

# --- API ROUTES ---

@app.get("/api/incidents")
def get_incidents():
    if not settings.log_file.exists():
        return {"incidents": []}
    
    incidents = []
    resolutions_path = settings.steer_dir / "resolutions.json"
    resolved_ids = []
    if resolutions_path.exists():
        try:
            resolved_ids = json.loads(resolutions_path.read_text())
        except: pass

    try:
        with open(settings.log_file, "r") as f:
            for line in f:
                try:
                    inc = json.loads(line)
                    if inc.get("id") in resolved_ids:
                        inc["status"] = "Resolved"
                    incidents.append(inc)
                except:
                    continue
    except Exception as e:
        print(f"Error reading logs: {e}")
        return {"incidents": []}
    
    return {"incidents": incidents[::-1]}

@app.get("/api/rules")
def get_rules():
    try:
        if not settings.rules_file.exists():
            return {"rules": {}}
        with open(settings.rules_file, "r") as f:
            data = yaml.safe_load(f) or {}
        return {"rules": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/teach")
def teach_agent(payload: TeachRequest):
    try:
        # 1. Save Rule
        rulebook.add_rule(
            agent_name=payload.agent_name,
            rule_content=payload.rule_content,
            category=payload.category
        )
        
        # 2. Resolve Incident
        if payload.incident_id:
            resolutions_path = settings.steer_dir / "resolutions.json"
            current_resolutions = []
            if resolutions_path.exists():
                try:
                    current_resolutions = json.loads(resolutions_path.read_text())
                except: pass
            
            if payload.incident_id not in current_resolutions:
                current_resolutions.append(payload.incident_id)
                with open(resolutions_path, "w") as f:
                    json.dump(current_resolutions, f, indent=2)
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- STATIC FILE SERVING (The Bundle) ---

# Calculate path to the bundled UI folder
UI_DIR = Path(__file__).parent / "ui"

if UI_DIR.exists():
    # 1. Serve Next.js static assets (_next folder)
    app.mount("/_next", StaticFiles(directory=UI_DIR / "_next"), name="next_assets")
    
    # 2. Catch-all for HTML (Single Page App routing)
    # We explicitly match "/" to serve index.html
    @app.get("/")
    async def read_index():
        return FileResponse(UI_DIR / "index.html")
        
    # Optional: Handle favicon if it exists
    if (UI_DIR / "favicon.ico").exists():
        @app.get("/favicon.ico")
        async def read_favicon():
            return FileResponse(UI_DIR / "favicon.ico")
