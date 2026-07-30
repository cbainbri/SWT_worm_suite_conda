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


def run(cmd, cwd=None, **kwargs):
    return subprocess.run(cmd, cwd=str(cwd or SUITE_DIR), **kwargs)


def get_submodule_paths():
    result = run(["git", "config", "--file", ".gitmodules", "--get-regexp", r"\.path$"],
                 capture_output=True, text=True)
    paths = []
    for line in result.stdout.strip().splitlines():
        _, _, path = line.partition(" ")
        path = path.strip()
        if path:
            paths.append(path)
    return paths


def stash_dirty_submodules(paths):
    """
    A submodule with uncommitted changes to tracked files makes `git submodule
    update` abort with a checkout error (even if those changes are identical to
    the incoming commit). Stash them out of the way first so the update can
    proceed; resolve_stashes() below decides afterward whether the stash is
    still needed.
    """
    stashed = {}
    for path in paths:
        sm_dir = SUITE_DIR / path
        if not sm_dir.exists():
            continue
        status = run(["git", "status", "--porcelain", "--untracked-files=no"],
                      cwd=sm_dir, capture_output=True, text=True)
        if not status.stdout.strip():
            continue
        msg = f"autoupdate.py: uncommitted changes before submodule update ({path})"
        result = run(["git", "stash", "push", "-m", msg], cwd=sm_dir,
                     capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  Note: '{path}' had uncommitted changes — stashed before updating.")
            stashed[path] = "stash@{0}"
        else:
            print(f"  Warning: could not stash changes in '{path}':\n{result.stderr.strip()}")
    return stashed


def resolve_stashes(stashed):
    """
    After the submodule checkout, check whether each stash is now redundant —
    i.e. the local edits it holds are identical to what's now checked out. If
    so, drop it. If the local edits genuinely differ, leave the stash in place
    and tell the user exactly how to inspect/reapply it.
    """
    for path, ref in stashed.items():
        sm_dir = SUITE_DIR / path
        diff = run(["git", "diff", "--quiet", ref, "HEAD"], cwd=sm_dir)
        if diff.returncode == 0:
            run(["git", "stash", "drop", ref], cwd=sm_dir, capture_output=True, text=True)
            print(f"  '{path}': stashed changes matched the update exactly — stash dropped, nothing lost.")
        else:
            print(f"  '{path}': stashed changes DIFFER from the update — left in stash ({ref}).")
            print(f"    Review with:  git -C {path} stash show -p {ref}")
            print(f"    Reapply with: git -C {path} stash pop {ref}")


def main():
    print("Pulling latest parent repo ...")
    result = run(["git", "pull"])
    if result.returncode != 0:
        print("\nFailed to pull parent repo — make sure you have internet access.")
        sys.exit(1)

    print("Checking for updates to tracking, food_analysis, opto_analysis ...")
    submodule_paths = get_submodule_paths()
    stashed = stash_dirty_submodules(submodule_paths)

    result = run(["git", "submodule", "update", "--remote", "--init"])
    if result.returncode != 0:
        print("\nUpdate failed — make sure you have internet access and the source repos are reachable.")
        if stashed:
            print("Note: local changes were stashed in the submodule(s) below before the failed update:")
            for path, ref in stashed.items():
                print(f"  git -C {path} stash list")
        sys.exit(1)

    if stashed:
        resolve_stashes(stashed)

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
