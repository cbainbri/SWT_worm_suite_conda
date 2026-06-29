#!/usr/bin/env python3
"""
SWT Worm Suite — Unified Launcher
Run: python launcher.py
"""
import os
import sys
import subprocess
from pathlib import Path

# Self-re-exec into the worm_suite conda environment if not already there.
# os.execvp replaces this process in-place — no double window.
if os.environ.get("CONDA_DEFAULT_ENV") != "worm_suite":
    import shutil
    _tool = shutil.which("micromamba") or shutil.which("conda") or shutil.which("mamba")
    if _tool:
        os.execvp(_tool, [_tool, "run", "-n", "worm_suite", "python"] + sys.argv)
    else:
        import tkinter as tk
        from tkinter import messagebox
        _r = tk.Tk(); _r.withdraw()
        messagebox.showerror(
            "Environment Not Found",
            "Could not find micromamba or conda.\n\nHave you run setup.py yet?"
        )
        _r.destroy()
        sys.exit(1)

_GPU_CACHE = Path(__file__).resolve().parent / '.gpu_config'
# GFX versions compiled into PyTorch ROCm wheels, newest first
_GFX_CANDIDATES = ['11.0.0', '10.3.0', '9.4.0', '9.0.10', '9.0.6']
_GPU_PROBE = (
    'import torch; t=torch.zeros(1,device="cuda"); '
    'assert (t+1).item()==1.0'
)

def _probe_gfx(ver: str | None) -> bool:
    """Run _GPU_PROBE in a subprocess with HSA_OVERRIDE_GFX_VERSION=ver."""
    env = os.environ.copy()
    if ver:
        env['HSA_OVERRIDE_GFX_VERSION'] = ver
    else:
        env.pop('HSA_OVERRIDE_GFX_VERSION', None)
    r = subprocess.run([sys.executable, '-c', _GPU_PROBE],
                       env=env, capture_output=True, timeout=20)
    return r.returncode == 0

def _set_hsa_override():
    """Detect the HSA_OVERRIDE_GFX_VERSION needed for this GPU and set it in
    os.environ so every child process inherits it with a fresh HSA context.
    Result is cached in .gpu_config; probe only runs when cache is missing."""
    if 'HSA_OVERRIDE_GFX_VERSION' in os.environ:
        return

    # Read cache
    cached = None
    if _GPU_CACHE.exists():
        cached = _GPU_CACHE.read_text().strip()
        if cached == 'none':
            return  # previously confirmed: no override needed
        os.environ['HSA_OVERRIDE_GFX_VERSION'] = cached
        return

    # No cache — probe (runs once, takes a few seconds)
    try:
        import torch
        if not torch.cuda.is_available():
            return
        if 'nvidia' in torch.cuda.get_device_name(0).lower():
            return
    except Exception:
        return

    # Try without override first
    if _probe_gfx(None):
        _GPU_CACHE.write_text('none')
        return

    # Try each GFX version until one works
    for ver in _GFX_CANDIDATES:
        if _probe_gfx(ver):
            os.environ['HSA_OVERRIDE_GFX_VERSION'] = ver
            _GPU_CACHE.write_text(ver)
            return

_set_hsa_override()

import tkinter as tk
from tkinter import ttk, messagebox

SUITE_DIR = Path(__file__).resolve().parent

