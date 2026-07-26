import json
import logging

import power_plans
import paths

logger = logging.getLogger(__name__)

CONFIG_PATH = paths.get_config_path()


def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load config from %s: %s", CONFIG_PATH, e)
        raise RuntimeError(f"Failed to load config: {e}") from e


def _enrich_modes(modes: dict) -> list[dict]:
    active_guid = power_plans.get_active_power_plan_guid()
    result = []
    for mode_id, mode in modes.items():
        active = False
        if mode.get("plan_guid") is not None and mode["plan_guid"] == active_guid:
            active = True
        result.append({
            "id": mode_id,
            "label": mode.get("label", mode_id),
            "active": active,
            "plan_guid": mode.get("plan_guid"),
            "disable_sleep": mode.get("disable_sleep", False),
            "keep_net": mode.get("keep_net", False),
        })
    return result


def reload_modes() -> None:
    _load_config()
    logger.info("Modes reloaded from %s", CONFIG_PATH)


def get_all_modes() -> list[dict]:
    config = _load_config()
    modes = config.get("modes", {})
    return _enrich_modes(modes)


def activate_mode(mode_id: str) -> dict:
    config = _load_config()
    modes = config.get("modes", {})

    if mode_id not in modes:
        raise ValueError(f"Mode '{mode_id}' not found in config")

    mode = modes[mode_id]
    result = {
        "status": "activated",
        "mode_id": mode_id,
        "label": mode.get("label", mode_id),
        "plan_set": False,
        "sleep_disabled": False,
        "network_kept": False,
    }

    try:
        plan_guid = mode.get("plan_guid")
        if plan_guid is not None:
            power_plans.set_active_power_plan(plan_guid)
            result["plan_set"] = True

        if mode.get("disable_sleep", False):
            power_plans.disable_sleep(0)
            result["sleep_disabled"] = True

        if mode.get("keep_net", False):
            power_plans.keep_network_active(True)
            result["network_kept"] = True

        logger.info("Mode '%s' activated: %s", mode_id, result)
        return result

    except ValueError:
        raise
    except Exception as e:
        logger.error("Failed to activate mode '%s': %s", mode_id, e)
        raise RuntimeError(f"Failed to activate mode '{mode_id}': {e}") from e
