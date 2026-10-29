@echo off
setlocal

set "REQUIREMENTS=%~dp0requirements.txt"
if /i "%~1"=="music" set "REQUIREMENTS=%~dp0requirements-music.txt"

call python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto install
)
call py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto install
)

echo Python was not found. Install Python 3.11 or newer and add it to PATH.
goto failed

:install
call %PYTHON_CMD% -m pip install --upgrade -r "%REQUIREMENTS%"
if errorlevel 1 goto failed

echo.
echo Python dependencies installed successfully.
if /i "%~1"=="music" echo Music playback also needs FFmpeg and Deno on PATH. See README.md.
pause
exit /b 0

:failed
echo Installation failed. Check the message above.
pause
exit /b 1
