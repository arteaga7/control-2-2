'''app.py: Simple app to select folders and some parameters to run bots.'''

import os
import subprocess
import sys
from pathlib import Path
import streamlit as st
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv

# Carpeta del .exe (al compilar) o del .py (en desarrollo)
if getattr(sys, "frozen", False):
    EXE_DIR = Path(sys.executable).resolve().parent
else:
    EXE_DIR = Path(__file__).resolve().parent

load_dotenv(EXE_DIR / ".env")

page_title = "Capgemini-Bots"
BASE_DIR = Path(__file__).resolve().parent      # imágenes empaquetadas
IMG_PATH = BASE_DIR / "images" / "unilever.png"

img = Image.open(IMG_PATH)
st.set_page_config(page_title=page_title, layout="wide",
                   page_icon=img)

# Title
st.title(page_title)


def get_root(path: str | Path, folder: str = "Unilever") -> Path | None:
    parts = Path(path).parts
    return Path(*parts[:parts.index(folder) + 1]) if folder in parts else None


if "folder" not in st.session_state:
    st.session_state["folder"] = None

if st.button("Select Unilever SharePoint"):
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    ruta = filedialog.askdirectory(master=root)
    root.destroy()

    if ruta:  # "" si el usuario cancela
        unilever = get_root(ruta)
        if unilever:
            st.session_state["folder"] = unilever.as_posix()
        else:
            st.error("Folder does not belong to 'Unilever SharePoint'")
            st.session_state["folder"] = None

folder = st.session_state["folder"]
unilever_path = Path(folder) if folder else None

st.write(folder or "No folder selected")

# Expander --------------------------------------
with st.expander("Clic here to show more details about Unilever SharePoint folder", expanded=False):
    # Image
    st.markdown(
        "**Note:** Unilever SharePoint is the syncronized folder for capgemini bots and it should contain the following folders:")
    img1 = Image.open(BASE_DIR / "images" / "sharepoint.png")
    st.image(img1, width="stretch", caption="Image 1")
# --------------------------------------

# Columns-------------------------------------------------------
st.header("Select", divider="gray")
col1, col2, col3 = st.columns(3)
with col1:
    control = st.selectbox(
        label="Control", options=['OTB C3.2', 'OTB C5.2', 'OTB C2.2']
    )
with col2:
    month = st.selectbox(
        label="Month", options=['7. Julio', '8. Agosto', '9. Septiembre', '10. Octubre']
    )
with col3:
    bot = st.selectbox(
        label="Bot", options=['Bot2', 'Bot4']
    )

# Run ------------------------------------------
st.header("Run")
if st.button(f"Run {bot}"):
    if bot == 'Bot4':
        st.write("Verifying inbox, please wait a few seconds...\n")
    folder = st.session_state.get("folder")
    if not folder:
        st.error("Select the Unilever SharePoint folder first.")
    else:
        if getattr(sys, "frozen", False):          # compilado → llama bot2.exe / bot4.exe
            script = EXE_DIR / f"{bot.lower()}.exe"
            cmd = [str(script)]
        else:                                      # desarrollo → python bot2.py
            script = EXE_DIR / f"{bot.lower()}.py"
            cmd = [sys.executable, str(script)]

        if not unilever_path.is_dir():
            st.error(f"Folder not found: {unilever_path}")
        elif not script.is_file():
            st.error(f"Script not found: {script}")
        else:
            cmd += ["--month", month,
                    "--control", control,
                    "--unilever_path", str(unilever_path),
                    "--bot", bot]
            with st.spinner(f"Running {bot}..."):
                result = subprocess.run(
                    cmd, capture_output=True, text=True, encoding="utf-8",
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            st.code(result.stdout or "(no output)")
            if result.returncode != 0:
                st.error("The bot finished with errors:")
                st.code(result.stderr)
            else:
                st.success(f"{bot} finished successfully.")
