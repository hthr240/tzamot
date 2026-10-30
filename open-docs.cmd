@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0open-docs.ps1"
if errorlevel 1 pause
