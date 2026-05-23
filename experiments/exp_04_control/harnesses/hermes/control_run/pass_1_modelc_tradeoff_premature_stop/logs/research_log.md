# Research Log

## Initialization
- Read required workspace instructions and baseline documentation: `AGENTS.md`, `program.md`, `WORKSPACE_MANIFEST.md`, `BASELINE_REPRO.md`, `README.md`, `WRITEUP.md`, `models/C/formula.md`.
- Confirmed constraints: one global mechanistic formula; no external inputs, lat/lon hacks, named-region routing, per-cell lookup, per-region formulas, arbitrary residual correction, or prior experiment evidence.

## Baseline reproduction
- Ran `.venv/bin/python scripts/verify.py` before model changes. Input hashes OK, but existing generated NetCDF artifacts differed by size/hash from `CHECKSUMS.txt` before regeneration:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13600931 bytes, got 13466737 bytes.
  - `out_terms/modelC_terms.nc`: expected 112006460 bytes, got 116077308 bytes.
- Ran `.venv/bin/python scripts/reproduce_modelC.py`; regenerated `ilamb/MODELS/ED-ModelC-final/burntArea.nc` from original Model C parameters.
- First `bash scripts/run_ilamb.sh` failed because `ilamb-run` was not on PATH. Reran with `.venv/bin` on PATH and `ILAMB_ROOT=$PWD/ilamb`.
- Official global ILAMB baseline completed in `ilamb/output_modelC`.
- Official GFED-region ILAMB baseline completed in `ilamb/output_modelC_regions` using built-in GFED regions.

## Mechanism search setup
- Added `scripts/run_modelC_mechanism_experiments.py` to run constrained exploratory Optuna searches over unified global mechanism families using only allowed fields.
- Candidate families encoded:
  1. `base_refit`: original Model C structure, refit under a global + regional proxy objective.
  2. `precip_shape`: original Model C plus exponents on annual precipitation floor and monthly rainfall dampening.
  3. `temp_window`: original Model C plus high-temperature suppression, representing heat/extreme aridity limits.
  4. `humid_suppression`: original Model C plus annual-precipitation humid/fuel-moisture suppression.
  5. `fuel_moisture_balance`: original Model C plus a smooth dryness relief of monthly precipitation dampening.

## Search results
- Ran 500 Optuna trials per family, 2500 total trials across 5 families.
- Proxy objective deliberately included global behavior plus regional mean/worst-tail diagnostics.
- Proxy results suggested regional robustness gains were possible, especially for `fuel_moisture_balance`, `precip_shape`, and `humid_suppression`, but proxy global scores were not clearly better than original C.

## Official evaluation results
- Ran official global ILAMB for all candidates. No candidate beat original Model C globally.
- Ran official regional ILAMB over GFED regions for all candidates. Several candidates improved derived regional diagnostics materially, but every such improvement traded away too much global spatial/seasonal performance.
- Closest global candidate: `ED-ModelC-temp_window`, Overall 0.659200 vs Model C 0.671529.
- Best regional mean candidate: `ED-ModelC-precip_shape`, derived regional mean 0.615108 vs Model C 0.560591, but global Overall fell to 0.646299.
- Best worst-region repair: `ED-ModelC-fuel_moisture_balance`, min derived regional Overall 0.421151 vs Model C 0.361275, but global Overall fell to 0.657146.

## Ablation/diagnostics
- Ran proxy ablations for added mechanisms in `scripts/run_proxy_ablations.py`.
- Results written to `experiments/modelC_mechanism_search/proxy_ablation_scores.csv`.
- Added terms were not consistently decisive: some improved proxy global spatial while degrading regional mean/min, indicating the regional gains mostly came from refit tradeoffs and not a clean step-function mechanism.

## Public benchmark
- Ran isolated public TRENDY/firepipe comparison using `scripts/run_public_trendy_firepipe_clean.sh` for reproduced final Model C.
- Output: `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-reproduced`.
- Reproduced final Model C scored 0.671274 in the public clean run, ahead of CLASSIC 0.666048 and CLM6.0 0.660644. The clean root's pre-existing `ED-ModelC-baseline` artifact scored 0.675085.
