#!/bin/bash
# Double-click this file in Finder to launch the SWT Worm Suite.
cd "$(dirname "$0")" || exit 1
python3 launcher.py
status=$?
if [ $status -ne 0 ]; then
    echo
    echo "Something went wrong. Make sure you ran setup.py first."
    read -n 1 -s -r -p "Press any key to close..."
fi
# Close the Terminal window this script opened
osascript -e 'tell application "Terminal" to close (every window whose name contains "mac_launch.command")' >/dev/null 2>&1 &
exit $status
