@echo off
setlocal EnableExtensions
title Horizon Go-Kart - Instalare automata Windows

set "MOD_DIR=%~dp0mixins\gokart_native"
if not exist "%MOD_DIR%\horizon-mixin.toml" (
    echo [EROARE] Nu am gasit "%MOD_DIR%\horizon-mixin.toml".
    echo Asigura-te ca ai dezarhivat intregul folder HorizonMods inainte sa rulezi acest fisier!
    pause
    exit /b 1
)

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
    echo [EROARE] Nu am gasit horizon-launcher.exe in locatia implicita:
    echo   %LOCALAPPDATA%\Programs\Horizon Launcher\horizon-launcher.exe
    echo Porneste Horizon Launcher si incearca din nou, sau instaleaza modul direct din tab-ul Mods -^> Add from GitHub!
    pause
    exit /b 1
)

echo ==============================================================
echo   Horizon Go-Kart (gokart_native) - Compilare in Horizon
echo ==============================================================
echo Launcher gasit: "%LAUNCHER%"
echo Folder mod:     "%MOD_DIR%"
echo.
echo NOTA: Prima compilare descarca automat Rust in Horizon Launcher
echo si poate dura 15-25 minute. Urmatoarele dureaza 1-2 minute.
echo.

"%LAUNCHER%" native-build "%MOD_DIR%" --trust-native-code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [EROARE] Compilarea a returnat codul %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================
echo   GATA! Modul Go-Kart a fost compilat in instanta ta Horizon!
echo   Acum mergi in Horizon Launcher si apasa butonul PLAY!
echo   In joc poti scrie /gokart kit sau fabrica piesele la masa.
echo ==============================================================
pause
