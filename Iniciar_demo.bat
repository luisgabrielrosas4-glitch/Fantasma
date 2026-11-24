@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py demo_python\main.py
) else (
  python demo_python\main.py
)
if errorlevel 1 pause
