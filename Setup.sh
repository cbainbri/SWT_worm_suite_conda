#!/usr/bin/env bash
# SWT Worm Suite -- Linux setup. Run:  ./Setup.sh   (or: bash Setup.sh)
# The real setup lives in setup/ -- this file just calls it.
# Options pass through, e.g.:  ./Setup.sh --launcher-only
cd "$(dirname "$0")" || exit 1
python3 setup/setup.py "$@"
