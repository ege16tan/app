import subprocess
import ctypes
import logging

logger = logging.getLogger(__name__)


def shutdown_pc(delay_seconds: int = 0) -> None:
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be >= 0")
    try:
        result = subprocess.run(
            ["shutdown", "/s", "/t", str(delay_seconds)],
            check=True,
            capture_output=True,
            text=True,
            encoding="mbcs",
        )
        logger.info("Shutdown scheduled with %d second delay", delay_seconds)
    except subprocess.CalledProcessError as e:
        logger.error("Shutdown failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Shutdown failed: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("Shutdown command not found")
        raise RuntimeError("Shutdown command not found") from e


def restart_pc() -> None:
    try:
        result = subprocess.run(
            ["shutdown", "/r", "/t", "0"],
            check=True,
            capture_output=True,
            text=True,
            encoding="mbcs",
        )
        logger.info("Restart initiated")
    except subprocess.CalledProcessError as e:
        logger.error("Restart failed (exit %d): %s", e.returncode, e.stderr.strip())
        raise RuntimeError(f"Restart failed: {e.stderr.strip()}") from e
    except FileNotFoundError as e:
        logger.error("Restart command not found")
        raise RuntimeError("Restart command not found") from e


def sleep_pc() -> None:
    try:
        result = ctypes.windll.powrprof.SetSuspendState(False, True, True)
        if result == 0:
            raise RuntimeError("SetSuspendState returned 0")
        logger.info("Sleep initiated")
    except Exception as e:
        logger.error("Sleep failed: %s", e)
        raise RuntimeError(f"Sleep failed: {e}") from e
