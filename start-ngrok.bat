@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-ngrok.ps1"
if errorlevel 1 (
    echo.
    echo Ngrok berhenti dengan error. Tekan tombol apa saja untuk menutup jendela ini.
    pause >nul
)
