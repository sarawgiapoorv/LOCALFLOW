@echo off
:: ══════════════════════════════════════════════════════════
::  LocalFlow — Silent Desktop Launcher
::  Elevates to Administrator and launches with no console.
:: ══════════════════════════════════════════════════════════

:: Check if already running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Launch LocalFlow without a visible console window
cd /d "%~dp0"
start "" pythonw main.py
exit
