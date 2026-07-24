import subprocess
import ctypes

def shutdown_pc(delay_seconds: int = 0):
    """
    Shuts down the PC with a specified delay.
    :param delay_seconds: Time to wait before shutting down in seconds.
    """
    subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)], check=True)

def restart_pc():
    """
    Restarts the PC immediately.
    """
    subprocess.run(["shutdown", "/r", "/t", "0"], check=True)

def sleep_pc():
    """
    Puts the PC into sleep mode (Suspend to RAM).
    """
    # SetSuspendState(Hibernate, ForceSuspension, CrashDump)
    # False = Sleep (Suspend to RAM), True = Force, True = Wakeup events enabled
    ctypes.windll.powrprof.SetSuspendState(False, True, True)
