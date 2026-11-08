@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev-up.ps1" %*
if errorlevel 1 pause
