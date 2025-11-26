@echo off
REM Build script for Cloud Storage Server executable
REM This creates a standalone .exe for running the server on Windows

echo ========================================
echo Building Cloud Storage Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then install requirements: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install PyInstaller if not present
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build\server rmdir /s /q build\server
if exist dist\CloudStorageServer.exe del /q dist\CloudStorageServer.exe

REM Build the executable
echo.
echo Building executable...
echo This may take a few minutes...
echo.

cd deployment
pyinstaller --clean server.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    cd ..
    pause
    exit /b 1
)

cd ..

REM Check if build succeeded
if exist dist\CloudStorageServer.exe (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created at: dist\CloudStorageServer.exe
    echo Size: 
    for %%A in (dist\CloudStorageServer.exe) do echo %%~zA bytes
    echo.
    echo IMPORTANT: Before running in production:
    echo 1. Edit config.yaml and set a secure secret_key
    echo 2. Set debug: false in config.yaml
    echo 3. Configure firewall to allow port 5000
    echo 4. Consider using a reverse proxy with SSL
    echo.
    echo To run: dist\CloudStorageServer.exe
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED - Executable not found
    echo ========================================
)

pause