CATEGORIES = [
    ("Tracking Pipeline", [
        ("Track Preview  (tune params on single directory)", SUITE_DIR / "tracking" / "track_preview.py"),
        ("Batch Tracking — Food",                            SUITE_DIR / "tracking" / "batch_tracking_food.py"),
        ("Batch Tracking — Food (GPU)",                     SUITE_DIR / "tracking" / "batch_tracking_gpu_accel_food.py"),
        ("Batch Tracking — Opto",                           SUITE_DIR / "tracking" / "batch_tracking_opto.py"),
        ("Track Editor — Food",                             SUITE_DIR / "tracking" / "track_editor_food.py"),
        ("Track Editor — Opto",                             SUITE_DIR / "tracking" / "track_editor_opto.py"),
    ]),
    ("Food Encounter Analysis", [
        ("Mask Borders",                SUITE_DIR / "food_analysis" / "automatic_mask_borders.py"),
        ("Merge Files",                 SUITE_DIR / "food_analysis" / "merge_files.py"),
        ("Bootstrap",                   SUITE_DIR / "food_analysis" / "bootstrap_food.py"),
        ("Bootstrap (Vectorized)",      SUITE_DIR / "food_analysis" / "bootstrap_food_vectorized.py"),
        ("Permutation Testing",         SUITE_DIR / "food_analysis" / "permutation_food.py"),
        ("Graph Viewer",                SUITE_DIR / "food_analysis" / "graph_viewer_food.py"),
    ]),
    ("Opto Analysis", [
        ("Merge Files",     SUITE_DIR / "opto_analysis" / "merge_files.py"),
        ("Bootstrap",       SUITE_DIR / "opto_analysis" / "bootstrap_opto.py"),
        ("Graph Viewer",    SUITE_DIR / "opto_analysis" / "graph_viewer_opto.py"),
    ]),
]

def launch(script: Path):
    if not script.exists():
        messagebox.showerror("Not found", f"Script not found:\n{script}")
        return
    subprocess.Popen([sys.executable, str(script)], cwd=str(script.parent))


class AccordionSection(ttk.Frame):
    def __init__(self, parent, title: str, tools: list, **kwargs):
        super().__init__(parent, **kwargs)
        self.expanded = tk.BooleanVar(value=True)

        # Header button
        self.header = tk.Button(
            self,
            text=f"  ▼  {title}",
            anchor="w",
            font=("TkDefaultFont", 10, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
            activebackground="#3c3c3c",
            activeforeground="#ffffff",
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.toggle,
        )
        self.header.pack(fill="x")

        # Script buttons container
        self.body = ttk.Frame(self)
        self.body.pack(fill="x")

        for label, script in tools:
            btn = tk.Button(
                self.body,
                text=f"      {label}",
                anchor="w",
                font=("TkDefaultFont", 9),
                bg="#f5f5f5",
                fg="#222222",
                activebackground="#ddeeff",
                activeforeground="#000000",
                bd=0,
                padx=8,
                pady=5,
                cursor="hand2",
                command=lambda s=script: launch(s),
            )
            btn.pack(fill="x", pady=1)

    def toggle(self):
        if self.expanded.get():
            self.body.pack_forget()
            self.header.config(text=self.header.cget("text").replace("▼", "▶"))
            self.expanded.set(False)
        else:
            self.body.pack(fill="x")
            self.header.config(text=self.header.cget("text").replace("▶", "▼"))
            self.expanded.set(True)


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SWT Worm Suite")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        ttk.Style(self).theme_use("clam")

        # Title bar
        title_frm = tk.Frame(self, bg="#1e1e1e")
        title_frm.pack(fill="x", padx=16, pady=(16, 10))
        tk.Label(
            title_frm,
            text="SWT Worm Suite",
            font=("TkDefaultFont", 15, "bold"),
            bg="#1e1e1e",
            fg="#ffffff",
        ).pack(anchor="w")
        tk.Label(
            title_frm,
            text="Select a tool to launch",
            font=("TkDefaultFont", 9),
            bg="#1e1e1e",
            fg="#888888",
        ).pack(anchor="w")

        # Accordion sections
        for title, tools in CATEGORIES:
            section = AccordionSection(self, title, tools, style="TFrame")
            section.pack(fill="x", padx=12, pady=4)

        # Footer
        tk.Label(
            self,
            text="Each tool opens in its own window",
            font=("TkDefaultFont", 8),
            bg="#1e1e1e",
            fg="#555555",
        ).pack(pady=(8, 12))


def main():
    app = Launcher()
    app.mainloop()


if __name__ == "__main__":
    main()
