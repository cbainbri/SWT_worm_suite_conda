#!/bin/bash
# SWT Worm Suite -- Mac setup. Double-click in Finder to install.
# The real setup lives in setup/ -- this file just calls it.
# Options pass through, e.g.:  ./Setup.command --launcher-only
cd "$(dirname "$0")" || exit 1
python3 setup/setup.py "$@"
status=$?
echo
if [ $status -eq 0 ]; then
    echo "Setup finished. You can close this window."
else
    echo "Setup did not complete -- check the output above."
fi
exit $status
