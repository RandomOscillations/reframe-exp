# Evaluation Log

Record exact evaluation commands and output directories here.

## Baseline / original Model C

Timestamp: 2026-05-13 local session.

Commands:

```bash
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_baseline" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_baseline" bash scripts/run_official_regions.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" MODEL_NAME="ED-ModelC-baseline-formal" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-baseline-formal" bash scripts/run_public_trendy_firepipe.sh
```

Output directories:
- Global official ILAMB: `ilamb/output_modelC_baseline`
- Regional official ILAMB: `ilamb/output_regions_baseline`
- Public TRENDY/firepipe: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-baseline-formal`

Score summary:

| Metric | Value |
|---|---:|
| Bias Score | 0.728089 |
| RMSE Score | 0.505759 |
| Seasonal Cycle Score | 0.845690 |
| Spatial Distribution Score | 0.772351 |
| Overall Score | 0.671529 |
| Period Mean (original grids) | 0.611164 |

Public benchmark: rank #1, Overall 0.671274. JSBACH produced the known public benchmark `IndexError`; completed candidate/model comparisons remain usable.

Accepted as evidence: yes.

## WET-SUPP-v1

Commands:

```bash
.venv/bin/python scripts/scan_candidate_wet_suppression.py
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_wet_supp_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_wet_supp_v1" bash scripts/run_official_regions.sh
```

Output directories:
- Global official ILAMB: `ilamb/output_modelC_wet_supp_v1`
- Regional official ILAMB: `ilamb/output_regions_wet_supp_v1`
- Search output: `out_candidate_wet_suppression.json`

Score summary:

| Metric | Value | Delta vs baseline |
|---|---:|---:|
| Bias Score | 0.729325 | +0.001236 |
| RMSE Score | 0.506214 | +0.000455 |
| Seasonal Cycle Score | 0.845835 | +0.000145 |
| Spatial Distribution Score | 0.769334 | -0.003017 |
| Overall Score | 0.671384 | -0.000145 |
| Period Mean (original grids) | 0.583389 | -0.027775 |

Accepted as evidence: yes. Accepted as model: no; official global declined and regional savanna/Australia damage remains.

## LAG+WET-v1

Commands:

```bash
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_lag_wet_combo_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_lag_wet_combo_v1" bash scripts/run_official_regions.sh
```

Output directories:
- Global official ILAMB: `ilamb/output_modelC_lag_wet_combo_v1`
- Regional official ILAMB: `ilamb/output_regions_lag_wet_combo_v1`

Score summary:

| Metric | Value | Delta vs baseline |
|---|---:|---:|
| Bias Score | 0.728988 | +0.000899 |
| RMSE Score | 0.506241 | +0.000482 |
| Seasonal Cycle Score | 0.850932 | +0.005242 |
| Spatial Distribution Score | 0.768463 | -0.003888 |
| Overall Score | 0.672173 | +0.000644 |
| Period Mean (original grids) | 0.592258 | -0.018906 |

Accepted as evidence: yes. Accepted as model: no; still regional damage and lower global than pure LAG-FUEL.

## LAG-FUEL-v1

Commands:

```bash
.venv/bin/python scripts/scan_candidate_lagged_fuel.py
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_lag_fuel_pure_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_lag_fuel_pure_v1" bash scripts/run_official_regions.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" MODEL_NAME="ED-ModelC-lag-fuel-pure-v1" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-lag-fuel-pure-v1" bash scripts/run_public_trendy_firepipe.sh
```

Output directories:
- Global official ILAMB: `ilamb/output_modelC_lag_fuel_pure_v1`
- Regional official ILAMB: `ilamb/output_regions_lag_fuel_pure_v1`
- Public TRENDY/firepipe: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-lag-fuel-pure-v1`
- Search output: `out_candidate_lagged_fuel.json`

Score summary:

| Metric | Value | Delta vs baseline |
|---|---:|---:|
| Bias Score | 0.727752 | -0.000337 |
| RMSE Score | 0.505788 | +0.000029 |
| Seasonal Cycle Score | 0.850890 | +0.005200 |
| Spatial Distribution Score | 0.771151 | -0.001200 |
| Overall Score | 0.672274 | +0.000745 |
| Period Mean (original grids) | 0.620074 | +0.008910 |

Public benchmark: rank #1, Overall 0.672014. JSBACH produced the known public benchmark `IndexError`. Caveat: public script symlinked multiple formal model names to the same workspace file, so the candidate public run printed an identical `ED-ModelC-baseline-formal` row; use the baseline run's `output_with_ED-ModelC-baseline-formal` for baseline public score.

Accepted as evidence: yes. Accepted as model: no; global gain hides regional damage.

## PRECIP-MEM-v1

Commands:

```bash
.venv/bin/python scripts/scan_candidate_precip_memory.py
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_precip_mem_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_precip_mem_v1" bash scripts/run_official_regions.sh
```

Output directories:
- Global official ILAMB: `ilamb/output_modelC_precip_mem_v1`
- Regional official ILAMB: `ilamb/output_regions_precip_mem_v1`
- Search output: `out_candidate_precip_memory.json`

Score summary:

| Metric | Value | Delta vs baseline |
|---|---:|---:|
| Bias Score | 0.728316 | +0.000227 |
| RMSE Score | 0.506595 | +0.000836 |
| Seasonal Cycle Score | 0.846707 | +0.001017 |
| Spatial Distribution Score | 0.762754 | -0.009597 |
| Overall Score | 0.670193 | -0.001336 |
| Period Mean (original grids) | 0.582927 | -0.028237 |

Accepted as evidence: yes. Accepted as model: no; global and spatial decline with African savanna damage.

## Final restoration / verification

Commands:

```bash
cp models/C/params.BASELINE-formal.json models/C/params.json
.venv/bin/python scripts/reproduce_modelC.py
sha256sum models/C/params.json ilamb/MODELS/ED-ModelC-final/burntArea.nc
.venv/bin/python scripts/verify.py
```

Hashes after restoration:

```text
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
```

Final `scripts/verify.py`: PASS.
