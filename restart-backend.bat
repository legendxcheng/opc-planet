@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "WEB_DIR=%ROOT_DIR%web"
set "HOST=127.0.0.1"
set "PORT=3010"

echo Restarting backend server on http://%HOST%:%PORT%

if not exist "%WEB_DIR%\package.json" (
  echo Cannot find web package.json at "%WEB_DIR%".
  exit /b 1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo Stopping process %%P on port %PORT%...
  taskkill /PID %%P /F >nul 2>nul
)

if not exist "%WEB_DIR%\node_modules" (
  echo Installing web dependencies...
  pushd "%WEB_DIR%" || exit /b 1
  call npm install || exit /b 1
  popd
)

echo URL: http://%HOST%:%PORT%
echo Close this window to stop the backend server.
echo.

pushd "%WEB_DIR%" || exit /b 1
call npm run dev -- --hostname %HOST% --port %PORT%
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

endlocal
