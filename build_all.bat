@echo off
REM Complete build script - builds both client and server executables

echo ============================================
echo Cloud Storage - Complete Build
echo ============================================
echo.
echo This will build both client and server executables.
echo.
pause

REM Build client
echo.
echo [1/2] Building Client Executable...
echo.
call deployment\build_client.bat

REM Build server  
echo.
echo [2/2] Building Server Executable...
echo.
call deployment\build_server.bat

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo.
echo Executables created in dist\ folder:
if exist dist\CloudStorageClient.exe (
    echo   [√] CloudStorageClient.exe
) else (
    echo   [X] CloudStorageClient.exe - FAILED
)
if exist dist\CloudStorageServer.exe (
    echo   [√] CloudStorageServer.exe
) else (
    echo   [X] CloudStorageServer.exe - FAILED
)
echo.

pause
