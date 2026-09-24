@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%install-windows.ps1"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%PS_SCRIPT%' -ErrorAction SilentlyContinue"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
