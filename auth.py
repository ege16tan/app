import json
import logging
from fastapi import Header, HTTPException, Depends
from typing import Optional

import paths

logger = logging.getLogger(__name__)

CONFIG_PATH = paths.get_config_path()

_config_cache: Optional[dict] = None


def reload_config() -> dict:
    global _config_cache
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
        logger.info("Configuration reloaded successfully")
        return _config_cache
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load config: %s", e)
        raise


def _get_config() -> dict:
    if _config_cache is None:
        return reload_config()
    return _config_cache


def verify_pin(x_pin: str) -> bool:
    config = _get_config()
    stored_pin = config.get("pin", "")
    return x_pin == stored_pin


def pin_required(x_pin: str = Header(...)) -> None:
    if not verify_pin(x_pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    return None
