@echo off
echo ============================================================
echo CSC-455-HOMELAB-PROJECT-CLOUD - FORCE WIPE (Windows)
echo ============================================================
echo.
echo WARNING: This will FORCE DELETE everything:
echo   - ALL user accounts
echo   - ALL files and folders
echo   - ALL encryption keys
echo   - ALL settings
echo.
echo Make sure to CLOSE the server first!
echo.
pause

echo.
echo ============================================================
echo Killing all Python processes...
echo ============================================================
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 2 >nul

echo.
echo ============================================================
echo Deleting database...
echo ============================================================
if exist "server\instance\csc455_homelab.db" (
    del /F /Q "server\instance\csc455_homelab.db"
    if exist "server\instance\csc455_homelab.db" (
        echo FAILED: Database still exists!
        echo The file may be locked. Try:
        echo   1. Restart your computer
        echo   2. Run this script as Administrator
    ) else (
        echo SUCCESS: Database deleted (ALL ACCOUNTS REMOVED^)
    )
) else (
    echo Database not found
)

echo.
echo ============================================================
echo Deleting uploaded files...
echo ============================================================
if exist "uploads" (
    rmdir /S /Q "uploads"
    mkdir "uploads"
    echo SUCCESS: Uploads folder wiped
) else (
    echo Uploads folder not found
    mkdir "uploads"
)

echo.
echo ============================================================
echo Deleting encryption keys...
echo ============================================================
if exist "%USERPROFILE%\.csc455_homelab\keys" (
    rmdir /S /Q "%USERPROFILE%\.csc455_homelab\keys"
    echo SUCCESS: Encryption keys deleted
) else (
    echo Keys not found
)

echo.
echo ============================================================
echo Deleting settings...
echo ============================================================
if exist "%USERPROFILE%\.csc455_homelab\settings.json" (
    del /F /Q "%USERPROFILE%\.csc455_homelab\settings.json"
    echo SUCCESS: Settings deleted
) else (
    echo Settings not found
)

echo.
echo ============================================================
echo WIPE COMPLETE
echo ============================================================
echo.
echo All data has been removed:
echo   * ALL user accounts deleted
echo   * ALL files wiped
echo   * System reset to factory state
echo.
echo Next steps:
echo   1. Start the server (creates fresh database)
echo   2. Register a NEW account
echo.
pause
