"""run_app.py: Lanzador de Streamlit para PyInstaller."""
import sys
from pathlib import Path
from streamlit.web import cli as stcli

# Fuerza a PyInstaller a incluir lo que usa app.py
import dotenv
import tkinter
import tkinter.filedialog
import PIL  # noqa: F401

if __name__ == "__main__":
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    sys.argv = [
        "streamlit", "run", str(base / "app.py"),
        "--global.developmentMode=false",
        "--server.headless=false",
    ]
    sys.exit(stcli.main())
