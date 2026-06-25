@echo off
cd /d "%~dp0"
python start.py
if errorlevel 1 (
    echo.
    echo Something went wrong. Run setup.py first if you haven't already:
    echo   python setup.py
    pause
)
