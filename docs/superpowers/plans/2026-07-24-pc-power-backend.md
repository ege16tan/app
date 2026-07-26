# PC Power Control Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a lightweight Windows REST server for power management (Shutdown, Restart, Sleep, Power Plans) with PIN auth.

**Architecture:** FastAPI server using a service layer that wraps Windows `powercfg` and `shutdown` CLI tools and `ctypes` for system sleep.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, `psutil`, `pywin32` (optional/backup), `ctypes`.

## Global Constraints
- Python 3.11+
- FastAPI + Uvicorn
- `pywin32` / `ctypes` for Windows Power APIs
- `subprocess` + `powercfg` CLI for Power-Plan-Management
- Idle Resources: < 1% CPU, < 50MB RAM
- Deployment: Windows Task Scheduler (`pythonw.exe`)
- Auth: `X-PIN` header via `secrets.compare_digest()`

---

## File Structure
- `config.json`: Configuration (PIN, port, plan GUID).
- `requirements.txt`: Dependencies.
- `main.py`: API routes and FastAPI app.
- `auth.py`: PIN validation logic.
- `power_manager.py`: Service layer for OS power actions.
- `docs/backup-native-api.md`: Reference for native API calls.
- `README.md`: Setup and curl examples.

---

### Task 1: Project Scaffolding & Config
**Files:**
- Create: `requirements.txt`
- Create: `config.json`

**Interfaces:**
- Produces: `config.json` with `{"pin": "1234", "port": 5000, "download_mode_plan_guid": null}`

- [ ] **Step 1: Create `requirements.txt`**
```text
fastapi
uvicorn
psutil
```
- [ ] **Step 2: Create `config.json`**
```json
{
  "pin": "1234",
  "port": 5000,
  "download_mode_plan_guid": null
}
```
- [ ] **Step 3: Commit**
```bash
git add requirements.txt config.json
git commit -m "feat: initial project scaffolding and config"
```

---

### Task 2: Power Manager Service Layer (Core Actions)
**Files:**
- Create: `power_manager.py`

**Interfaces:**
- Produces: 
  - `shutdown_pc(delay: int)`
  - `restart_pc()`
  - `sleep_pc()`

- [ ] **Step 1: Implement `shutdown_pc` and `restart_pc` using `subprocess`**
```python
import subprocess
import ctypes

def shutdown_pc(delay_seconds: int = 0):
    subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)], check=True)

def restart_pc():
    subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
```
- [ ] **Step 2: Implement `sleep_pc` using `ctypes`**
```python
def sleep_pc():
    # SetSuspendState(Hibernate, ForceSuspension, CrashDump)
    # False = Sleep (Suspend to RAM), True = Force, True = Wakeup events enabled
    ctypes.windll.powrprof.SetSuspendState(False, True, True)
```
- [ ] **Step 3: Commit**
```bash
git add power_manager.py
git commit -m "feat: implement core power actions in service layer"
```

---

### Task 3: Power Plan Management
**Files:**
- Modify: `power_manager.py`

**Interfaces:**
- Produces: 
  - `get_power_plans() -> list[dict]`
  - `set_power_plan(guid: str)`
  - `ensure_download_mode_plan(config_path: str) -> str`

- [ ] **Step 1: Implement `get_power_plans` parsing `powercfg /list`**
```python
import subprocess
import re

def get_power_plans():
    result = subprocess.run(["powercfg", "/list"], capture_output=True, text=True)
    plans = []
    # Pattern: GUID (Name)
    matches = re.findall(r'([\w-]+)\s+\(([^)]+)\)', result.stdout)
    for guid, name in matches:
        plans.append({"guid": guid, "name": name})
    return plans
```
- [ ] **Step 2: Implement `set_power_plan`**
```python
def set_power_plan(guid: str):
    subprocess.run(["powercfg", "/setactive", guid], check=True)
```
- [ ] **Step 3: Implement `ensure_download_mode_plan`**
```python
import json

def ensure_download_mode_plan(config_path: str) -> str:
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    guid = config.get("download_mode_plan_guid")
    if guid:
        return guid

    # 1. Duplicate Balanced Scheme
    # Note: Balanced GUID is usually 381b4222-f694-41f0-9685-ff5596c32cce
    balanced_guid = "381b4222-f694-41f0-9685-ff5596c32cce"
    res = subprocess.run(["powercfg", "/duplicatescheme", balanced_guid], capture_output=True, text=True)
    # Extract GUID from output "Power Scheme GUID: XXXX..."
    new_guid = re.search(r'([a-f0-9-]{36})', res.stdout).group(1)
    
    # 2. Rename
    subprocess.run(["powercfg", "/changename", new_guid, "Download Modus"], check=True)
    
    # 3. Set Network/USB to never sleep (AC)
    # Example: Network adapter sleep (generic)
    subprocess.run(["powercfg", "/setacvalueindex", new_guid, "fec29850-213a-415e-8515-4c9406334911", "253a150d-c54c-47d4-a060-6d45a1886021", "0"], check=True)
    
    # 4. Persist
    config["download_mode_plan_guid"] = new_guid
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    return new_guid
```
- [ ] **Step 4: Commit**
```bash
git add power_manager.py
git commit -m "feat: implement power plan management"
```

