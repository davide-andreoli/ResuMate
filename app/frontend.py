import subprocess
from pathlib import Path


def main():
    app_path = Path(__file__).parent / "frontend" / "main.py"
    subprocess.run(["streamlit", "run", str(app_path)], check=True)


if __name__ == "__main__":
    main()
