@echo off
chcp 65001 >nul
title PPT Live Preview

rem ============================================================
rem  PPT Live Preview - one-click launcher for the SVG live editor
rem
rem  Usage: copy this file into any course project root (the folder
rem         that contains svg_output\) and double-click it.
rem         It auto-opens your browser. Keep the console window OPEN.
rem         Press Ctrl+C to stop the server.
rem  The filename does not matter; rename it if you like.
rem ============================================================

rem dp0 always ends with a backslash. Strip it, otherwise the
rem trailing backslash-quote gets escaped and swallows later args.
set "PROJ=%~dp0"
set "PROJ=%PROJ:~0,-1%"

rem Assumes layout <PPT_ROOT>\projects\<set>\<project>\
rem so three levels up from the project root is the ppt-master clone.
set "ROOT=%~dp0..\..\.."
set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"

if not exist "%PY%" (
  echo [ERROR] Python not found at:
  echo         %PY%
  echo         Edit the PY line inside this .bat to your python.exe path.
  echo.
  pause
  exit /b 1
)

if not exist "%PROJ%\svg_output" (
  echo [ERROR] No svg_output folder found in:
  echo         %PROJ%
  echo         Put this .bat into a course project root and try again.
  echo.
  pause
  exit /b 1
)

echo ============================================
echo  PPT Live Preview Server
echo  Project: %PROJ%
echo ============================================
echo.
echo  Starting ... keep this window OPEN.
echo  The real URL is written to:
echo    live_preview\lock.json
echo  Press Ctrl+C to stop the server.
echo.

"%PY%" "%ROOT%\skills\ppt-master\scripts\svg_editor\server.py" "%PROJ%" --live --timeout 0

echo.
echo Server stopped.
pause
