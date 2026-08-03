@echo off
REM Slaughterhouse5 biosphere — local dashboard launcher (Windows)
REM Opens the live dashboard in your browser and starts the PULSE server.
title Slaughterhouse5 biosphere
cd /d "%~dp0"
echo.
echo   Slaughterhouse5 biosphere dashboard
echo   --------------------------------
echo   Starting local server on http://localhost:8753/
echo   (Ctrl+C in this window stops it)
echo.
start "" http://localhost:8753/
python -m bios.dashboard
pause
