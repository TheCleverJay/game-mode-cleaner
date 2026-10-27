@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Game Mode Cleaner - Preview / 游戏模式清理 - 预览
echo.
echo ========================================
echo   游戏模式清理 - 预览（不会关闭任何程序）
echo   Game Mode Cleaner - PREVIEW (safe)
echo ========================================
echo.
echo 这一步只查看会动到哪些程序，不会真正关闭。
echo This only lists targets; nothing will be stopped.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\GameModeCleaner.ps1" -Lang zh
if errorlevel 1 (
  echo.
  echo [错误] PowerShell 运行失败。可尝试：右键本文件 → 以管理员身份运行（通常不需要）。
  echo [ERROR] PowerShell failed. Try: right-click → Run as administrator (usually not needed).
)
echo.
echo 若名单不对，请编辑 exclusions.txt（把不想关的程序名加进去）。
echo To keep an app running, add its process name to exclusions.txt
echo.
pause
