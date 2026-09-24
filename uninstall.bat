@echo off
setlocal
title ChatPrint CLI - Windows Uninstaller
echo ============================================================
echo           ChatPrint CLI - Windows Uninstaller
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%scripts\uninstall-windows.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] Could not find uninstaller script: "%PS_SCRIPT%"
    echo Please make sure you run uninstall.bat from the ChatPrint CLI folder.
    pause
    exit /b 1
)

echo Starting uninstallation via PowerShell...
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%PS_SCRIPT%' -ErrorAction SilentlyContinue"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Uninstaller exited with error code %ERRORLEVEL%.
)

echo.
pause
