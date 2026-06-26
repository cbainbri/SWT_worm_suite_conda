#!/usr/bin/env python3
"""
SWT Worm Suite (conda) — Setup
Finds or installs a conda tool (micromamba / mamba / conda), creates the
worm_suite environment, and downloads SAM weights.
Run once:
    python setup.py
"""
import io
import os
import platform
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

SUITE_DIR = Path(__file__).resolve().parent
ENV_NAME  = "worm_suite"

# ─── Conda tool detection ─────────────────────────────────────────────────────

def find_conda_tool() -> tuple[Path, str] | tuple[None, None]:
    """
    Find the best available conda-compatible tool.
    Returns (path, tool_name) or (None, None).
    Priority: micromamba > mamba > conda
    """
    system = platform.system()

    # 1. Check PATH first (covers activated base envs, Homebrew, etc.)
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

    # 2. Check common install locations
    home = Path.home()
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
            (Path("/opt/miniconda3/bin/conda"),            "conda"),
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


# ─── Micromamba fallback install ──────────────────────────────────────────────

MICROMAMBA_URLS = {
    ("Windows", "AMD64"):   "https://micro.mamba.pm/api/micromamba/win-64/latest",
    ("Windows", "x86_64"):  "https://micro.mamba.pm/api/micromamba/win-64/latest",
    ("Darwin",  "arm64"):   "https://micro.mamba.pm/api/micromamba/osx-arm64/latest",
    ("Darwin",  "x86_64"):  "https://micro.mamba.pm/api/micromamba/osx-64/latest",
    ("Linux",   "x86_64"):  "https://micro.mamba.pm/api/micromamba/linux-64/latest",
    ("Linux",   "aarch64"): "https://micro.mamba.pm/api/micromamba/linux-aarch64/latest",
}

def micromamba_install_path() -> Path:
    if platform.system() == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "micromamba" / "micromamba.exe"
    return Path.home() / ".local" / "bin" / "micromamba"

def install_micromamba() -> Path:
    key = (platform.system(), platform.machine())
    url = MICROMAMBA_URLS.get(key)
    if not url:
        raise RuntimeError(f"No micromamba binary available for {key}")
    print("Downloading micromamba...")
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    dest = micromamba_install_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
        member = tar.getmember(
            "Library/bin/micromamba.exe" if platform.system() == "Windows"
            else "bin/micromamba"
        )
        dest.write_bytes(tar.extractfile(member).read())
    if platform.system() != "Windows":
        os.chmod(dest, 0o755)
    print(f"micromamba installed at {dest}")
    return dest


def env_exists(tool_path: Path) -> bool:
    r = subprocess.run([str(tool_path), "env", "list"], capture_output=True, text=True)
    return ENV_NAME in r.stdout


# ─── GPU Detection ────────────────────────────────────────────────────────────

def detect_gpu() -> str:
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        return "mps"
    try:
        if subprocess.run(["nvidia-smi"], capture_output=True, timeout=5).returncode == 0:
            return "cuda"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        if subprocess.run(["rocm-smi"], capture_output=True, timeout=5).returncode == 0:
            return "rocm"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "cpu"

TORCH_URLS = {
    "cpu":  "https://download.pytorch.org/whl/cpu",
    "cuda": "https://download.pytorch.org/whl/cu121",
    "rocm": "https://download.pytorch.org/whl/rocm6.2",
    "mps":  None,
}

GPU_OPTIONS = [
    ("cpu",  "CPU only  (works on all machines)"),
    ("cuda", "NVIDIA GPU  (CUDA)"),
    ("rocm", "AMD GPU  (ROCm)"),
    ("mps",  "Apple Silicon  (MPS — M1/M2/M3)"),
]
GPU_LABELS = {k: v for k, v in GPU_OPTIONS}

# ─── UI ───────────────────────────────────────────────────────────────────────

