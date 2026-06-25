#!/usr/bin/env python3
"""
SWT Worm Suite — Unified Launcher
Run: python launcher.py
"""
import subprocess
import sys
from pathlib import Path
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
