@echo off
:: SWT Worm Suite -- Windows setup. Double-click to install.
:: The real setup lives in setup\ -- this file just calls it.
:: Options pass through, e.g.:  Setup.bat --launcher-only
call "%~dp0setup\windows_setup.bat" %*
