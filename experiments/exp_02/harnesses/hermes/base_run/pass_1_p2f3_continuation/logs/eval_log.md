# Evaluation Log

## Baseline

- `./.venv/bin/python scripts/verify.py`: PASS.
- Official baseline global/regional ILAMB run completed.

## Continuation commands

Cold/liquid/warm wet-gate grids and distinct precipitation/temperature mechanism grids were generated with `scripts/research_candidates.py` and inline deterministic grids. Serious candidates were copied into separate `ilamb/MODELS/<name>/burntArea.nc` directories and evaluated with official ILAMB.

P2F3 continued search:
```bash
.venv/bin/python scripts/search_p2f3_continued.py | tee runs/logs/search_p2f3_continued_corrected.log
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-p2f3-seed2 ED-p2f3-opt2 ED-p2f3-nolow2 ED-p2f3-nohigh2 \
  --build_dir ilamb/output_candidates_p2f3_corrected_global
```

Official regional P2F3 runs:
```bash
OUT="$PWD/ilamb/output_regions_ED-p2f3-seed2" MODEL_NAME="ED-p2f3-seed2" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
OUT="$PWD/ilamb/output_regions_ED-p2f3-nolow2" MODEL_NAME="ED-p2f3-nolow2" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
OUT="$PWD/ilamb/output_regions_ED-p2f3-nohigh2" MODEL_NAME="ED-p2f3-nohigh2" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
```

Public TRENDY/firepipe final:
```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
MODEL_NAME="ED-p2f3-current-final" \
SRC="$PWD/runs/candidates/p2f3_seed_current/burntArea.nc" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```
Known caveat: JSBACH produced the known ILAMB `IndexError`, but score table completed.

## Official global ILAMB: continued search

| Model | Overall Score | Bias Score | RMSE Score | Seasonal Cycle Score | Spatial Distribution Score | Period Mean (original grids) |
| --- | --- | --- | --- | --- | --- | --- |
| ED-p2f3-seed2 | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.466368 |
| ED-p2f3-nolow2 | 0.676981 | 0.738300 | 0.512151 | 0.845262 | 0.777043 | 0.478758 |
| ED-p2f3-opt2 | 0.676764 | 0.738236 | 0.513157 | 0.848586 | 0.770686 | 0.461376 |
| ED-p2f3-nohigh2 | 0.676040 | 0.737042 | 0.510722 | 0.850117 | 0.771599 | 0.509712 |
| ED-wet-temp-grid | 0.674491 | 0.731839 | 0.513465 | 0.845167 | 0.768522 | 0.514447 |
| ED-combo-warm-ann | 0.672911 | 0.732627 | 0.511792 | 0.845278 | 0.763068 | 0.508788 |
| ED-warm-gate-c8 | 0.672605 | 0.731496 | 0.510594 | 0.845105 | 0.765235 | 0.532080 |
| ED-drymonth-norm | 0.672018 | 0.730259 | 0.509119 | 0.848593 | 0.763001 | 0.552347 |
| ED-rain-pulse-grid | 0.671705 | 0.729434 | 0.508045 | 0.848708 | 0.764295 | 0.566025 |
| ED-ModelC-final | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.611164 |
| ED-ann-wet | 0.671188 | 0.730580 | 0.506740 | 0.846026 | 0.765854 | 0.557574 |

## Official regional ILAMB: selected models