---

### Task 4: Authentication Layer
**Files:**
- Create: `auth.py`

**Interfaces:**
- Produces: `verify_pin(provided_pin: str) -> bool`

- [ ] **Step 1: Implement PIN check using `secrets.compare_digest`**
```python
import secrets
import json

def verify_pin(provided_pin: str) -> bool:
    with open("config.json", "r") as f:
        config = json.load(f)
    return secrets.compare_digest(provided_pin, config.get("pin", ""))
```
- [ ] **Step 2: Commit**
```bash
git add auth.py
git commit -m "feat: implement secure PIN authentication"
```

---

### Task 5: API Endpoints (FastAPI)
**Files:**
- Create: `main.py`

**Interfaces:**
- Consumes: `auth.verify_pin`, `power_manager.*`

- [ ] **Step 1: Setup FastAPI and PIN dependency**
```python
from fastapi import FastAPI, Header, HTTPException, Depends
from auth import verify_pin
import power_manager
import psutil
import os

app = FastAPI()

async def pin_required(x_pin: str = Header(None)):
    if not x_pin or not verify_pin(x_pin):
        raise HTTPException(status_code=401, detail="Invalid or missing PIN")
    return x_pin
```
- [ ] **Step 2: Implement Power Endpoints**
```python
@app.post("/shutdown", dependencies=[Depends(pin_required)])
async def shutdown(delay_seconds: int = 0):
    power_manager.shutdown_pc(delay_seconds)
    return {"message": f"Shutting down in {delay_seconds}s"}

@app.post("/restart", dependencies=[Depends(pin_required)])
async def restart():
    power_manager.restart_pc()
    return {"message": "Restarting"}

@app.post("/sleep", dependencies=[Depends(pin_required)])
async def sleep():
    power_manager.sleep_pc()
    return {"message": "Sleeping"}
```
- [ ] **Step 3: Implement Plan Endpoints**
```python
@app.get("/power-plans", dependencies=[Depends(pin_required)])
async def list_plans():
    return power_manager.get_power_plans()

@app.post("/power-plan/{guid}", dependencies=[Depends(pin_required)])
async def set_plan(guid: str):
    power_manager.set_power_plan(guid)
    return {"message": f"Plan {guid} activated"}

@app.post("/power-plan/download-mode", dependencies=[Depends(pin_required)])
async def download_mode():
    guid = power_manager.ensure_download_mode_plan("config.json")
    power_manager.set_power_plan(guid)
    return {"message": "Download mode activated", "guid": guid}
```
- [ ] **Step 4: Implement `/status` endpoint**
```python
@app.get("/status")
async def status():
    process = psutil.Process(os.getpid())
    return {
        "status": "ok",
        "cpu_percent": psutil.cpu_percent(),
        "ram_mb": process.memory_info().rss / (1024 * 1024)
    }
```
- [ ] **Step 5: Commit**
```bash
git add main.py
git commit -m "feat: implement FastAPI endpoints"
```

---

### Task 6: Backup Doc & README
**Files:**
- Create: `docs/backup-native-api.md`
- Create: `README.md`

- [ ] **Step 1: Write `docs/backup-native-api.md`**
(Document `pywin32` and `ctypes` alternatives for shutdown/restart/sleep).
- [ ] **Step 2: Write `README.md`**
(Include: `pip install`, `powercfg` verification, Firewall port instructions, and Task Scheduler steps: `pythonw.exe` path, Trigger "At log on", Action "Start a program").
- [ ] **Step 3: Add curl examples**
`curl -X POST -H "X-PIN: 1234" http://localhost:5000/shutdown` etc.
- [ ] **Step 4: Commit**
```bash
git add docs/backup-native-api.md README.md
git commit -m "docs: add backup api guide and setup readme"
```
