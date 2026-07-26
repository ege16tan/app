# Project: PC Power Control Backend

## Goal
Lightweight Windows REST server for remote power management. Android app (Phase 2) sends commands via LAN.

## Features
- **Power Actions**: Shutdown (with delay), Restart, Sleep.
- **Power Plans**: List and switch Windows power schemes.
- **Generic Modes System**: Presets (Download, Silent, etc.) defined in `config.json` — each can set plan, disable sleep, keep network active.
- **Security**: Protected by `X-PIN` header.
- **Resource Efficient**: < 1% CPU, < 50MB RAM idle.
- **Stealth Mode**: No console window (`pythonw.exe`), auto-starts via Task Scheduler.

## Tech Stack
- **Language**: Python 3.11+
- **API**: FastAPI + Uvicorn
- **OS Interface**: `subprocess` (`powercfg`, `shutdown`), `ctypes` (`powrprof.dll`)
- **Config**: `config.json` (modes extensible without code changes)

## Module Structure
| File | Responsibility |
|---|---|
| `main.py` | API routing, FastAPI app |
| `auth.py` | PIN verification (`X-PIN` header) |
| `power_actions.py` | Shutdown, Restart, Sleep via OS APIs |
| `power_plans.py` | List/switch power schemes via `powercfg` |
| `modes_engine.py` | Generic modes system (activate presets) |
| `config.json` | Configuration (PIN, port, mode definitions) |

## API Summary
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/shutdown` | PIN | Shut down PC (`{"delay_seconds": 0}`) |
| POST | `/restart` | PIN | Reboot PC |
| POST | `/sleep` | PIN | Suspend to RAM |
| GET | `/power-plans` | PIN | List power schemes |
| POST | `/power-plan/{guid}` | PIN | Activate a power scheme |
| GET | `/modes` | PIN | List configured modes |
| POST | `/modes/{id}/activate` | PIN | Activate a mode preset |
| GET | `/status` | None | Health check (CPU/RAM) |
