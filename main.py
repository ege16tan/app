import json
import os
import logging
import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager
from typing import Literal

import auth
import power_actions
import power_plans
import modes_engine
import service_checker
import paths


BASE_DIR = paths.get_base_path()
CONFIG_PATH = paths.get_config_path()

LOG_FILE = os.path.join(BASE_DIR, "server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")

_process = psutil.Process(os.getpid())


class ServiceConfig(BaseModel):
    id: str
    label: str
    host: str
    port: int
    model_config = ConfigDict(extra="forbid")


class ModeConfig(BaseModel):
    label: str
    plan_guid: str | None = None
    disable_sleep: bool = False
    keep_net: bool = False
    model_config = ConfigDict(extra="forbid")


class ConfigModel(BaseModel):
    pin: str = Field(min_length=4, max_length=20)
    port: int = Field(ge=1, le=65535, default=5000)
    modes: dict[str, ModeConfig] = Field(default_factory=dict)
    services: list[ServiceConfig] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


def load_config() -> ConfigModel:
    with open(CONFIG_PATH, "r") as f:
        raw = json.load(f)
    return ConfigModel(**raw)

config = load_config()
PORT = config.port


class ShutdownRequest(BaseModel):
    delay_seconds: int = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    _process.cpu_percent(interval=0.1)
    logger.info("PC Power Control Backend starting on port %d", PORT)
    yield
    logger.info("PC Power Control Backend shutting down")


app = FastAPI(title="PC Power Control Backend", version="1.0.0", lifespan=lifespan)


dashboard_path = os.path.join(BASE_DIR, "static", "dashboard.html")
with open(dashboard_path, encoding="utf-8") as f:
    _dashboard_html = f.read()


@app.get("/", response_class=HTMLResponse)
async def api_dashboard():
    return _dashboard_html


@app.get("/api/dashboard")
async def api_dashboard_data():
    plans = power_plans.get_power_plans()
    active_plan = next((p for p in plans if p.get("active")), None)
    modes = modes_engine.get_all_modes()
    active_mode = next((m for m in modes if m.get("active")), None)
    services = service_checker.get_all_services()
    return {
        "status": "ok",
        "cpu_percent": round(_process.cpu_percent(interval=0.1), 1),
        "memory_mb": round(_process.memory_info().rss / 1024 / 1024, 1),
        "active_plan_name": active_plan.get("name") if active_plan else None,
        "active_plan_guid": active_plan.get("guid") if active_plan else None,
        "active_mode_id": active_mode.get("id") if active_mode else None,
        "active_mode_label": active_mode.get("label") if active_mode else None,
        "modes": modes,
        "services": services,
    }


@app.post("/shutdown")
async def api_shutdown(req: ShutdownRequest, _=Depends(auth.pin_required)):
    power_actions.shutdown_pc(req.delay_seconds)
    return {"status": "shutdown initiated", "delay_seconds": req.delay_seconds}


@app.post("/restart")
async def api_restart(_=Depends(auth.pin_required)):
    power_actions.restart_pc()
    return {"status": "restart initiated"}


@app.post("/sleep")
async def api_sleep(_=Depends(auth.pin_required)):
    power_actions.sleep_pc()
    return {"status": "sleep initiated"}


@app.get("/power-plans")
async def api_list_power_plans(_=Depends(auth.pin_required)):
    return power_plans.get_power_plans()


@app.post("/power-plan/{guid}")
async def api_set_power_plan(guid: str, _=Depends(auth.pin_required)):
    power_plans.set_active_power_plan(guid)
    return {"status": "power plan changed", "guid": guid}


@app.get("/modes")
async def api_list_modes(_=Depends(auth.pin_required)):
    return modes_engine.get_all_modes()


@app.post("/modes/{mode_id}/activate")
async def api_activate_mode(mode_id: str, _=Depends(auth.pin_required)):
    try:
        result = modes_engine.activate_mode(mode_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def api_status():
    return {
        "status": "ok",
        "cpu_percent": round(_process.cpu_percent(interval=0.1), 1),
        "memory_mb": round(_process.memory_info().rss / 1024 / 1024, 1),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
