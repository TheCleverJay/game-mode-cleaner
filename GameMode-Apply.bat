@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Game Mode Cleaner - Apply / 游戏模式清理 - 执行
echo.
echo ========================================
echo   游戏模式清理 - 执行
echo   Game Mode Cleaner - APPLY
echo ========================================
echo.
echo 将尝试关闭「干扰项名单」里匹配到的程序。
echo 系统关键进程、杀毒核心、以及 exclusions.txt 里的名字不会动。
echo Will stop matched interrupters only. Never-kill + exclusions are kept.
echo.
echo 不会保证更高帧数，只是尽量腾出内存/CPU。
echo Does not promise higher FPS.
echo.
set /p CONFIRM=确认执行清理？输入 Y 继续，其它键取消 / Type Y to apply, anything else cancels: 
if /I not "%CONFIRM%"=="Y" (
  echo.
  echo 已取消 / Cancelled.
  pause
  exit /b 0
)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\GameModeCleaner.ps1" -Apply -Lang zh
if errorlevel 1 (
  echo.
  echo [错误] PowerShell 运行失败。
  echo [ERROR] PowerShell failed.
)
echo.
echo 需要再开回来的软件，从开始菜单重新启动即可。
echo Relaunch apps from the Start Menu if you still need them.
echo.
pause
