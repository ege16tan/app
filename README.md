# PC Power Control Backend

Lightweight Windows REST server for remote power management.
Android app (Phase 2) sends commands via LAN.

## Quick Start

### 1. Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### 2. Configure
Edit `config.json`:
```json
{
  "pin": "1234",
  "port": 5000,
  "modes": {
    "download": { "label": "Download-Modus", "plan_guid": null, "disable_sleep": true, "keep_net": true },
    "silent": { "label": "Silent-Modus", "plan_guid": null, "disable_sleep": false, "keep_net": false }
  },
  "services": [
    { "id": "nas", "label": "NAS", "host": "192.168.1.100", "port": 80 }
  ]
}
```

Get a mode's `plan_guid` via `GET /power-plans` and set it to auto-switch on mode activation.

### 3. Run (Manually)
```powershell
.\venv\Scripts\python main.py
```
Dashboard: http://localhost:5000/

## Dashboard (Web UI)

The server serves a live dashboard at **http://localhost:5000/** showing:
- CPU / RAM usage
- Active power plan
- Active mode
- All configured modes (with activate button)
- Service health (online/offline per TCP check)
- Quick action buttons (Shutdown, Restart, Sleep)

## Setup as Background Service

### Automatic (recommended)
```powershell
# Install as Windows Task (auto-start on logon + startup):
.\setup_task.ps1 install

# Check status:
.\setup_task.ps1 status

# Remove:
.\setup_task.ps1 remove
```

### Manual via Task Scheduler
- **Trigger:** "At logon" or "At startup"
- **Action:** Start a program
  - **Program:** `C:\path\to\venv\Scripts\pythonw.exe`
  - **Arguments:** `C:\path\to\main.py`
  - **Start in:** `C:\path\to\project`
- **Run with highest privileges** (required for powercfg changes)

## Build Standalone EXE

```powershell
.\venv\Scripts\python build.py
```
Output: `dist\PCPowerControl.exe` (~15 MB)

The EXE runs the server in the background (no console window). Place it anywhere, `config.json` is read from the same folder.

### Installer
Compile `installer.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php):
```
iscc.exe installer.iss
```

## API Reference

All endpoints except `/status` and `/` require `X-PIN` header.

### Power Actions
```bash
# Shutdown (with optional delay)
curl -X POST "http://localhost:5000/shutdown" -H "X-PIN: 1234" -H "Content-Type: application/json" -d "{\"delay_seconds\": 30}"
# Restart
curl -X POST "http://localhost:5000/restart" -H "X-PIN: 1234"
# Sleep
curl -X POST "http://localhost:5000/sleep" -H "X-PIN: 1234"
```

### Power Plans
```bash
curl -X GET "http://localhost:5000/power-plans" -H "X-PIN: 1234"
curl -X POST "http://localhost:5000/power-plan/a1841308-3541-4fab-bc81-f71556f20b4a" -H "X-PIN: 1234"
```

### Modes (Generic Preset System)
```bash
curl -X GET "http://localhost:5000/modes" -H "X-PIN: 1234"
curl -X POST "http://localhost:5000/modes/download/activate" -H "X-PIN: 1234"
```

### Health Check (no PIN)
```bash
curl http://localhost:5000/status
```

## Adding New Modes

No code changes — just add to `config.json`:
```json
"gaming": {
  "label": "Gaming-Modus",
  "plan_guid": "GUID_HERE",
  "disable_sleep": true,
  "keep_net": false
}
```

## Verification
```powershell
# After switching a plan:
powercfg /getactivescheme

# Idle resource usage (expect < 1% CPU, < 50 MB RAM):
curl http://localhost:5000/status
```
