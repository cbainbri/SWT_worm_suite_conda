@echo off
cd /d "%~dp0"
setlocal

echo.
echo  SWT Worm Suite -- Windows Setup
echo  ==================================
echo.

:: ── 1. Find an existing conda/micromamba tool ─────────────────────────────────
set CONDA_EXE=

for /f "delims=" %%i in ('where micromamba 2^>nul') do (
    if not defined CONDA_EXE set CONDA_EXE=%%i
)
for /f "delims=" %%i in ('where mamba 2^>nul') do (
    if not defined CONDA_EXE set CONDA_EXE=%%i
)
for /f "delims=" %%i in ('where conda 2^>nul') do (
    if not defined CONDA_EXE set CONDA_EXE=%%i
)

if not defined CONDA_EXE (
    for %%p in (
        "%LOCALAPPDATA%\micromamba\micromamba.exe"
        "%USERPROFILE%\micromamba\micromamba.exe"
        "%USERPROFILE%\mambaforge\Scripts\mamba.exe"
        "%USERPROFILE%\miniforge3\Scripts\mamba.exe"
        "%USERPROFILE%\miniconda3\Scripts\conda.exe"
        "%USERPROFILE%\Miniconda3\Scripts\conda.exe"
        "%USERPROFILE%\anaconda3\Scripts\conda.exe"
        "%USERPROFILE%\Anaconda3\Scripts\conda.exe"
    ) do (
        if not defined CONDA_EXE if exist %%p set CONDA_EXE=%%~p
    )
)

:: ── 2. If nothing found, download and silently install Miniconda3 ─────────────
if not defined CONDA_EXE (
    echo No conda installation found. Downloading Miniconda3...
    echo This is a one-time download (approx. 100 MB^).
    echo.

    :: Detect architecture
    set MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
    if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
        set MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-arm64.exe
    )

    set INSTALLER=%TEMP%\Miniconda3_installer.exe
    powershell -NoProfile -Command "Invoke-WebRequest -Uri '%MINICONDA_URL%' -OutFile '%INSTALLER%'"

    if not exist "%INSTALLER%" (
        echo.
        echo ERROR: Download failed. Check your internet connection, then try again.
        echo Or install Miniconda manually from:
        echo   https://docs.conda.io/en/latest/miniconda.html
        pause
        exit /b 1
    )

    echo Installing Miniconda3 (silent, no admin rights required^)...
    "%INSTALLER%" /S /D=%USERPROFILE%\Miniconda3
    del "%INSTALLER%"

    set CONDA_EXE=%USERPROFILE%\Miniconda3\Scripts\conda.exe
    if not exist "%CONDA_EXE%" (
        echo.
        echo ERROR: Miniconda install did not complete as expected.
        echo Please install manually from:
        echo   https://docs.conda.io/en/latest/miniconda.html
        pause
        exit /b 1
    )

    echo Miniconda3 installed.
    echo.
) else (
    echo Found conda tool: %CONDA_EXE%
    echo.
)

:: ── 3. Find a Python to run setup.py ─────────────────────────────────────────
::
:: Priority:
::   a) worm_suite env already exists (re-run / partial install) -- use it
::   b) base env has Python (Miniconda/Anaconda) -- use it
::   c) neither (micromamba fresh install, no Python yet) -- create worm_suite
::      from environment.yml first, then use it

set RUN_ENV=

:: (a) worm_suite already exists?
"%CONDA_EXE%" env list 2>nul | findstr /C:"worm_suite" >nul
if not errorlevel 1 (
    set RUN_ENV=worm_suite
    goto run_setup
)

:: (b) base env has Python?
"%CONDA_EXE%" run -n base python --version >nul 2>&1
if not errorlevel 1 (
    set RUN_ENV=base
    goto run_setup
)

:: (c) No Python anywhere -- create worm_suite first
echo No Python found in base environment (micromamba install detected^).
echo Creating worm_suite environment first -- this takes 5-15 minutes...
echo.
"%CONDA_EXE%" env create -f "%~dp0environment.yml" -y
if errorlevel 1 (
    echo.
    echo Environment creation failed -- check the output above.
    pause
    exit /b 1
)
set RUN_ENV=worm_suite

:run_setup
echo.
echo Starting setup wizard (using %RUN_ENV% environment^)...
echo (A window will appear -- keep this terminal open until setup completes^)
echo.
"%CONDA_EXE%" run -n %RUN_ENV% python "%~dp0setup.py"

if errorlevel 1 (
    echo.
    echo Setup did not complete successfully -- check the output above.
) else (
    echo.
    echo Setup finished.
)

echo.
pause
endlocal
