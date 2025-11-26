@echo off
REM Package client for distribution
REM Creates a ZIP file ready to share with users

echo ============================================
echo Packaging Client for Distribution
echo ============================================
echo.

REM Check if executable exists
if not exist dist\CloudStorageClient.exe (
    echo ERROR: CloudStorageClient.exe not found!
    echo Please run build_client.bat first.
    pause
    exit /b 1
)

REM Create distribution folder
echo Creating distribution package...
if exist dist\ClientPackage rmdir /s /q dist\ClientPackage
mkdir dist\ClientPackage

REM Copy files
echo Copying files...
copy dist\CloudStorageClient.exe dist\ClientPackage\
copy config.yaml dist\ClientPackage\
copy CLIENT_README.txt dist\ClientPackage\README.txt

REM Check if 7-Zip is available for better compression
where 7z >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Creating ZIP with 7-Zip...
    7z a -tzip dist\CloudStorageClient-Package.zip dist\ClientPackage\*
) else (
    REM Use PowerShell to create ZIP
    echo Creating ZIP with PowerShell...
    powershell -Command "Compress-Archive -Path 'dist\ClientPackage\*' -DestinationPath 'dist\CloudStorageClient-Package.zip' -Force"
)

if exist dist\CloudStorageClient-Package.zip (
    echo.
    echo ============================================
    echo Package Created Successfully!
    echo ============================================
    echo.
    echo Location: dist\CloudStorageClient-Package.zip
    echo.
    echo Contents:
    echo   - CloudStorageClient.exe
    echo   - config.yaml
    echo   - README.txt
    echo.
    echo IMPORTANT: Before distributing:
    echo 1. Edit config.yaml in the package to set your server URL
    echo 2. Test the executable on a clean machine
    echo 3. Provide your users with:
    echo    - The server URL
    echo    - Instructions to register an account
    echo.
) else (
    echo.
    echo ERROR: Failed to create package
)

pause
