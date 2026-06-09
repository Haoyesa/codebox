@echo off
setlocal enableextensions enabledelayedexpansion
cd /d "%~dp0"

if not exist ".env" (
  if exist ".env.template" copy ".env.template" ".env" >nul
  echo [WARN] .env missing. Template copied. Fill credentials and run again.
  exit /b 1
)

set "APP_ID="
set "APP_SECRET="
set "USER_TOKEN="

for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
  set "KEY=%%~A"
  set "VAL=%%~B"
  if /I "!KEY!"=="FEISHU_APP_ID" set "APP_ID=!VAL!"
  if /I "!KEY!"=="FEISHU_APP_SECRET" set "APP_SECRET=!VAL!"
  if /I "!KEY!"=="FEISHU_USER_ACCESS_TOKEN" set "USER_TOKEN=!VAL!"
)

if defined USER_TOKEN (
  if /I not "!USER_TOKEN!"=="your_user_access_token_here" (
    if not "!USER_TOKEN!"=="" goto ok
  )
)

if defined APP_ID if defined APP_SECRET (
  if /I not "!APP_ID!"=="your_app_id_here" (
    if /I not "!APP_SECRET!"=="your_app_secret_here" goto ok
  )
)

echo [ERROR] Credentials are not configured.
echo [HINT] Use either:
echo [HINT] 1) FEISHU_APP_ID + FEISHU_APP_SECRET
 echo [HINT] 2) FEISHU_USER_ACCESS_TOKEN
exit /b 1

:ok
echo [OK] Credentials look configured.
exit /b 0
