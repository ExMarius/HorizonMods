@echo off
setlocal EnableExtensions
title Horizon Vehicles - Update Automat cu 1 Click

echo ==============================================================
echo   Horizon Vehicles - Descarcare + Update Automat (1 Click)
echo ==============================================================

set "LAUNCHER=%LOCALAPPDATA%\Programs\Horizon Launcher\horizon-launcher.exe"
if not exist "%LAUNCHER%" (
    for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$p = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'horizon-launcher' } | Select-Object -First 1).Path; if ($p) { Write-Output $p }"`) do (
        set "LAUNCHER=%%P"
    )
)
if not exist "%LAUNCHER%" (
    where horizon-launcher.exe >nul 2>nul
    if %ERRORLEVEL% EQU 0 set "LAUNCHER=horizon-launcher.exe"
)
if not exist "%LAUNCHER%" if not "%LAUNCHER%"=="horizon-launcher.exe" (
    echo [EROARE] Nu am gasit horizon-launcher.exe! Porneste Horizon Launcher si incearca din nou.
    pause
    exit /b 1
)

set "TMP_HNMOD=%TEMP%\gokart_native_latest.hnmod"
set "URL=https://github.com/ExMarius/HorizonMods/raw/arena/fb5f91ff-horizonmods/dist/gokart_native.hnmod"

echo [1/2] Descarc ultima versiune gokart_native.hnmod direct de pe GitHub...
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL%' -OutFile '%TMP_HNMOD%' -UseBasicParsing"
if %ERRORLEVEL% NEQ 0 (
    echo [EROARE] Nu am putut descarca %URL%
    pause
    exit /b 1
)

echo [2/2] Actualizez instanta Horizon (recompilare incrementala ~1-2 min)...
"%LAUNCHER%" native-build "%TMP_HNMOD%" --trust-native-code
if %ERRORLEVEL% NEQ 0 (
    echo [EROARE] Compilarea a returnat codul %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================
echo   GATA! Ultima versiune Horizon Vehicles este instalata!
echo   Intra in Horizon Launcher si apasa PLAY!
echo ==============================================================
pause
