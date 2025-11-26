@echo off
echo Starting CSC-455-Homelab-Project-Cloud Server...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start server
python -m server.app

pause
