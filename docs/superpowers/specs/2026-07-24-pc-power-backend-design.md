# PC Power Control Backend Design (Phase 1)

## Overview
Lightweight Windows REST server for power management. Controlled via Android app (Phase 2) over LAN.

## Core Goals
- Power actions: Shutdown, Restart, Sleep.
- Power plan management: Read and switch Windows power schemes.
- Security: PIN-based authentication via `X-PIN` header.
- Efficiency: Idle < 1% CPU, < 50MB RAM.
- Stealth: Run via `pythonw.exe` through Windows Task Scheduler.

## Technical Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **OS Interface**: 
  - `subprocess` for `shutdown` and `powercfg`.
  - `ctypes` for `SetSuspendState` (Sleep).
- **Deployment**: Windows Task Scheduler (Trigger: Logon/Startup).

## Architecture

### Components
1. **API Layer (`main.py`)**: 
   - FastAPI routes.
   - Dependency injection for PIN authentication.
2. **Auth Layer (`auth.py`)**: 
   - Constant-time PIN comparison using `secrets.compare_digest()`.
3. **Service Layer (`power_manager.py`)**:
   - Abstracts Windows CLI/API calls.
   - Handles `subprocess.run` and `ctypes` calls.
4. **Config (`config.json`)**:
   - Stores `pin`, `port`, and `download_mode_plan_guid`.

### Endpoints
| Method | Path | Action | Auth |
|---|---|---|---|
| POST | `/shutdown` | System shutdown. Body: `{"delay_seconds": int}` | Yes |
| POST | `/restart` | System restart. | Yes |
| POST | `/sleep` | System sleep (Suspend to RAM). | Yes |
| GET | `/power-plans` | List GUIDs and names of available plans. | Yes |
| POST | `/power-plan/{guid}` | Activate specific power plan. | Yes |
| POST | `/power-plan/download-mode` | Create/Activate optimized "Download Mode" plan. | Yes |
| GET | `/status` | Health check + Process CPU/RAM usage. | No |

## Implementation Details

### Power Actions
- **Shutdown**: `shutdown /s /t <seconds>`
- **Restart**: `shutdown /r /t 0`
- **Sleep**: `ctypes.windll.powrprof.SetSuspendState(False, True, True)`
- **Plans**: Parse output of `powercfg /list`. Change via `powercfg /setactive <guid>`.

### Download Mode logic
1. Check if `config.json["download_mode_plan_guid"]` exists.
2. If no:
   - Duplicate balanced scheme: `powercfg /duplicatescheme <balanced_guid>`.
   - Rename to "Download Modus".
   - Set network/USB sleep settings to "Never" using `powercfg /setacvalueindex`.
   - Save new GUID to `config.json`.
3. Activate GUID via `powercfg /setactive`.

### Resource Monitoring
- Use `psutil` in `/status` endpoint to report `cpu_percent()` and `memory_info().rss`.

## Deployment & Setup
1. **Install**: `pip install -r requirements.txt`.
2. **Firewall**: Open selected port in Windows Firewall for Private Network.
3. **Task Scheduler**:
   - Trigger: "At log on" or "At startup".
   - Action: `pythonw.exe C:\path\to\main.py`.
   - Config: "Run whether user is logged in or not" (Verification needed for Session 0 sleep behavior).

## Backup Plan (Option 2)
If `subprocess` is insufficient, refer to `docs/backup-native-api.md` for full `pywin32` and `ctypes` implementation of power state transitions.
