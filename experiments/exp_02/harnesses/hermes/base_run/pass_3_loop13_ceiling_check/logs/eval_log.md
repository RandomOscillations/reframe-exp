# Evaluation Log

## Baseline and previous best context

- Baseline verification: `./.venv/bin/python scripts/verify.py` PASS.
- Original Model C official global: 0.671529.
- P2F3 official global/public: 0.677073 / 0.676846.
- ED-next-curing-hotwet-1 official global/public: 0.687626 / 0.687405.

## Loop 13 continuation commands

Search script:
```bash
.venv/bin/python scripts/search_hotwet_next.py --trials 500 | tee runs/logs/search_hotwet_next.log
```
The all-family run timed out before final emit, so families were executed individually. Search counts:
- `boreal_protected_wetcomp`: 500 Optuna trials.
- `arid_curing_attenuation`: 500 Optuna trials.
- `wet_productivity_curing_attenuation`: 500 Optuna trials.
- `combined_protect_attenuate`: 300 Optuna trials after timeout.
- deterministic arid+boreal protection grid: 48 combinations, top 6 official global, selected regional runs.

Official global/regional ILAMB:
```bash
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-loop13-aridatt ED-loop13-wetprodatt ED-loop13-borealprotect ED-loop13-combined ED-loop13-borealdiag \
  --build_dir ilamb/output_candidates_loop13_global

ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-loop13-aridboreal-0 ED-loop13-aridboreal-1 ED-loop13-aridboreal-2 ED-loop13-aridboreal-3 ED-loop13-aridboreal-4 ED-loop13-aridboreal-5 \
  --build_dir ilamb/output_candidates_loop13_aridboreal_global
```
Regional runs were completed for `ED-loop13-aridatt`, `ED-loop13-wetprodatt`, `ED-loop13-borealprotect`, `ED-loop13-combined`, `ED-loop13-borealdiag`, `ED-loop13-aridboreal-0`, `ED-loop13-aridboreal-3`, and `ED-loop13-aridboreal-5`.

Public TRENDY/firepipe:
```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" MODEL_NAME="ED-loop13-aridatt" SRC="$PWD/runs/candidates/loop13_arid_curing_attenuation_opt500/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" MODEL_NAME="ED-loop13-aridboreal-5" SRC="$PWD/runs/candidates/loop13_arid_boreal_grid_5/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" MODEL_NAME="ED-loop13-combined" SRC="$PWD/runs/candidates/loop13_combined_protect_attenuate_opt300/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh
```
Known caveat: JSBACH produced the known ILAMB `IndexError`; score tables completed.

## Official global ILAMB summary

Full table: `runs/tables/continued_loop13_global_scores.md`.

Key rows:

| Model | Overall | Bias | RMSE | Seasonal | Spatial | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ED-loop13-combined | 0.690564 | 0.745298 | 0.522464 | 0.859230 | 0.803364 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridatt | 0.690378 | 0.745436 | 0.523449 | 0.857251 | 0.802306 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridboreal-5 | 0.690073 | 0.745667 | 0.522883 | 0.856854 | 0.802077 | Rejected: partial boreal recovery but not balanced |
| ED-loop13-wetprodatt | 0.688892 | 0.744718 | 0.521065 | 0.857322 | 0.800290 | Rejected: BONA/BOAS damage |
| ED-loop13-borealprotect | 0.688726 | 0.744697 | 0.520973 | 0.857421 | 0.799568 | Rejected: BONA/BOAS damage |
| ED-loop13-borealdiag | 0.688133 | 0.744463 | 0.519621 | 0.857194 | 0.799763 | Rejected: marginal global gain and BONA loss |
| ED-next-curing-hotwet-1 | 0.687626 | 0.744018 | 0.518584 | 0.857581 | 0.799362 | Retained best balanced |
| ED-p2f3-seed2 | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 | Regional-broad alternate |

## Regional highlights versus ED-next-curing-hotwet-1

Hotwet-1: BONA 0.769133, BOAS 0.729333, AUST 0.681726, MIDE 0.392997.

Loop 13 candidates:
- `ED-loop13-combined`: BONA 0.703762, BOAS 0.701550, AUST 0.681661, MIDE 0.411305. Rejected: MIDE/global gains are bought with boreal damage.
- `ED-loop13-aridatt`: BONA 0.695631, BOAS 0.693656, AUST 0.677449, MIDE 0.417546. Rejected: severe boreal/AUST tradeoff.
- `ED-loop13-aridboreal-5`: BONA 0.729587, BOAS 0.720784, AUST 0.677449, MIDE 0.417530. Rejected: partial boreal protection but still worse than hotwet-1 in BONA/BOAS/AUST/CEAM/SEAS/EQAS.
- `ED-loop13-borealdiag`: BONA 0.751941, BOAS 0.729618, AUST 0.682525. Rejected: not a step-function improvement; BONA still below hotwet-1.

Full regional table: `runs/tables/continued_loop13_regional_scores.md`.

## Public TRENDY/firepipe

Full public table: `runs/tables/public_ED-loop13-combined_top.md`.

Top rows:
- `ED-loop13-combined`: 0.690353.
- `ED-loop13-aridatt`: 0.690170.
- `ED-loop13-aridboreal-5`: 0.689864.
- `ED-next-curing-warmwet-nowarmgate`: 0.688384.
- `ED-next-curing-hotwet-1`: 0.687405.

Public score alone would favor loop 13 combined/arid candidates, but official regional ILAMB rejects them as not scientifically acceptable replacements.
