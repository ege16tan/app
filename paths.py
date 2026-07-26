import os
import sys


def get_base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path() -> str:
    return os.path.join(get_base_path(), "config.json")
