import os
import sys
import subprocess

DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
MAIN_SCRIPT = os.path.join(os.path.dirname(__file__), "main.py")

os.makedirs(DIST_DIR, exist_ok=True)

pyinstaller_args = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--noconsole",
    "--name", "PCPowerControl",
    "--distpath", DIST_DIR,
    "--workpath", os.path.join(os.path.dirname(__file__), "build"),
    "--specpath", os.path.join(os.path.dirname(__file__), "build"),
    "--add-data", f"{STATIC_DIR}{os.pathsep}static",
    "--clean",
    "--log-level", "INFO",
    MAIN_SCRIPT,
]

print("=" * 60)
print("Building PCPowerControl.exe...")
print("=" * 60)
print()

result = subprocess.run(pyinstaller_args, cwd=os.path.dirname(__file__))
if result.returncode != 0:
    print("Build failed with return code", result.returncode)
    sys.exit(1)

exe_path = os.path.join(DIST_DIR, "PCPowerControl.exe")
print()
print("=" * 60)
print("SUCCESS:", exe_path)
print("Size:", round(os.path.getsize(exe_path) / 1024 / 1024, 1), "MB")
print("=" * 60)
