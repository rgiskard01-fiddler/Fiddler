@echo off
REM Slaughterhouse5 biosphere — local dashboard launcher (Windows)
REM The Python server auto-picks a free port (so an old instance can't block it)
REM and prints the URL; this launcher captures it and opens the right tab.
title Slaughterhouse5 biosphere
cd /d "%~dp0"
echo   Starting local server (auto port)...
echo   (Ctrl+C in this window stops it)
python -m bios.dashboard
pause
