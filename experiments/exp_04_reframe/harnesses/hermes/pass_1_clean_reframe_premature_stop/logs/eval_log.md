# Evaluation Log

## Baseline Model C reproduction

Workspace: `/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_04-reframe/hermes/reframe`

Prerequisite verification:

Command:

```bash
.venv/bin/python scripts/verify.py
```

Result:
- Present: 24, Missing: 0.
- Hash OK: 22, Mismatch: 2.
- Mismatches were generated artifacts only, recorded before proceeding:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13,600,931 bytes, got 13,466,737 bytes.
  - `out_terms/modelC_terms.nc`: expected 112,006,460 bytes, got 116,077,308 bytes.
- All fixed inputs and `models/C/params.json` matched pinned hashes.

Baseline regeneration:

```bash
.venv/bin/python scripts/reproduce_modelC.py
```

Key output:
- Params: original `models/C/params.json`.
- Land cells: 13,826 / 64,800.
- Raw rate land mean: 0.09018 yr^-1; max 0.9987 yr^-1; cap 5.0 yr^-1.
- ED-transformed land mean: 0.00610759; GFED land mean: 0.00298745; ratio 2.044.
- Wrote `ilamb/MODELS/ED-ModelC-final/burntArea.nc`.

Official global ILAMB:

```bash
PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh
```

Output directory: `ilamb/output_modelC`

Global scalar scores for `ED-ModelC-final`:

| Metric | Score |
|---|---:|
| Bias Score | 0.7281 |
| RMSE Score | 0.5058 |
| Seasonal Cycle Score | 0.8457 |
| Spatial Distribution Score | 0.7724 |
| Overall Score | 0.6715 |

Official regional ILAMB run:

```bash
PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-ModelC-final \
  --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust \
  --build_dir ilamb/output_modelC_regions \
  --skip_plots
```

Output directory: `ilamb/output_modelC_regions`


## Loop 1 candidate official ILAMB

Search script: `scripts/experiment_fire_search.py`.

Official global candidate run:

```bash
PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-ModelC-final ED-ModelC-curing_ratio-g700 ED-ModelC-curing_ratio-r500 ED-ModelC-gpp_asym-r500 ED-ModelC-wet_firebreak-r500 \
  --regions global \
  --build_dir ilamb/output_candidates_loop1_global_full
```

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| ED-ModelC-curing_ratio-g700 | 0.729482 | 0.499233 | 0.838594 | 0.782165 | 0.669741 |
| ED-ModelC-curing_ratio-r500 | 0.699994 | 0.510097 | 0.827503 | 0.301372 | 0.569813 |
| ED-ModelC-gpp_asym-r500 | 0.722221 | 0.516424 | 0.843135 | 0.610321 | 0.641705 |
| ED-ModelC-wet_firebreak-r500 | 0.713542 | 0.515713 | 0.830597 | 0.516938 | 0.618500 |

Official regional candidate run:
- Output: `ilamb/output_candidates_loop1/scalar_database.csv`
- Extracted diagnostic CSV: `experiments/loop1_official_regional_components.csv`

Clean public TRENDY/firepipe:

Commands used via `scripts/run_public_trendy_firepipe_clean.sh`:
- C0 regenerated baseline: `MODEL_NAME=ED-ModelC-final-c0 SRC=ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- C4 serious candidate: `MODEL_NAME=ED-ModelC-curing_ratio-g700 SRC=ilamb/MODELS/ED-ModelC-curing_ratio-g700/burntArea.nc`

Public output for C4: `public_benchmark_clean/ilamb/output_with_ED-ModelC-curing_ratio-g700`.

Top public rows from C4 run:

| Rank | Model | Overall |
|---:|---|---:|
| 1 | ED-ModelC-baseline | 0.675085 |
| 2 | ED-ModelC-final-c0 | 0.671274 |
| 3 | ED-ModelC-curing_ratio-g700 | 0.669487 |
| 4 | CLASSIC | 0.666048 |
| 5 | CLM6.0 | 0.660644 |
| 6 | CLM-FATES | 0.656831 |
| 7 | ELM-FATES | 0.656788 |
| 8 | JULES-ES | 0.590519 |

Note: public benchmark reports a setup `ED-ModelC-baseline` already present in `public_benchmark_clean`, slightly ahead of the regenerated C0 artifact. Both are inside the clean workspace benchmark root. The candidate C4 remains above public comparator models but below both Model C artifacts.
