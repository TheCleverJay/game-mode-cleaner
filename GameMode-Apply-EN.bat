@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Game Mode Cleaner - Apply
echo.
echo === Game Mode Cleaner - APPLY ===
echo Will stop matched interrupters only. Never-kill + exclusions stay.
echo Does not promise higher FPS.
echo.
set /p CONFIRM=Type Y to apply, anything else cancels: 
if /I not "%CONFIRM%"=="Y" (
  echo Cancelled.
  pause
  exit /b 0
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\GameModeCleaner.ps1" -Apply -Lang en
echo.
echo Relaunch apps from the Start Menu if needed.
pause
