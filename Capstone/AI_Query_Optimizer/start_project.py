import json
import os
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE = Path(__file__).resolve().parent
VENV_DIR = BASE / ".venv"
ENV_FILE = BASE / ".env"
ENV_EXAMPLE = BASE / ".env.example"
STATE_FILE = BASE / "run_state.json"
APP_SCRIPT = BASE / "app.py"
TRAIN_SCRIPT = BASE / "train_model.py"
REQUIREMENTS = BASE / "requirements.txt"
MODEL_FILE = BASE / "query_model.pkl"
MYSQL_BIN_DIR = os.environ.get("MYSQL_BIN_DIR")

if sys.platform == "win32":
    PYTHON_IN_VENV = VENV_DIR / "Scripts" / "python.exe"
else:
    PYTHON_IN_VENV = VENV_DIR / "bin" / "python"


def ensure_env_file():
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy2(ENV_EXAMPLE, ENV_FILE)
            print(f"Created .env from .env.example")
        else:
            print("Warning: .env.example missing. Create .env manually.")


def ensure_venv():
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print("Virtual environment already exists.")


def venv_python():
    if PYTHON_IN_VENV.exists():
        return str(PYTHON_IN_VENV)
    return sys.executable


def install_requirements():
    print("Installing Python dependencies...")
    subprocess.check_call([venv_python(), "-m", "pip", "install", "-r", str(REQUIREMENTS)])


def train_model():
    if MODEL_FILE.exists():
        print("Model file exists, skipping training.")
        return
    print("Training model and generating dataset...")
    subprocess.check_call([venv_python(), str(TRAIN_SCRIPT)])


def mysql_is_running():
    try:
        with socket.create_connection(("127.0.0.1", 3306), timeout=1):
            return True
    except OSError:
        return False


def find_mysql_bin():
    if MYSQL_BIN_DIR:
        path = Path(MYSQL_BIN_DIR)
        if path.exists():
            return path
    if sys.platform == "win32":
        candidates = [
            Path(r"C:/Program Files/MySQL/MySQL Server 9.7/bin"),
            Path(r"C:/Program Files/MySQL/MySQL Server 8.0/bin"),
            Path(r"C:/Program Files/MySQL/MySQL Server 5.7/bin"),
            Path(r"C:/Program Files/MariaDB 10.11/bin"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    which_mysql = shutil.which("mysql")
    if which_mysql:
        return Path(which_mysql).resolve().parent
    return None


def start_mysql_service():
    if mysql_is_running():
        print("MySQL is already running.")
        return None

    mysql_bin = find_mysql_bin()
    if not mysql_bin:
        print("Could not find MySQL binary path. Set MYSQL_BIN_DIR or install MySQL.")
        return None

    mysqld = mysql_bin / ("mysqld.exe" if sys.platform == "win32" else "mysqld")
    if not mysqld.exists():
        print(f"MySQL server binary not found in {mysql_bin}")
        return None

    print(f"Starting MySQL server from {mysqld}")
    if sys.platform == "win32":
        process = subprocess.Popen([
            str(mysqld),
            "--console",
        ], cwd=mysql_bin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        process = subprocess.Popen([
            str(mysqld),
            "--datadir=/var/lib/mysql",
        ], cwd=mysql_bin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(3)
    if mysql_is_running():
        print("MySQL started successfully.")
        return process.pid
    print("MySQL did not start successfully. Verify server installation.")
    return None


def start_flask_app():
    print("Starting Flask app...")
    proc = subprocess.Popen([
        venv_python(),
        str(APP_SCRIPT),
    ], cwd=str(BASE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0))
    time.sleep(3)
    print(f"Flask app started with PID {proc.pid}")
    return proc.pid


def save_state(app_pid, mysql_pid=None):
    state = {
        "app_pid": app_pid,
        "mysql_pid": mysql_pid,
        "started_at": time.time(),
    }
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f)
    print(f"Saved startup state to {STATE_FILE}")


def open_browser():
    url = "http://localhost:5000"
    print(f"Opening browser at {url}")
    webbrowser.open(url)


def main():
    ensure_env_file()
    ensure_venv()
    install_requirements()
    train_model()

    mysql_pid = None
    if not mysql_is_running():
        mysql_pid = start_mysql_service()
    else:
        print("MySQL server is already accessible on port 3306.")

    app_pid = start_flask_app()
    save_state(app_pid, mysql_pid)
    open_browser()
    print("Startup complete.")


if __name__ == "__main__":
    main()
