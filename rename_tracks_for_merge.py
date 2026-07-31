#!/usr/bin/env python3
"""
Prep Track Data (standalone): scan an experiment root directory (e.g. F:\\nsm_chrimson)
for tracks*.csv files in each experiment subfolder, and copy the highest-numbered one
into an output directory as <experiment folder name>.csv, ready to hand to merge_files.py.
A second copy is always left alongside the original tracksN.csv in its source folder
as a backup. The same "Prep Track Data" workflow is also built into merge_files.py
directly (opto_analysis/ and food_analysis/), so this script is only needed if you'd
rather prep files without opening merge_files.py.

Numbering convention: tracks.csv (implicit #1) < tracks2.csv < tracks3.csv ...
Higher number = more recently edited/corrected. tracks_long.csv is ignored.

Run: python rename_tracks_for_merge.py
"""

import re
import shutil
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Prep Track Data"

TRACKS_PATTERN = re.compile(r'^tracks(\d*)\.csv$', re.IGNORECASE)


def find_best_tracks_file(exp_dir: Path):
    """Return (path, flag_or_None) for the highest-numbered tracksN.csv in exp_dir,
    or (None, reason) if no tracks*.csv file is present."""
    candidates = []
    for p in exp_dir.iterdir():
        if not p.is_file():
            continue
        m = TRACKS_PATTERN.match(p.name)
        if m:
            num = int(m.group(1)) if m.group(1) else 1
            candidates.append((num, p))

    if not candidates:
        return None, "No tracks*.csv file found"

    candidates.sort(key=lambda t: t[0])
    best_num, best_path = candidates[-1]

    flag = None
    if best_num == 1:
        flag = "Using tracks.csv - no edited tracksN version found"
    elif best_num > 2:
        flag = f"Using {best_path.name} - highest found is #{best_num}, verify this is really the latest edit"

    return best_path, flag


