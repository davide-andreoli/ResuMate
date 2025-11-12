import subprocess
import time
from pathlib import Path


def main():
    root = Path(__file__).parent
    backend_path = root / "api" / "main.py"
    frontend_path = root / "pages" / "main.py"

    backend_proc = subprocess.Popen(
        [
            "uvicorn",
            f"{backend_path.stem}:app",
            "--app-dir",
            str(backend_path.parent),
            "--reload",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    time.sleep(2)

    frontend_proc = subprocess.Popen(
        ["streamlit", "run", str(frontend_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print("Backend and frontend started.")
    print("FastAPI → http://127.0.0.1:8000")
    print("Streamlit → http://127.0.0.1:8501")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
