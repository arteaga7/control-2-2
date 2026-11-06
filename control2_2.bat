@echo off
setlocal

REM ---- Valores por defecto ----
set "DEF_MONTH=10. Octubre"
set "DEF_PATH=C:\SharePoints"

REM ---- Pedir argumentos ----
set "MONTH="
set /p "MONTH=Mes a revisar [%DEF_MONTH%]: "
if "%MONTH%"=="" set "MONTH=%DEF_MONTH%"

set "UNILEVER_PATH="
set /p "UNILEVER_PATH=Ruta de SharePoint [%DEF_PATH%]: "
if "%UNILEVER_PATH%"=="" set "UNILEVER_PATH=%DEF_PATH%"

REM ---- Limpiar comillas y "\" final ----
set "UNILEVER_PATH=%UNILEVER_PATH:"=%"
if "%UNILEVER_PATH:~-1%"=="\" set "UNILEVER_PATH=%UNILEVER_PATH:~0,-1%"

REM ---- Validar que la ruta exista ----
if not exist "%UNILEVER_PATH%\" (
    echo.
    echo [ERROR] La ruta no existe: %UNILEVER_PATH%
    pause
    exit /b 1
)

echo.
echo Ejecutando con:
echo   --month         "%MONTH%"
echo   --unilever_path "%UNILEVER_PATH%"
echo.

"%~dp0c2_2_bot2.exe" --month "%MONTH%" --unilever_path "%UNILEVER_PATH%"

echo.
pause
endlocal