@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Game Mode Cleaner - Preview
echo.
echo === Game Mode Cleaner - PREVIEW (nothing will be stopped) ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\GameModeCleaner.ps1" -Lang en
echo.
echo Edit exclusions.txt to keep apps running (one process name per line).
pause
