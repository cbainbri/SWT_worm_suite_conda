@echo off
cd /d "%~dp0"

echo Checking for updates to tracking, food_analysis, opto_analysis ...
echo.

git submodule update --remote
if errorlevel 1 (
    echo.
    echo Update failed -- check your internet connection and try again.
    pause
    exit /b 1
)

git diff --quiet HEAD
if errorlevel 1 (
    git add tracking food_analysis opto_analysis
    git commit -m "update submodules to latest"
    echo.
    echo Done -- submodules updated and committed.
) else (
    echo Already up to date.
)

pause
