@echo off
echo Restarting Windows Explorer...
taskkill /f /im explorer.exe
timeout /t 2 >nul
start explorer.exe
echo Done.