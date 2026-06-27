#!/usr/bin/env python3
"""
SWT Worm Suite (conda) — Start
Finds micromamba/mamba/conda, checks the environment exists, launches the suite.
    python start.py        (Windows)
    python3 start.py       (Mac/Linux)
Or double-click launch.bat / launch.sh
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
ENV_NAME  = "worm_suite"


def find_conda_tool() -> tuple[Path, str] | tuple[None, None]:
    """
    Find the best available conda-compatible tool.
    Returns (path, tool_name) or (None, None).
    Priority: micromamba > mamba > conda
    """
    system = platform.system()
    home   = Path.home()

    # Check PATH first
    which = "where" if system == "Windows" else "which"
    for tool in ("micromamba", "mamba", "conda"):
        try:
            r = subprocess.run([which, tool], capture_output=True, text=True)
            if r.returncode == 0:
                p = Path(r.stdout.strip().splitlines()[0])
                if p.exists():
                    return p, tool
        except FileNotFoundError:
            pass

    # Common install locations
    if system == "Windows":
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        candidates = [
            (local / "micromamba" / "micromamba.exe",        "micromamba"),
            (home  / "micromamba" / "micromamba.exe",         "micromamba"),
            (home  / "mambaforge" / "Scripts" / "mamba.exe",  "mamba"),
            (home  / "miniforge3" / "Scripts" / "mamba.exe",  "mamba"),
            (home  / "miniconda3" / "Scripts" / "conda.exe",  "conda"),
            (home  / "anaconda3"  / "Scripts" / "conda.exe",  "conda"),
            (home  / "Miniconda3" / "Scripts" / "conda.exe",  "conda"),
            (home  / "Anaconda3"  / "Scripts" / "conda.exe",  "conda"),
        ]
    elif system == "Darwin":
        candidates = [
            (home / ".local" / "bin" / "micromamba",      "micromamba"),
            (home / "micromamba" / "bin" / "micromamba",  "micromamba"),
            (home / "mambaforge" / "bin" / "mamba",       "mamba"),
            (home / "miniforge3" / "bin" / "mamba",       "mamba"),
            (Path("/opt/homebrew/bin/mamba"),              "mamba"),
            (Path("/usr/local/bin/mamba"),                 "mamba"),
            (home / "miniconda3" / "bin" / "conda",       "conda"),
            (home / "anaconda3"  / "bin" / "conda",       "conda"),
            (home / "miniforge3" / "bin" / "conda",       "conda"),
            (Path("/opt/anaconda3/bin/conda"),             "conda"),
        ]
    else:  # Linux
        candidates = [
            (home / ".local" / "bin" / "micromamba",      "micromamba"),
            (home / "micromamba" / "bin" / "micromamba",  "micromamba"),
            (home / "mambaforge" / "bin" / "mamba",       "mamba"),
            (home / "miniforge3" / "bin" / "mamba",       "mamba"),
            (Path("/usr/bin/mamba"),                       "mamba"),
            (home / "miniconda3" / "bin" / "conda",       "conda"),
            (home / "anaconda3"  / "bin" / "conda",       "conda"),
            (home / "miniforge3" / "bin" / "conda",       "conda"),
            (Path("/usr/bin/conda"),                       "conda"),
        ]

    for path, tool in candidates:
        if path.exists():
            return path, tool

    return None, None


def env_exists(tool_path: Path) -> bool:
    r = subprocess.run([str(tool_path), "env", "list"], capture_output=True, text=True)
    return ENV_NAME in r.stdout


def main():
    tool_path, tool_name = find_conda_tool()

    if not tool_path:
        print("No conda tool found (micromamba, mamba, or conda).")
        print("Run setup first:  python setup.py")
        sys.exit(1)

    if not env_exists(tool_path):
        print(f"Environment '{ENV_NAME}' not found.")
        print("Run setup first:  python setup.py")
        sys.exit(1)

    print(f"Launching SWT Worm Suite via {tool_name} (environment: {ENV_NAME}) ...")
    subprocess.run(
        [str(tool_path), "run", "-n", ENV_NAME,
         "python", str(SUITE_DIR / "launcher.py")],
        cwd=str(SUITE_DIR)
    )


if __name__ == "__main__":
    main()
