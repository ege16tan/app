import json
import socket
import logging

import paths

logger = logging.getLogger(__name__)

CONFIG_PATH = paths.get_config_path()


def _load_services() -> list[dict]:
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config.get("services", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Failed to load services from config: %s", e)
        return []


def check_service(host: str, port: int | None = None, timeout: int = 3) -> dict:
    result = {"online": False, "latency_ms": None}
    try:
        addr = (host, port) if port else (host, 80)
        sock = socket.create_connection(addr, timeout=timeout)
        sock.close()
        result["online"] = True
    except Exception:
        pass
    return result


def get_all_services() -> list[dict]:
    services = _load_services()
    if not services:
        return services
    for s in services:
        try:
            check = check_service(s.get("host", ""), s.get("port"))
            s["online"] = check["online"]
        except Exception:
            s["online"] = False
    return services
