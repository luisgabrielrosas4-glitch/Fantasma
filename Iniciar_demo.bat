@echo off
cd /d "%~dp0"
set "PY=python"
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
%PY% -c "import pygame; assert getattr(pygame, 'IS_CE', False)" >nul 2>nul
if errorlevel 1 (
  echo Este prototipo requiere Pygame-ce.
  echo Instala las dependencias con: %PY% -m pip install -r requirements.txt
  pause
  exit /b 1
)
%PY% demo_python\main.py
if errorlevel 1 pause
