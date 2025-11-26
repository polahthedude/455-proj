@echo off
echo Starting CSC-455-Homelab-Project-Cloud Client...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start client
python -m client.gui.main_window

pause
