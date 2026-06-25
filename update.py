#!/usr/bin/env python3
"""
SWT Worm Suite — Update
Pulls the latest scripts from all three source repos (tracking, food_analysis, opto_analysis).
    python update.py
"""
import subprocess
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent


def run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=str(SUITE_DIR), **kwargs)


def main():
    print("Checking for updates to tracking, food_analysis, opto_analysis ...")

    result = run(["git", "submodule", "update", "--remote"])
    if result.returncode != 0:
        print("\nUpdate failed — make sure you have internet access and the source repos are reachable.")
        sys.exit(1)

    # Check if anything actually changed
    status = run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("\nAlready up to date.")
        return

    print("\nChanges pulled:")
    for line in status.stdout.strip().splitlines():
        print(f"  {line}")

    run(["git", "add", "tracking", "food_analysis", "opto_analysis"])
    run(["git", "commit", "-m", "update submodules to latest"])
    print("\nDone — submodules updated and committed.")


if __name__ == "__main__":
    main()