class DupDialog(tk.Toplevel):
    """Ask what to do when the destination filename already exists."""
    def __init__(self, master, filename: str):
        super().__init__(master)
        self.title("File already exists")
        self.resizable(False, False)
        self.result = None  # 'skip' | 'overwrite' | 'skip_all' | 'overwrite_all'

        frm = ttk.Frame(self, padding=15)
        frm.grid(row=0, column=0)

        ttk.Label(
            frm,
            text=f'"{filename}" already exists in the output directory.',
            wraplength=380,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        btns = ttk.Frame(frm)
        btns.grid(row=1, column=0, columnspan=2)

        ttk.Button(btns, text="Skip", width=14,
                   command=lambda: self._choose('skip')).grid(row=0, column=0, padx=4, pady=3)
        ttk.Button(btns, text="Overwrite", width=14,
                   command=lambda: self._choose('overwrite')).grid(row=0, column=1, padx=4, pady=3)
        ttk.Button(btns, text="Skip All", width=14,
                   command=lambda: self._choose('skip_all')).grid(row=1, column=0, padx=4, pady=3)
        ttk.Button(btns, text="Overwrite All", width=14,
                   command=lambda: self._choose('overwrite_all')).grid(row=1, column=1, padx=4, pady=3)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self._choose('skip'))
        self.wait_visibility()
        self.focus_set()

    def _choose(self, choice):
        self.result = choice
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.minsize(800, 500)

        self.root_var = tk.StringVar()
        self.out_var = tk.StringVar()

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        desc = ttk.Label(frm, text=(
            "Pick a root directory containing experiment subfolders.\n"
            "For each subfolder, the highest-numbered tracks*.csv (tracks.csv, tracks2.csv, tracks3.csv, ...) is\n"
            "copied into the output directory as <experiment folder name>.csv, ready for merge_files.py."
        ), justify="left")
        desc.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Label(frm, text="Root directory:").grid(row=1, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.root_var, width=70).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(frm, text="Browse...", command=self._browse_root).grid(row=1, column=2, sticky="w")

        ttk.Label(frm, text="Output directory:").grid(row=2, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.out_var, width=70).grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Button(frm, text="Browse...", command=self._browse_out).grid(row=2, column=2, sticky="w")

        ttk.Button(frm, text="Prep Track Data", command=self._run).grid(row=3, column=1, pady=(10, 0))

        self.log = tk.Text(frm, height=28, wrap="word")
        self.log.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        frm.rowconfigure(4, weight=1)
        frm.columnconfigure(1, weight=1)

        self.log.tag_config("warn", foreground="#b8860b")
        self.log.tag_config("err", foreground="#c0392b")
        self.log.tag_config("ok", foreground="#2e7d32")

    def _browse_root(self):
        d = filedialog.askdirectory(title="Choose experiment root directory")
        if d:
            self.root_var.set(d)

    def _browse_out(self):
        d = filedialog.askdirectory(title="Choose output directory")
        if d:
            self.out_var.set(d)

    def _log(self, msg, tag=None):
        self.log.insert("end", msg + "\n", (tag,) if tag else ())
        self.log.see("end")
        self.log.update_idletasks()

    def _run(self):
        root_dir = Path(self.root_var.get().strip())
        out_dir_str = self.out_var.get().strip()

        if not root_dir.exists() or not root_dir.is_dir():
            messagebox.showerror("Error", f"Root directory does not exist:\n{root_dir}")
            return
        if not out_dir_str:
            messagebox.showerror("Error", "Please choose an output directory.")
            return

        out_dir = Path(out_dir_str)
        out_dir.mkdir(parents=True, exist_ok=True)

        exp_dirs = sorted(p for p in root_dir.iterdir() if p.is_dir())
        if not exp_dirs:
            messagebox.showwarning("No experiments", f"No subdirectories found in:\n{root_dir}")
            return

        self.log.delete("1.0", "end")
        self._log(f"Scanning {len(exp_dirs)} experiment folder(s) in:\n{root_dir}\n")

        global_choice = None  # 'skip_all' | 'overwrite_all' once the user picks one
        copied = skipped_dup = skipped_missing = 0

        for exp_dir in exp_dirs:
            best_path, flag = find_best_tracks_file(exp_dir)

            if best_path is None:
                self._log(f"[MISSING] {exp_dir.name}: {flag} (folder: {exp_dir})", "err")
                skipped_missing += 1
                continue

            if flag:
                self._log(f"[FLAG] {exp_dir.name}: {flag}", "warn")

            dest = out_dir / f"{exp_dir.name}.csv"

            if dest.exists():
                if global_choice == 'skip_all':
                    self._log(f"[SKIP] {exp_dir.name}: {dest.name} already exists (skip all)", "warn")
                    skipped_dup += 1
                    continue
                elif global_choice != 'overwrite_all':
                    dlg = DupDialog(self, dest.name)
                    self.wait_window(dlg)
                    choice = dlg.result or 'skip'
                    if choice in ('skip_all', 'overwrite_all'):
                        global_choice = choice
                    if choice in ('skip', 'skip_all'):
                        self._log(f"[SKIP] {exp_dir.name}: {dest.name} already exists", "warn")
                        skipped_dup += 1
                        continue

            try:
                shutil.copy2(best_path, dest)
                self._log(f"[OK] {exp_dir.name}: copied {best_path.name} -> {dest.name}", "ok")
                copied += 1
            except Exception as e:
                self._log(f"[ERROR] {exp_dir.name}: failed to copy {best_path.name}: {e}", "err")
                continue

            # Backup copy stays next to the original tracksN.csv regardless of
            # what happens to the collected copy in out_dir.
            backup_dest = exp_dir / dest.name
            try:
                if backup_dest.resolve() != best_path.resolve():
                    shutil.copy2(best_path, backup_dest)
                    self._log(f"[BACKUP] {exp_dir.name}: also saved as {backup_dest.name} in source folder", "ok")
            except Exception as e:
                self._log(f"[ERROR] {exp_dir.name}: failed to save backup copy: {e}", "err")

        self._log(
            f"\nDone. Copied: {copied}, Skipped (duplicate): {skipped_dup}, "
            f"Missing tracks file: {skipped_missing}"
        )
        messagebox.showinfo(
            "Done",
            f"Copied: {copied}\nSkipped (duplicate): {skipped_dup}\nMissing tracks file: {skipped_missing}",
        )


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
