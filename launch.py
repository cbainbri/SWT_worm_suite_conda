#!/usr/bin/env python3
"""
SWT Worm Suite — Mac/Linux launcher
Usage:  python3 launch.py   or   ./launch.py
"""
import subprocess
import sys
from pathlib import Path

sys.exit(subprocess.run([sys.executable, Path(__file__).parent / "start.py"]).returncode)
