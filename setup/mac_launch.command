#!/bin/bash
# Real Mac launcher. Setup puts Mac_launcher.command in the suite folder,
# which calls this; double-clicking this file directly also works.
cd "$(dirname "$0")" || exit 1
python3 launcher.py
status=$?
if [ $status -ne 0 ]; then
    echo
    echo "Something went wrong. Make sure you ran Setup.command first."
    read -n 1 -s -r -p "Press any key to close..."
fi
# Close the Terminal window this script opened
osascript -e 'tell application "Terminal" to close (every window whose name contains "Mac_launcher.command" or name contains "mac_launch.command")' >/dev/null 2>&1 &
exit $status
