@echo off
cd /d "%~dp0"

set "OUT=dist\CapgeminiBots"

uv pip install -r requirements.txt || goto :error

REM 1) App Streamlit (onedir) -> dist\CapgeminiBots\
uv run pyinstaller --noconfirm --onedir --name CapgeminiBots ^
  --collect-all streamlit --copy-metadata streamlit ^
  --add-data "app.py;." --add-data "images;images" ^
  run_app.py || goto :error

REM 2) Bots (onefile) -> en la misma carpeta que CapgeminiBots.exe
uv run pyinstaller --noconfirm --onefile --name bot2 --paths . --collect-all extract_msg --distpath "%OUT%" bot2.py || goto :error
uv run pyinstaller --noconfirm --onefile --name bot4 --paths . --collect-all extract_msg --distpath "%OUT%" bot4.py || goto :error

REM 3) .env junto a los .exe
copy /Y .env "%OUT%\.env" || goto :error

echo Listo: revisa la carpeta %OUT%\
pause
exit /b 0

:error
echo ERROR: la compilacion fallo.
pause
exit /b 1