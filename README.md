# SWT Worm Suite — Local (conda)

Unified analysis suite for C. elegans tracking, food encounter analysis, and optogenetics experiments.
Runs natively on Windows, Mac, and Linux using an isolated micromamba environment — no Docker, no browser, full access to all drives and USB storage.

---

## Quick Start

### Clone (first time)
```
git clone --recurse-submodules https://github.com/cbainbri/SWT_worm_suite_conda.git
```

### Install (first time only)
```
python setup.py
```
Opens a window, detects your GPU, then installs micromamba, creates the isolated `worm_suite` environment, and downloads the SAM model weights (~1.2 GB). Takes 10–20 minutes.

### Every launch after that
**Windows:** double-click `launch.bat`
**Mac/Linux:** `./launch.sh`  or  `python3 start.py`

---

## Tools

### Tracking Pipeline
| Script | Purpose |
|---|---|
| `track_preview.py` | Tune tracking parameters on a single directory before batch runs |
| `batch_tracking_food.py` | Batch track food encounter experiments |
| `batch_tracking_gpu_accel_food.py` | Same, GPU-accelerated |
| `batch_tracking_opto.py` | Batch track optogenetics experiments |
| `track_editor_food.py` | Manually correct food encounter tracks |
| `track_editor_opto.py` | Manually correct opto tracks |

### Food Encounter Analysis
| Script | Purpose |
|---|---|
| `automatic_mask_borders.py` | Draw or auto-generate food mask using SAM |
| `merge_files.py` | Convert wide-format CSVs to long-format composite |
| `bootstrap_food.py` | Richards curve fitting with bootstrap bagging |
| `bootstrap_food_vectorized.py` | Vectorized bootstrap (faster on large datasets) |
| `permutation_food.py` | Permutation testing on bootstrap results |
| `graph_viewer_food.py` | Visualize fits, traces, and violin plots |

### Opto Analysis
| Script | Purpose |
|---|---|
| `merge_files.py` | Convert wide-format opto CSVs to long-format composite |
| `bootstrap_opto.py` | Decay-recovery curve fitting with bootstrap bagging |
| `graph_viewer_opto.py` | Visualize bootstrap results |

---

## Updating the analysis scripts

The `tracking/`, `food_analysis/`, and `opto_analysis/` directories are git submodules pointing to their own source repos. To pull the latest scripts from all three at once, run:

```
python update.py
```

This fetches the latest commits from each source repo and records the update. You can also run the git command directly:

```
git submodule update --remote
git commit -m "update submodules"
```

---

## Why micromamba?

All scripts run through the isolated `worm_suite` conda environment — never your system Python.
- No dependency conflicts with anything else on your machine
- Full native access to all drives and USB storage (plug in, browse to it — done)
- GPU acceleration works directly with your installed drivers
- Works on Windows, Mac (Intel + Apple Silicon), and Linux

## GPU

Selected during `python setup.py`. To switch GPU type later, just run `python setup.py` again — it reinstalls torch without recreating the full environment.
