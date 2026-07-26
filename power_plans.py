import subprocess
import logging
import re
import ctypes

logger = logging.getLogger(__name__)

OEM_ENCODING = f"cp{ctypes.windll.kernel32.GetOEMCP()}"


def get_power_plans() -> list[dict]:
    try:
        result = subprocess.run(
            ["powercfg", "/l"],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
    except subprocess.CalledProcessError as e:
        logger.error("powercfg /l failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Failed to list power plans: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("powercfg command not found")
        raise RuntimeError("powercfg command not found") from e

    plans = []
    for line in result.stdout.splitlines():
        match = re.search(r"([\da-fA-F\-]{36})", line)
        if not match:
            continue
        guid = match.group(1)
        name_match = re.search(r"\((.+?)\)", line)
        name = name_match.group(1) if name_match else guid
        active = "*" in line
        plans.append({"guid": guid, "name": name, "active": active})

    return plans


def set_active_power_plan(guid: str) -> None:
    try:
        subprocess.run(
            ["powercfg", "/s", guid],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
        logger.info("Active power plan set to %s", guid)
    except subprocess.CalledProcessError as e:
        logger.error("powercfg /s failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Failed to set power plan {guid}: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("powercfg command not found")
        raise RuntimeError("powercfg command not found") from e


def get_active_power_plan_guid() -> str | None:
    try:
        result = subprocess.run(
            ["powercfg", "/getactivescheme"],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
    except subprocess.CalledProcessError as e:
        logger.error("powercfg /getactivescheme failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Failed to get active scheme: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("powercfg command not found")
        raise RuntimeError("powercfg command not found") from e

    match = re.search(r"([\da-fA-F\-]{36})", result.stdout)
    if match:
        return match.group(1)
    logger.warning("No GUID found in powercfg /getactivescheme output")
    return None


def disable_sleep(timeout_minutes: int = 0) -> None:
    try:
        subprocess.run(
            ["powercfg", "/change", "standby-timeout-ac", str(timeout_minutes)],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
        subprocess.run(
            ["powercfg", "/change", "standby-timeout-dc", str(timeout_minutes)],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
        logger.info("Sleep disabled (timeout=%d minutes, AC and DC)", timeout_minutes)
    except subprocess.CalledProcessError as e:
        logger.error("powercfg /change standby-timeout failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Failed to disable sleep: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("powercfg command not found")
        raise RuntimeError("powercfg command not found") from e


def keep_network_active(enable: bool) -> None:
    value = "1" if enable else "0"
    try:
        subprocess.run(
            [
                "powercfg", "/setacvalueindex",
                "SCHEME_CURRENT",
                "0012ee47-9041-4b5d-9b77-535fba8b1442",
                "0e0b6032-45fe-4a1b-bfba-9f3c0ae2e231",
                value,
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding=OEM_ENCODING,
        )
        logger.info("Network adapter sleep policy set to %s", value)
    except Exception as e:
        logger.warning("Failed to set network adapter sleep policy (best-effort): %s", e)
