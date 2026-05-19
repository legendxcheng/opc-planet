@echo off
setlocal

cd /d "%~dp0"

set "KNOWLEDGE_ARCHIVE=E:\tmp\opc-website-knowledge.tar.gz"
set "WEB_REPO=git@git.weixin.qq.com:legendxcheng/opc-website.git"

if not exist "E:\tmp" mkdir "E:\tmp"

echo [1/2] Packaging knowledge directories...
tar -czf "%KNOWLEDGE_ARCHIVE%" knowledge sources outputs agent
if errorlevel 1 (
  echo Failed to package knowledge directories.
  exit /b 1
)

echo [2/2] Deploying website...
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\deploy-web.ps1" -RepoUrl "%WEB_REPO%" -KnowledgeArchivePath "%KNOWLEDGE_ARCHIVE%"
if errorlevel 1 (
  echo Website deployment failed.
  exit /b 1
)

echo Website deployment completed.
endlocal