| Model | Region | Overall Score | Bias Score | RMSE Score | Seasonal Cycle Score | Spatial Distribution Score |
| --- | --- | --- | --- | --- | --- | --- |
| ED-ModelC-final | global | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 |
| ED-ModelC-final | bona | 0.789806 | 0.883981 | 0.742535 | 0.925121 | 0.654858 |
| ED-ModelC-final | tena | 0.381473 | 0.437076 | 0.307975 | 0.694036 | 0.160304 |
| ED-ModelC-final | ceam | 0.376153 | 0.286887 | 0.310422 | 0.847470 | 0.125564 |
| ED-ModelC-final | nhsa | 0.605824 | 0.501408 | 0.493150 | 0.914425 | 0.626989 |
| ED-ModelC-final | shsa | 0.507249 | 0.473091 | 0.429758 | 0.820024 | 0.383616 |
| ED-ModelC-final | euro | 0.361128 | 0.393450 | 0.261763 | 0.808165 | 0.080499 |
| ED-ModelC-final | mide | 0.382769 | 0.436689 | 0.310067 | 0.765840 | 0.091179 |
| ED-ModelC-final | nhaf | 0.645855 | 0.769337 | 0.479548 | 0.901029 | 0.599810 |
| ED-ModelC-final | shaf | 0.646693 | 0.759732 | 0.502274 | 0.902122 | 0.567063 |
| ED-ModelC-final | boas | 0.728733 | 0.840753 | 0.619204 | 0.796639 | 0.767865 |
| ED-ModelC-final | ceas | 0.670499 | 0.783351 | 0.560258 | 0.722163 | 0.726466 |
| ED-ModelC-final | seas | 0.487193 | 0.496169 | 0.377266 | 0.826697 | 0.358569 |
| ED-ModelC-final | eqas | 0.507395 | 0.477132 | 0.523149 | 0.836452 | 0.177092 |
| ED-ModelC-final | aust | 0.670219 | 0.745626 | 0.652014 | 0.579524 | 0.721918 |
| ED-p2f3-seed2 | global | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 |
| ED-p2f3-seed2 | bona | 0.771207 | 0.883408 | 0.741203 | 0.923351 | 0.566871 |
| ED-p2f3-seed2 | tena | 0.414691 | 0.499475 | 0.358680 | 0.690093 | 0.166526 |
| ED-p2f3-seed2 | ceam | 0.403716 | 0.376508 | 0.343289 | 0.840487 | 0.115005 |
| ED-p2f3-seed2 | nhsa | 0.606292 | 0.540715 | 0.502157 | 0.915313 | 0.571118 |
| ED-p2f3-seed2 | shsa | 0.545642 | 0.570951 | 0.484417 | 0.811870 | 0.376555 |
| ED-p2f3-seed2 | euro | 0.385437 | 0.439637 | 0.290451 | 0.807493 | 0.099154 |
| ED-p2f3-seed2 | mide | 0.419018 | 0.503206 | 0.359813 | 0.759446 | 0.112814 |
| ED-p2f3-seed2 | nhaf | 0.653435 | 0.767026 | 0.480379 | 0.915245 | 0.624148 |
| ED-p2f3-seed2 | shaf | 0.656661 | 0.758657 | 0.501939 | 0.901277 | 0.619491 |
| ED-p2f3-seed2 | boas | 0.728730 | 0.842895 | 0.630159 | 0.798876 | 0.741563 |
| ED-p2f3-seed2 | ceas | 0.679173 | 0.790580 | 0.585772 | 0.735254 | 0.698485 |
| ED-p2f3-seed2 | seas | 0.511484 | 0.568322 | 0.404397 | 0.821928 | 0.358376 |
| ED-p2f3-seed2 | eqas | 0.629088 | 0.709699 | 0.588010 | 0.846438 | 0.413281 |
| ED-p2f3-seed2 | aust | 0.667783 | 0.752720 | 0.655949 | 0.560839 | 0.713459 |
| ED-p2f3-nolow2 | global | 0.676981 | 0.738300 | 0.512151 | 0.845262 | 0.777043 |
| ED-p2f3-nolow2 | bona | 0.776514 | 0.882449 | 0.740704 | 0.923328 | 0.595387 |
| ED-p2f3-nolow2 | tena | 0.409607 | 0.491567 | 0.351971 | 0.689545 | 0.162981 |
| ED-p2f3-nolow2 | ceam | 0.403094 | 0.374896 | 0.342180 | 0.843571 | 0.112642 |
| ED-p2f3-nolow2 | nhsa | 0.602467 | 0.538385 | 0.500779 | 0.915313 | 0.557078 |
| ED-p2f3-nolow2 | shsa | 0.543003 | 0.566750 | 0.484004 | 0.816890 | 0.363370 |
| ED-p2f3-nolow2 | euro | 0.376685 | 0.423869 | 0.280490 | 0.807939 | 0.090638 |
| ED-p2f3-nolow2 | mide | 0.411795 | 0.492708 | 0.351652 | 0.759879 | 0.103084 |
| ED-p2f3-nolow2 | nhaf | 0.654221 | 0.768109 | 0.479215 | 0.901900 | 0.642668 |
| ED-p2f3-nolow2 | shaf | 0.658167 | 0.758824 | 0.502073 | 0.900880 | 0.626986 |
| ED-p2f3-nolow2 | boas | 0.727854 | 0.841171 | 0.626081 | 0.798876 | 0.747060 |
| ED-p2f3-nolow2 | ceas | 0.677930 | 0.787265 | 0.581198 | 0.735177 | 0.704813 |
| ED-p2f3-nolow2 | seas | 0.509260 | 0.567966 | 0.404326 | 0.821630 | 0.348054 |
| ED-p2f3-nolow2 | eqas | 0.629021 | 0.709688 | 0.588003 | 0.846438 | 0.412971 |
| ED-p2f3-nolow2 | aust | 0.670770 | 0.751221 | 0.655478 | 0.573332 | 0.718340 |
| ED-warm-gate-c8 | global | 0.672605 | 0.731496 | 0.510594 | 0.845105 | 0.765235 |
| ED-warm-gate-c8 | bona | 0.786381 | 0.886193 | 0.743964 | 0.925184 | 0.632598 |
| ED-warm-gate-c8 | tena | 0.410084 | 0.480176 | 0.324976 | 0.699774 | 0.220516 |
| ED-warm-gate-c8 | ceam | 0.403132 | 0.358148 | 0.331568 | 0.845716 | 0.148662 |
| ED-warm-gate-c8 | nhsa | 0.609214 | 0.525950 | 0.497239 | 0.914405 | 0.611237 |
| ED-warm-gate-c8 | shsa | 0.510592 | 0.508046 | 0.433086 | 0.791105 | 0.387637 |
| ED-warm-gate-c8 | euro | 0.432033 | 0.543229 | 0.341381 | 0.809892 | 0.124284 |
| ED-warm-gate-c8 | mide | 0.399563 | 0.469429 | 0.317896 | 0.770956 | 0.121637 |
| ED-warm-gate-c8 | nhaf | 0.649117 | 0.769114 | 0.480275 | 0.900993 | 0.614925 |
| ED-warm-gate-c8 | shaf | 0.645135 | 0.748872 | 0.507823 | 0.906380 | 0.554778 |
| ED-warm-gate-c8 | boas | 0.733066 | 0.846401 | 0.623627 | 0.796639 | 0.775038 |
| ED-warm-gate-c8 | ceas | 0.683281 | 0.808984 | 0.578343 | 0.724703 | 0.726031 |
| ED-warm-gate-c8 | seas | 0.498929 | 0.538556 | 0.388148 | 0.828430 | 0.351364 |
| ED-warm-gate-c8 | eqas | 0.518737 | 0.505298 | 0.528506 | 0.830565 | 0.200811 |
| ED-warm-gate-c8 | aust | 0.672249 | 0.755360 | 0.655491 | 0.574291 | 0.720610 |
| ED-combo-warm-ann | global | 0.672911 | 0.732627 | 0.511792 | 0.845278 | 0.763068 |
| ED-combo-warm-ann | bona | 0.760457 | 0.894470 | 0.750075 | 0.925460 | 0.482205 |
| ED-combo-warm-ann | tena | 0.413688 | 0.491832 | 0.334529 | 0.700145 | 0.207402 |
| ED-combo-warm-ann | ceam | 0.408872 | 0.369446 | 0.337997 | 0.846341 | 0.152580 |
| ED-combo-warm-ann | nhsa | 0.616152 | 0.540862 | 0.503940 | 0.914147 | 0.617869 |
| ED-combo-warm-ann | shsa | 0.519399 | 0.520351 | 0.439113 | 0.795815 | 0.402603 |
| ED-combo-warm-ann | euro | 0.436752 | 0.553670 | 0.350940 | 0.808686 | 0.119524 |
| ED-combo-warm-ann | mide | 0.399539 | 0.469292 | 0.318035 | 0.771278 | 0.121055 |
| ED-combo-warm-ann | nhaf | 0.648065 | 0.768699 | 0.479914 | 0.900993 | 0.610805 |
| ED-combo-warm-ann | shaf | 0.643191 | 0.747200 | 0.506968 | 0.906289 | 0.548527 |
| ED-combo-warm-ann | boas | 0.736629 | 0.859914 | 0.643216 | 0.796646 | 0.740150 |
| ED-combo-warm-ann | ceas | 0.684611 | 0.809813 | 0.588618 | 0.723650 | 0.712355 |
| ED-combo-warm-ann | seas | 0.506435 | 0.552692 | 0.393843 | 0.828110 | 0.363689 |
| ED-combo-warm-ann | eqas | 0.542917 | 0.551343 | 0.544643 | 0.831440 | 0.242516 |
| ED-combo-warm-ann | aust | 0.671433 | 0.754973 | 0.655369 | 0.574400 | 0.717054 |

## Public TRENDY/firepipe top rows

| Model | Overall Score | Bias Score | RMSE Score | Seasonal Cycle Score | Spatial Distribution Score | Period Mean (original grids) |
| --- | --- | --- | --- | --- | --- | --- |
| ED-p2f3-current-final | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| ED-p2f3-seed-current | 0.676029 | 0.736685 | 0.511031 | 0.848158 | 0.773242 | 0.503630 |
| ED-wet-temp-grid | 0.674241 | 0.731839 | 0.513465 | 0.845167 | 0.767269 | 0.514447 |
| ED-ModelC-formal-candidate | 0.673022 | 0.731755 | 0.508111 | 0.851062 | 0.766069 | 0.547347 |
| ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| ED-ModelC-curing-lag-v1-current | 0.671767 | 0.727997 | 0.505755 | 0.848710 | 0.770616 | 0.614471 |
| ED-ModelC-lag-fuel-v1-current | 0.671600 | 0.728075 | 0.505767 | 0.848154 | 0.770237 | 0.622335 |
| ED-ModelC-opt-wet-v1-current | 0.671436 | 0.730475 | 0.506667 | 0.845975 | 0.767397 | 0.567266 |
| ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
