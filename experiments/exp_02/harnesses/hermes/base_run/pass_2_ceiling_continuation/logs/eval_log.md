# Evaluation Log

## Baseline

- `./.venv/bin/python scripts/verify.py`: PASS.
- Official baseline global/regional ILAMB run completed.

## P2F3 best-so-far before this continuation

P2F3 continued search:
```bash
.venv/bin/python scripts/search_p2f3_continued.py | tee runs/logs/search_p2f3_continued_corrected.log
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-p2f3-seed2 ED-p2f3-opt2 ED-p2f3-nolow2 ED-p2f3-nohigh2 \
  --build_dir ilamb/output_candidates_p2f3_corrected_global
```

P2F3 official global Overall was 0.677073 and public TRENDY/firepipe was 0.676846.

## Continuation commands after P2F3

P2F3 failure-directed searches:
```bash
.venv/bin/python scripts/search_p2f3_next.py --trials 700 | tee runs/logs/search_p2f3_next.log
# The full multi-family command timed out before emit; families were then run separately with 500 trials each.
```

Individual 500-trial searches:
```bash
.venv/bin/python - <<'PY'
import sys; sys.path.insert(0,'scripts')
import search_p2f3_next as s
for fam,seed,name in [
 ('low_arid_warm_gate',401,'next_low_arid_warm_gate_opt500'),
 ('cold_continental_relax',402,'next_cold_continental_relax_opt500'),
 ('curing_phase',403,'next_curing_phase_opt500'),
 ('curing_with_wet_comp',404,'next_curing_wet_comp_opt500')]:
    p,n=s.run_family(fam,500,seed)
    s.emit(name,fam,p,'500-trial Optuna P2F3 continuation',n)
PY
```

Curing refinement:
```bash
.venv/bin/python scripts/search_p2f3_curing_refine.py | tee runs/logs/search_p2f3_curing_refine.log
```

Official global/regional ILAMB was run for:
- `ED-next-coldrelax`, `ED-next-curing`, `ED-next-curing-wet`
- `ED-next-curing-warmwet`, `ED-next-curing-warmwet-nowet`, `ED-next-curing-warmwet-nocure`, `ED-next-curing-warmwet-nowarmgate`
- `ED-next-curing-scale-0p2`, `0p35`, `0p5`, `0p65`, `0p8`, `1p0`, `1p25`
- `ED-next-curing-hotwet-0`, `1`, `2`, `3`

Public TRENDY/firepipe was run for the serious accepted/rejected top candidates:
```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
MODEL_NAME="ED-next-curing-hotwet-1" \
SRC="$PWD/runs/candidates/next_curing_hotwet_grid_1/burntArea.nc" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh

TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
MODEL_NAME="ED-next-curing-warmwet-nowarmgate" \
SRC="$PWD/runs/candidates/next_curing_warmwet_no_warmgate_ablation/burntArea.nc" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```
Known caveat: JSBACH produced the known ILAMB `IndexError`, but score tables completed.

## Official global ILAMB: full continued search

See `runs/tables/continued_next_global_scores.md`. Key rows:

| Model | Overall Score | Bias Score | RMSE Score | Seasonal Cycle Score | Spatial Distribution Score | Period Mean (original grids) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ED-next-curing-warmwet-nowarmgate | 0.688603 | 0.744397 | 0.520711 | 0.858030 | 0.799164 | 0.453583 |
| ED-next-curing-warmwet | 0.688292 | 0.744508 | 0.520161 | 0.857611 | 0.799019 | 0.457118 |
| ED-next-curing-hotwet-0 | 0.688033 | 0.744401 | 0.519319 | 0.857447 | 0.799681 | 0.466588 |
| ED-next-curing-hotwet-1 | 0.687626 | 0.744018 | 0.518584 | 0.857581 | 0.799362 | 0.471262 |
| ED-next-curing-scale-1p25 | 0.684994 | 0.740401 | 0.515725 | 0.854069 | 0.799049 | 0.526501 |
| ED-next-curing | 0.684534 | 0.740517 | 0.515532 | 0.853681 | 0.797406 | 0.515936 |
| ED-next-curing-scale-0p35 | 0.680952 | 0.739764 | 0.514287 | 0.850744 | 0.785677 | 0.485181 |
| ED-p2f3-seed2 | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.466368 |
| ED-next-coldrelax | 0.676930 | 0.739103 | 0.512622 | 0.847835 | 0.772470 | 0.469110 |

## Official regional ILAMB: accepted final vs P2F3

`ED-next-curing-hotwet-1` vs `ED-p2f3-seed2`:

| Region | P2F3 Overall | Hotwet-1 Overall | Delta | Main note |
| --- | ---: | ---: | ---: | --- |
| global | 0.677073 | 0.687626 | +0.010553 | Step global gain; Spatial +0.026689; Seasonal +0.009502 |
| bona | 0.771207 | 0.769133 | -0.002074 | BONA essentially preserved vs P2F3; no collapse |
| tena | 0.414691 | 0.419723 | +0.005032 | Weak dryland gain vs P2F3 |
| ceam | 0.403716 | 0.393815 | -0.009901 | Regresses; still above original Model C |
| nhsa | 0.606292 | 0.584617 | -0.021675 | Regresses |
| shsa | 0.545642 | 0.517434 | -0.028208 | Regresses |
| euro | 0.385437 | 0.404197 | +0.018760 | Weak-region gain vs P2F3 |
| mide | 0.419018 | 0.392997 | -0.026021 | Regresses; still above original Model C |
| nhaf | 0.653435 | 0.683038 | +0.029603 | Large spatial gain |
| shaf | 0.656661 | 0.689496 | +0.032835 | Large spatial gain |
| boas | 0.728730 | 0.729333 | +0.000603 | Preserved/slight gain |
| ceas | 0.679173 | 0.682268 | +0.003095 | Slight gain |
| seas | 0.511484 | 0.504324 | -0.007160 | Regresses but remains above original Model C |
| eqas | 0.629088 | 0.621145 | -0.007943 | Regresses but retains most P2F3 gain |
| aust | 0.667783 | 0.681726 | +0.013943 | Material AUST improvement; Seasonal +0.027789 |

Full selected regional table: `runs/tables/continued_next_regional_scores.md`.

## Public TRENDY/firepipe

Accepted final:
- `ED-next-curing-hotwet-1` public Overall 0.687405, ranked #1 in the public table, above P2F3 0.676846.
- Public table path: `runs/tables/public_ED-next-curing-hotwet-1_top.md` and `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`.

Rejected top-scalar:
- `ED-next-curing-warmwet-nowarmgate` public Overall 0.688384, but rejected due BONA/BOAS regional spatial damage.
- Public table path: `runs/tables/public_ED-next-curing-warmwet-nowarmgate_top.md`.
