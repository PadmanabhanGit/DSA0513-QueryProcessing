import json
import os
import signal
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
STATE_FILE = BASE / "run_state.json"


def kill_pid(pid):
    try:
        if sys.platform == "win32":
            subprocess.check_call(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"Stopped process {pid}")
    except Exception as e:
        print(f"Unable to stop PID {pid}: {e}")


def main():
    if not STATE_FILE.exists():
        print("No run_state.json found. Nothing to stop.")
        return

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    app_pid = state.get("app_pid")
    mysql_pid = state.get("mysql_pid")

    if app_pid:
        kill_pid(app_pid)
    if mysql_pid:
        kill_pid(mysql_pid)

    try:
        STATE_FILE.unlink()
        print("Removed run_state.json")
    except Exception as e:
        print(f"Unable to remove state file: {e}")


if __name__ == "__main__":
    main()
