# Research Log

## 2026-05-23T02:13Z — startup and baseline prerequisites

Read required files before changing model code/parameters: `AGENTS.md`, `program.md`, `WORKSPACE_MANIFEST.md`, `BASELINE_REPRO.md`, `README.md`, `WRITEUP.md`, and `models/C/formula.md`.

Understanding: start from original Model C, keep one global mechanistic formula under the fixed input contract, no external inputs or region/cell identity hacks, evaluate with official global and regional ILAMB, use clean `public_benchmark_clean` for serious TRENDY/firepipe comparisons, maintain auditable logs, and continue mechanism loops until a defensible stopping point.

Initial prerequisite checks:
- `.venv/bin/python scripts/verify.py` found all expected files present and all pinned input/parameter hashes OK.
- Two generated artifacts differed from pinned by size before regeneration:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13,600,931 bytes, found 13,466,737 bytes.
  - `out_terms/modelC_terms.nc`: expected 112,006,460 bytes, found 116,077,308 bytes.
- This difference is recorded before proceeding, per `BASELINE_REPRO.md`. The model input arrays and `models/C/params.json` matched pinned hashes.
- `.venv/bin/python scripts/reproduce_modelC.py` regenerated `ilamb/MODELS/ED-ModelC-final/burntArea.nc` from the original Model C params.
- `bash scripts/run_ilamb.sh` required local environment fixes: `ilamb-run` was in `.venv/bin`, and ILAMB required `ILAMB_ROOT=$PWD/ilamb`. Re-run as `PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh`.

Baseline Model C official global ILAMB completed successfully in `ilamb/output_modelC`.

## Baseline research stance

Model C is already strong globally. The main scientific path is not a scalar leaderboard tweak, but to ask which regional failures reveal a missing global mechanism. The immediate triage target is regional behavior, especially regions with low spatial/RMSE components despite strong seasonal timing.


## Loop 1 — Missing landscape/fuel-continuity mechanisms

Regional triage showed weak regions mostly have acceptable seasonal phase but poor magnitude/spatial allocation. Structural analogy: Model C behaves like a simple series circuit of necessary climatic gates. The failures suggested missing “firebreak/continuity fuses”: regimes where climate and ignition timing are permissive, but burned area stays small because fuel continuity, humid closure, agricultural fragmentation, or rapid post-rain curing constraints prevent spread. Under the fixed input contract, these can only be inferred indirectly from annual/monthly precipitation, dbar, monthly GPP, and temperature.

Implemented `scripts/experiment_fire_search.py` for global-formula candidate searches. It uses only fixed inputs and GFED/ILAMB for evaluation. Region masks are used only in objective diagnostics, never as formula inputs.

Mechanism families searched:
1. `wet_firebreak`: annual wetness high-end suppressor, analogous to a circuit fuse that trips in humid/fuel-closed regimes.
2. `gpp_asym`: asymmetric GPP dose-response, analogous to a dose-response curve where too little fuel and too much wet productivity both reduce spread.
3. `curing_ratio`: monthly rain dampening buffered by accumulated dbar, analogous to a queue/bottleneck where a wet month matters less after a long dry buildup.

Optuna runs:
- C1 wet firebreak: 500 trials, regional objective.
- C2 asymmetric GPP: 500 trials, regional objective.
- C3 curing ratio: 500 trials, regional objective.
- C4 curing ratio: 700 trials, global objective.

Official ILAMB was run for all candidates. Public TRENDY/firepipe was run for the serious near-global candidate C4 and for regenerated C0 baseline.

Outcome: no candidate delivered a defensible step-function improvement. C4 improved official global Spatial Distribution (0.7822 vs 0.7724) and Bias slightly, but lost RMSE and Seasonal and official Overall (0.6697 vs 0.6715). Regionally, C1-C3 can improve weak regions only by suppressing too broadly, causing global spatial collapse and/or severe underburn in boreal/savanna systems. This is evidence that the weak-region failure is real but not cleanly resolvable with a simple additional global gate from the existing five inputs.