class SetupApp(tk.Tk):
    def __init__(self, detected_gpu: str, found_tool: str | None, tool_path: Path | None):
        super().__init__()
        self.title("SWT Worm Suite — Local Setup")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")
        self.gpu_var = tk.StringVar(value=detected_gpu)

        pad = {"padx": 20, "pady": 6}

        tk.Label(self, text="SWT Worm Suite — Local Setup",
                 font=("TkDefaultFont", 14, "bold"),
                 bg="#1e1e1e", fg="#ffffff").pack(pady=(20, 4))

        if found_tool:
            subtitle = f"Using {found_tool} to create the isolated worm_suite environment."
        else:
            subtitle = "No conda tool found — will install micromamba automatically."
        tk.Label(self, text=subtitle,
                 font=("TkDefaultFont", 9), bg="#1e1e1e", fg="#888888").pack()

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=14)

        # Tool detection status
        tool_frame = tk.Frame(self, bg="#2b2b2b")
        tool_frame.pack(fill="x", padx=20, pady=(0, 6))
        if found_tool:
            tool_text = f"  {found_tool}  —  {tool_path}"
            tool_color = "#88cc88"
        else:
            tool_text = "  No conda tool found — micromamba will be installed"
            tool_color = "#ccaa44"
        tk.Label(tool_frame, text=tool_text,
                 font=("TkDefaultFont", 9, "italic"),
                 bg="#2b2b2b", fg=tool_color, anchor="w").pack(fill="x", padx=10, pady=8)

        # GPU detection status
        gpu_frame = tk.Frame(self, bg="#2b2b2b")
        gpu_frame.pack(fill="x", padx=20, pady=(0, 10))
        gpu_status = "Detected" if detected_gpu != "cpu" else "No GPU detected — defaulting to"
        tk.Label(gpu_frame,
                 text=f"  {gpu_status}: {GPU_LABELS.get(detected_gpu, detected_gpu)}",
                 font=("TkDefaultFont", 9, "italic"),
                 bg="#2b2b2b", fg="#aaaaaa", anchor="w").pack(fill="x", padx=10, pady=8)

        tk.Label(self, text="Select GPU type:",
                 font=("TkDefaultFont", 10, "bold"),
                 bg="#1e1e1e", fg="#cccccc", anchor="w").pack(fill="x", **pad)

        for value, label in GPU_OPTIONS:
            tk.Radiobutton(self, text=label, variable=self.gpu_var, value=value,
                           font=("TkDefaultFont", 9),
                           bg="#1e1e1e", fg="#dddddd", selectcolor="#333333",
                           activebackground="#1e1e1e", activeforeground="#ffffff",
                           anchor="w").pack(fill="x", padx=30, pady=2)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=14)

        tk.Label(self,
                 text="All scripts run inside the isolated worm_suite environment\n— never touches your system Python.",
                 font=("TkDefaultFont", 8), bg="#1e1e1e", fg="#555555",
                 justify="left", wraplength=360).pack(fill="x", padx=20, pady=(0, 10))

        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(fill="x", padx=20, pady=(4, 20))

        tk.Button(btn_frame, text="Cancel", width=12, command=self.destroy,
                  bg="#333333", fg="#cccccc", relief="flat",
                  cursor="hand2").pack(side="right", padx=(6, 0))

        tk.Button(btn_frame, text="Install", width=18, command=self.proceed,
                  bg="#0066cc", fg="#ffffff", activebackground="#0055aa",
                  relief="flat", cursor="hand2",
                  font=("TkDefaultFont", 9, "bold")).pack(side="right")

    def proceed(self):
        gpu = self.gpu_var.get()
        self.destroy()
        run_install(gpu)

# ─── Install ──────────────────────────────────────────────────────────────────

def run_install(gpu: str):
    print(f"\nGPU selected: {gpu}")
    print("=" * 50)

    tool_path, tool_name = find_conda_tool()

    if tool_path:
        print(f"Using {tool_name}: {tool_path}")
    else:
        print("No conda tool found — installing micromamba...")
        tool_path = install_micromamba()
        tool_name = "micromamba"

    if env_exists(tool_path):
        print(f"\nEnvironment '{ENV_NAME}' already exists — skipping create.")
    else:
        print(f"\nCreating environment '{ENV_NAME}' using {tool_name} ...")
        print("This takes 5–15 minutes on first run.\n")
        result = subprocess.run(
            [str(tool_path), "env", "create",
             "-f", str(SUITE_DIR / "environment.yml"), "-y"],
            cwd=str(SUITE_DIR)
        )
        if result.returncode != 0:
            print("\nEnvironment creation failed — check output above.")
            _root = tk.Tk(); _root.withdraw()
            messagebox.showerror("Setup Failed", "Environment creation failed.\nCheck the terminal for details.")
            _root.destroy()
            sys.exit(1)

    print(f"\nInstalling PyTorch ({gpu}) ...")
    torch_url = TORCH_URLS.get(gpu)
    if torch_url:
        cmd = [str(tool_path), "run", "-n", ENV_NAME,
               "pip", "install", "torch", "torchvision",
               "--index-url", torch_url]
    else:
        cmd = [str(tool_path), "run", "-n", ENV_NAME,
               "pip", "install", "torch", "torchvision"]
    subprocess.run(cmd, check=True)

    print("\nDownloading SAM model weights (~1.2 GB) ...")
    subprocess.run(
        [str(tool_path), "run", "-n", ENV_NAME,
         "python", str(SUITE_DIR / "download_models.py")],
        cwd=str(SUITE_DIR), check=True
    )

    print("\n" + "=" * 50)
    print(f"Setup complete! (used: {tool_name})")
    print("\nTo launch:")
    print("  Windows:    double-click windows_launch.bat")
    print("  Mac/Linux:  python3 launch.py")

    _root = tk.Tk()
    _root.withdraw()
    messagebox.showinfo(
        "Setup Complete — SWT Worm Suite",
        "Installation successful!\n\n"
        "To launch the suite:\n"
        "  Windows:    double-click  windows_launch.bat\n"
        "  Mac/Linux:  python3 launch.py"
    )
    _root.destroy()


def main():
    detected_gpu = detect_gpu()
    tool_path, tool_name = find_conda_tool()
    app = SetupApp(detected_gpu, tool_name, tool_path)
    app.mainloop()


if __name__ == "__main__":
    main()
