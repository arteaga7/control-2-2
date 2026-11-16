'''app.py: Simple app to select folders and some parameters'''

from pathlib import Path
import streamlit as st
# import pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import filedialog

page_title = "Capgemini-Bots"
img_path = Path(__file__).resolve().parent
img_path = img_path / "images" / "unilever.png"

img = Image.open(img_path)
st.set_page_config(page_title=page_title, layout="wide",
                   page_icon=img)

# Title
st.title(page_title)


def get_root(path: str | Path, folder: str = "Unilever") -> Path | None:
    parts = Path(path).parts
    return Path(*parts[:parts.index(folder) + 1]) if folder in parts else None


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

st.write(st.session_state.get("folder", "No folder selected"))


# Columns-------------------------------------------------------
st.header("Select", divider="gray")
col1, col2, col3 = st.columns(3)
with col1:
    control = st.selectbox(
        label="Control", options=['OTB C2.2', 'OTB C3.2', 'OTB C5.2']
    )
with col2:
    month = st.selectbox(
        label="Month", options=['09. Sep', '10. Oct', '11. Nov']
    )
with col3:
    bot = st.selectbox(
        label="Bot", options=['Bot1', 'Bot2', 'Bot4', 'Bot6']
    )

# Image -----------------------------------------
st.header("Image", divider="blue")
st.image(img, width="stretch", caption="Image 1")
