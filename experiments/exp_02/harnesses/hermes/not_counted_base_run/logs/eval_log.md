# Evaluation Log

## Baseline Model C
- Verification: `.venv/bin/python scripts/verify.py` PASS, all 24 pinned artifacts present and hash OK.
- Official global ILAMB: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh`.
  - Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, Overall 0.671529.
- Official regional ILAMB: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh`.

## Search/evaluation commands
- Search script created: `scripts/explore_mechanisms.py`.
- Candidate NCs and metadata: `candidates/<candidate_id>/burntArea.nc` and `candidates/<candidate_id>.json`.
- Official candidate outputs copied under `artifacts/evals/*_output_modelC*` and `artifacts/evals/*_output_regions_official*`.
- Public logs: `artifacts/evals/C6b_public_trendy_firepipe.log` (stale/cached first public run, not used for final), `artifacts/evals/C7_public_trendy_firepipe_clean.log` (clean run used).

## Official global ILAMB comparison
| Candidate | Overall | Bias | RMSE | Seasonal | Spatial |
|---|---:|---:|---:|---:|---:|
| C0 baseline | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 |
| C2 dryrate | 0.672542 | 0.729561 | 0.507665 | 0.852988 | 0.764830 |
| C6b humid suppress | 0.672691 | 0.732340 | 0.507491 | 0.845969 | 0.770162 |
| C7 humid+dryrate | 0.673264 | 0.731755 | 0.508111 | 0.851062 | 0.767279 |

## Serious candidate regional Overall comparison
| Region | Baseline | C2 dryrate | C6b humid | C7 humid+dry | Best delta vs baseline |
|---|---:|---:|---:|---:|---:|
| bona | 0.789806 | 0.787680 | 0.789910 | 0.788504 | +0.000104 |
| tena | 0.381473 | 0.387950 | 0.385201 | 0.387201 | +0.006477 |
| ceam | 0.376153 | 0.388136 | 0.394321 | 0.395297 | +0.019144 |
| nhsa | 0.605824 | 0.612135 | 0.612635 | 0.614489 | +0.008665 |
| shsa | 0.507249 | 0.514548 | 0.529248 | 0.524389 | +0.021999 |
| euro | 0.361128 | 0.368368 | 0.362372 | 0.366309 | +0.007240 |
| mide | 0.382769 | 0.385654 | 0.382955 | 0.384436 | +0.002885 |
| nhaf | 0.645855 | 0.647620 | 0.646670 | 0.648910 | +0.003055 |
| shaf | 0.646693 | 0.644307 | 0.645391 | 0.643847 | -0.001302 |
| boas | 0.728733 | 0.730300 | 0.728764 | 0.729999 | +0.001567 |
| ceas | 0.670499 | 0.674705 | 0.670835 | 0.672759 | +0.004206 |
| seas | 0.487193 | 0.496964 | 0.505065 | 0.505368 | +0.018175 |
| eqas | 0.507395 | 0.526712 | 0.589676 | 0.574394 | +0.082281 |
| aust | 0.670219 | 0.670222 | 0.668985 | 0.669813 | +0.000003 |

## Clean public TRENDY/firepipe run for final C7
Command:
`TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh`
with public output/model dirs removed first.

Caveat: JSBACH raised the known ILAMB IndexError before completing in collective post-processing; score table was produced and used.

Public ranking excerpt:
| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial | Period mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 2 | ED-ModelC-formal-candidate (C7) | 0.673022 | 0.731755 | 0.508111 | 0.851062 | 0.766069 | 0.547347 |
| 3 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| 4 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| 9 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| 10 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| 11 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |
