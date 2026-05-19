@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "WEB_DIR=%ROOT_DIR%web"
set "HOST=127.0.0.1"
set "PORT=3010"

echo Starting frontend on http://%HOST%:%PORT%

if not exist "%WEB_DIR%\package.json" (
  echo Cannot find web package.json at "%WEB_DIR%".
  exit /b 1
)

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
  echo Frontend already appears to be running.
  echo URL: http://%HOST%:%PORT%
  exit /b 0
)

if not exist "%WEB_DIR%\node_modules" (
  echo Installing web dependencies...
  pushd "%WEB_DIR%" || exit /b 1
  call npm install || exit /b 1
  popd
)

echo URL: http://%HOST%:%PORT%
echo Close this window to stop the frontend server.
echo.

pushd "%WEB_DIR%" || exit /b 1
call npm run dev -- --hostname %HOST% --port %PORT%
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

endlocal
