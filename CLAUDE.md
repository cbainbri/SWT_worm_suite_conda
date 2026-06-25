# CLAUDE.md — SWT Worm Suite

## Project Overview
Unified, containerized suite of C. elegans analysis tools combining tracking, food encounter analysis, and optogenetics analysis pipelines. Target: single entry point that runs on Linux, Mac, and Windows via conda (local) or Docker + noVNC (container).

## Directory Structure
```
SWT_worm_suite/
├── tracking/               food + opto tracking and editing tools
├── food_analysis/          masking, merging, bootstrap, permutation, graphing (food)
│   └── segmentation/       SAM model weights live here (gitignored, downloaded via download_models.py)
├── opto_analysis/          merging, bootstrap, graphing (opto)
├── docker/                 Dockerfile support files (start.sh, etc.)
├── launcher.py             unified GUI launcher — accordion UI, categorized by pipeline
├── download_models.py      downloads sam_vit_l_0b3195.pth (~1.2GB) into food_analysis/segmentation/
├── environment.yml         conda environment (all deps, cross-platform)
├── requirements.txt        pip fallback
├── Dockerfile              noVNC container build (Linux desktop in browser at localhost:6080)
├── docker-compose.yml      one-command container launch
└── README.md
```

## Progress

### Done
- [x] Directory structure created
- [x] All 16 scripts copied from tracking_pipeline, food_encounter_analysis, opto_analysis
- [x] segmentation/.gitkeep in food_analysis/
- [x] download_models.py written
- [x] launcher.py — accordion UI with collapsible categories (Tracking / Food / Opto), dark header theme, each tool opens as subprocess

### In Progress
- [x] environment.yml — unified conda environment
- [x] requirements.txt — unified pip requirements
- [x] Dockerfile — Ubuntu 22.04 + noVNC + all deps (SAM weights NOT baked in, mounted as volume)
- [x] docker/start.sh — Xvfb + fluxbox + x11vnc + noVNC startup script
- [x] docker-compose.yml — mounts food_analysis/segmentation/ + data/, exposes port 6080
- [x] README.md — conda path + Docker path documented, SAM volume mount clearly explained
- [ ] git init + initial commit
- [ ] GitHub repo (private)

### Not Started
- [x] Test launcher on Windows — accordion UI confirmed working
- [x] setup.py — Tkinter GUI, auto-detects GPU, writes .env, kicks off docker compose
- [x] docker-compose.nvidia.yml — NVIDIA GPU passthrough override
- [x] docker-compose.amd.yml — AMD ROCm device passthrough override
- [x] .env.example — documents GPU_TYPE options
- [x] Dockerfile updated — GPU_TYPE build arg, installs correct torch (cpu/cuda/rocm)
- [x] requirements.txt — torch removed, handled by Dockerfile
- [x] start.py — starts container in detached mode, polls port, opens browser automatically; handles port conflicts
- [x] setup.py updated — also opens browser automatically after build
- [x] docker-compose.yml — NOVNC_PORT env var for configurable port
- [ ] Test Docker build end-to-end
- [ ] Test noVNC GUI on Mac/Linux

## Key Decisions
- **Launcher UI:** accordion-style Tkinter window — categories collapse/expand, scripts are individual launch buttons. Each script opens as its own subprocess in its own window. No redesign of individual tool UIs.
- **SAM model:** not in git, not baked into Docker image. `docker/start.sh` calls `download_models.py` as its first step — downloads ~1.2GB to the mounted `food_analysis/segmentation/` volume on first run, skips instantly if already present. Script auto-detects on launch.
- **Container approach:** Docker + noVNC (Xfce desktop in browser). Users open `localhost:6080`. All Tkinter/PyQt5 GUIs work unchanged. GPU optional via NVIDIA Container Toolkit.
- **Local approach:** conda environment (`environment.yml`). `conda env create -f environment.yml` + `python download_models.py` + `python launcher.py`.

## Notes for Claude
- Only read/copy from sibling directories — never modify `tracking_pipeline/`, `food_encounter_analysis/`, or `opto_analysis/` from within this project
- The SAM model path expected by `automatic_mask_borders.py` is `./segmentation/` relative to the script file — keep the script in `food_analysis/` and weights in `food_analysis/segmentation/`
- `bootstrap_opto.py` uses PyQt5 (not Tkinter) to avoid multiprocessing conflicts — launcher spawns it as a subprocess so no event loop clash
- Update the progress section of this file as work is completed
