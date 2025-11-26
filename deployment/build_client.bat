@echo off
REM Build script for Cloud Storage Client executable
REM This creates a standalone .exe that users can double-click

echo ========================================
echo Building Cloud Storage Client
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
if exist build\client rmdir /s /q build\client
if exist dist\CloudStorageClient.exe del /q dist\CloudStorageClient.exe

REM Build the executable
echo.
echo Building executable...
echo This may take a few minutes...
echo.

cd deployment
pyinstaller --clean client.spec

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
if exist dist\CloudStorageClient.exe (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created at: dist\CloudStorageClient.exe
    echo Size: 
    for %%A in (dist\CloudStorageClient.exe) do echo %%~zA bytes
    echo.
    echo IMPORTANT: Before distributing to users:
    echo 1. Edit config.yaml and set the correct server_url
    echo 2. Test the executable on a clean machine
    echo 3. Users need to edit config.yaml with your server address
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED - Executable not found
    echo ========================================
)

pause
