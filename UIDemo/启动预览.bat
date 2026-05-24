@echo off
chcp 65001 >nul
echo Starting preview...

set "ROOT=F:\CodeWorkSpace\PrintServer-V1\UIDemo"

start "" "%ROOT%\index.html"

echo.
echo Preview opened in browser.
echo Close this window when done.
timeout /t 3 >nul
