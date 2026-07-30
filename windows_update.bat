@echo off
cd /d "%~dp0"
setlocal

:: ── Locate a conda/micromamba executable ─────────────────────────────────────
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

if not defined CONDA_EXE (
    echo ERROR: conda / mamba / micromamba not found.
    echo Please install Miniconda from https://docs.conda.io/en/latest/miniconda.html
    echo Then run update.py from the Miniconda Prompt.
    pause
    exit /b 1
)

:: ── Run the update inside the worm_suite environment ─────────────────────────
"%CONDA_EXE%" run -n worm_suite python "%~dp0update.py"
if errorlevel 1 (
    echo.
    echo Update did not complete successfully -- check the output above.
)

echo.
pause
endlocal
