@echo off
setlocal
title ChatPrint CLI - Windows Installer
echo ============================================================
echo           ChatPrint CLI - Windows Installer
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%scripts\install-windows.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] Could not find installer script: "%PS_SCRIPT%"
    echo Please make sure you run install.bat from the ChatPrint CLI folder.
    pause
    exit /b 1
)

echo Starting installation via PowerShell...
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%PS_SCRIPT%' -ErrorAction SilentlyContinue"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Installer exited with error code %ERRORLEVEL%.
)

echo.
pause
