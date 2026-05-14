# Final Report — Continued ED Fire Model Improvement Beyond P2F3

## Executive summary

I continued from P2F3 as the current best-so-far, not as an endpoint. The continuation found a new best balanced model:

`ED-next-curing-hotwet-1`, stored as:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`

It is a unified global formula: original Model C + P2F3 wet-canopy/arid fuel-continuity suppressors + a drying/curing-phase enhancement + hot/warm-climate wet-month compensation. It uses only allowed P/T/Dbar/GPP-derived quantities and no region, latitude/longitude, cell identity, lookup, or residual correction.

Main result:
- Official global ILAMB Overall: 0.687626.
- Public TRENDY/firepipe Overall: 0.687405.
- Previous P2F3 official global: 0.677073.
- Previous P2F3 public: 0.676846.
- Official improvement over P2F3: +0.010553.
- Public improvement over P2F3: +0.010559.

This is a step-function global/public improvement over P2F3, not a third-decimal tie. It also improves global Bias, RMSE, Seasonal Cycle, and Spatial Distribution components. Regionally, it is not a strict dominance over P2F3: it improves BONA/BOAS preservation relative to the rejected high-scalar wet variants, materially improves AUST, TENA, EURO, NHAF, SHAF, and CEAS vs P2F3, but regresses CEAM, NHSA, SHSA, MIDE, SEAS, and EQAS vs P2F3. Therefore:
- Best global/public model found: `ED-next-curing-hotwet-1`.
- Best broad weak-region model remains: P2F3 (`ED-p2f3-seed2`), especially for MIDE/CEAM/EQAS and South America.
- Highest scalar model found, rejected: `ED-next-curing-warmwet-nowarmgate`, official 0.688603 and public 0.688384, because it damages BONA/BOAS spatial behavior.

## Final formula

P2F3 core:
```text
base_rate = original Model C annual rate after fire_exp

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)
deficit_ratio = Dbar / (P_ann + ratio_p0)
arid_soft   = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)
P2F3_rate = base_rate * wet_suppress * arid_soft * arid_desert
```

Continuation mechanism:
```text
drying = sigmoid(Dbar[t] - Dbar[t-1], drying_k, drying_c)
drymonth = 1 / (1 + (p_month/(P_ann/12) / pconc_half)^pconc_pow)
warm_month = sigmoid(T_air, temp_k, temp_c)
curing = drying * drymonth * warm_month

wetmonth = sigmoid(p_month/(P_ann/12), wet_k_month, wet_c_month)
warm_climate_gate = sigmoid(T_air_annual_climatology, warm_k, warm_c)

fire_rate = P2F3_rate * (1 + cure_amp * curing) *
            (1 - wet_amp_month * wetmonth * warm_climate_gate)

burntArea_month = (1 - exp(-min(fire_rate, FIRE_MAX_RATE))) / 12
```

Physical interpretation:
1. P2F3 structural controls:
   - Persistent wet-canopy inhibition suppresses humid closed-canopy regimes.
   - Two arid thresholds represent soft and hyperarid fuel-continuity fragmentation.
2. Drying/curing phase:
   - Fire spread is amplified when Dbar is increasing, rainfall is below normal for the month, and temperatures are warm enough for curing/ignition.
   - This targets the AUST seasonality failure and improves savanna/grass fire regions.
3. Hot/warm wet-month compensation:
   - The curing term can over-amplify warm transition/wet months. A precipitation-concentration wet-month compensation corrects this, but only under warm climatology, avoiding the earlier BONA/BOAS collapse from ungated wet suppression.

Final accepted parameters are in `runs/candidates/p2f3_curing_hotwet_final/params.json`.

Key continuation parameters:
```text
drying_k    = 0.151909755193002
drying_c    = 71.10327035972242
pconc_half  = 0.17733668059544083
pconc_pow   = 3.6607083389419017
temp_k      = 0.5483001798421393
temp_c      = 6.554353498957058
cure_amp    = 1.5049730144952744
wet_k_month = 1.9603357957179453
wet_c_month = 0.6295980601621034
wet_amp_month = 0.65
warm_k      = 0.5
warm_c      = 8
warm_floor  = 0.0
```

## Official global ILAMB comparison

| Model | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ED-next-curing-warmwet-nowarmgate | 0.688603 | 0.744397 | 0.520711 | 0.858030 | 0.799164 | 0.453583 |
| ED-next-curing-hotwet-1 | 0.687626 | 0.744018 | 0.518584 | 0.857581 | 0.799362 | 0.471262 |
| ED-next-curing-scale-1p25 | 0.684994 | 0.740401 | 0.515725 | 0.854069 | 0.799049 | 0.526501 |
| ED-next-curing | 0.684534 | 0.740517 | 0.515532 | 0.853681 | 0.797406 | 0.515936 |
| ED-next-curing-scale-0p35 | 0.680952 | 0.739764 | 0.514287 | 0.850744 | 0.785677 | 0.485181 |
| ED-p2f3-seed2 | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.466368 |
| ED-p2f3-nolow2 | 0.676981 | 0.738300 | 0.512151 | 0.845262 | 0.777043 | 0.478758 |
| ED-next-coldrelax | 0.676930 | 0.739103 | 0.512622 | 0.847835 | 0.772470 | 0.469110 |
| ED-ModelC-final | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.611164 |

Full table: `runs/tables/continued_next_global_scores.md`.

## Public TRENDY/firepipe comparison

Accepted final public result:
- `ED-next-curing-hotwet-1`: 0.687405.
- `ED-p2f3-current-final`: 0.676846.
- `ED-ModelC-pass2-P2F3`: 0.676846.
- `ED-ModelC-baseline-current`: 0.671274.

Rejected top-scalar public result:
- `ED-next-curing-warmwet-nowarmgate`: 0.688384, but rejected due BONA/BOAS regional damage.

Public output paths:
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-warmwet-nowarmgate/scalar_database.csv`

Known caveat: JSBACH again produced the known ILAMB `IndexError`, but score tables completed.

## Regional comparison: accepted final vs P2F3

| Region | P2F3 Overall | Hotwet-1 Overall | Delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| global | 0.677073 | 0.687626 | +0.010553 | Step global gain; Spatial +0.026689 and Seasonal +0.009502 |
| bona | 0.771207 | 0.769133 | -0.002074 | Essentially preserved vs P2F3; avoids wet-suppression collapse |
| tena | 0.414691 | 0.419723 | +0.005032 | Further weak dryland gain |
| ceam | 0.403716 | 0.393815 | -0.009901 | Regresses; still above original Model C |
| nhsa | 0.606292 | 0.584617 | -0.021675 | Regresses |
| shsa | 0.545642 | 0.517434 | -0.028208 | Regresses |
| euro | 0.385437 | 0.404197 | +0.018760 | Clear weak-region gain |
| mide | 0.419018 | 0.392997 | -0.026021 | Regresses; remains above original Model C |
| nhaf | 0.653435 | 0.683038 | +0.029603 | Large gain, mainly spatial |
| shaf | 0.656661 | 0.689496 | +0.032835 | Large gain, mainly spatial |
| boas | 0.728730 | 0.729333 | +0.000603 | Preserved/slight gain |
| ceas | 0.679173 | 0.682268 | +0.003095 | Slight gain |
| seas | 0.511484 | 0.504324 | -0.007160 | Regresses but remains above Model C |
| eqas | 0.629088 | 0.621145 | -0.007943 | Regresses but retains most P2F3 gain |
| aust | 0.667783 | 0.681726 | +0.013943 | Material AUST fix; Seasonal +0.027789 |

Full selected regional table: `runs/tables/continued_next_regional_scores.md`.

## Mechanisms tried in this continuation

### 1. Low-arid warm gate

Goal: reduce BONA spatial damage by attenuating P2F3's low/soft arid threshold outside warm regimes.

Search: 500 Optuna trials.

Outcome: optimum collapsed to near identity (`floor=0.9867`). Rejected before official acceptance; it did not reveal a meaningful mechanism beyond P2F3.

### 2. Cold continental suppression relaxation

Goal: restore some P2F3-suppressed fire in cold, high-temperature-amplitude climates to recover BONA/BOAS spatial patterns.

Search: 500 Optuna trials, official global/regional.

Outcome:
- Official global 0.676930, slightly below P2F3.
- BONA improved vs P2F3 (0.777749 vs 0.771207), BOAS improved (0.730364 vs 0.728730), but global score and broader behavior were insufficient.

Decision: rejected.

### 3. Drying/curing phase enhancement

Goal: address missing seasonal fire behavior, especially AUST, by amplifying burning during active drying and warm, below-normal rainfall months.

Search: 500 Optuna trials plus deterministic amplitude scans.

Outcome:
- `ED-next-curing`: official global 0.684534, BONA/BOAS preserved, AUST improved to 0.678597.
- `ED-next-curing-scale-1p25`: official global 0.684994, but regional tradeoffs grew.

Decision: serious accepted mechanism, but not final alone because it eroded some P2F3 weak-region gains.

### 4. Curing plus warm/hot wet-month compensation

Goal: preserve curing-phase global/AUST/spatial gains while reducing over-amplification in warm wet months. Warm-climate gating was required to avoid BONA/BOAS damage.

Search: 700 Optuna trials plus deterministic hot/warm-gated grid and ablations.

Ablations/diagnostics:
- No wet compensation: lower global and weak wet-region balance.
- No curing enhancement: global collapses to 0.659039 despite improvements in some weak dry regions; curing is essential for the global step.
- No warm gate: highest scalar but BONA/BOAS collapse; warm/hot gating is essential for regional defensibility.
- Hotwet grid identified `ED-next-curing-hotwet-1` as the best balanced compromise.

Decision: accepted as final balanced continuation.

## Why rejected candidates failed

- Wet-temperature family: improved weak regions but caused unacceptable BONA/BOAS spatial collapse.
- Warm-gated wet-temperature: safer but too small globally.
- Annual wet/dry-month standalone families: mechanistically useful but insufficient as standalone changes.
- P2F3 no-low/no-high ablations: showed both thresholds have support; no-low is parsimonious but weaker in target drylands.
- Cold continental relaxation: helped BONA/BOAS but did not beat P2F3 globally.
- Curing without wet compensation: strong global/AUST result but too much erosion of P2F3 weak-region gains.
- Curing with ungated wet compensation: highest global/public score but BONA/BOAS damage, so rejected as scalar overfit.

## Constraint compliance

The final accepted model uses only allowed inputs:
- Dbar,
- P_ann,
- P_month,
- T_air,
- GPP through original Model C.

Derived variables are smooth global transformations of these fields:
- precipitation concentration,
- Dbar tendency,
- annual T_air climatology,
- P2F3 arid deficit ratio.

No candidate used:
- external model inputs,
- latitude/longitude,
- named-region routing,
- per-region formulas,
- per-cell lookup tables,
- arbitrary residual correction coefficients,
- direct GFED cell-identity fitting.

Regional labels were used only for official ILAMB evaluation and post-hoc diagnostics.

## Empirical ceiling and remaining failures

The continuation did find a real step beyond P2F3 in global/public scoring and in several regional behaviors. However, it did not find a model that dominates P2F3 in every region.

Remaining unresolved failures:
- CEAM/MIDE/TENA/EURO spatial scores remain low, even when Overall improves. This points to missing land-use, cropland, management/suppression, ignition, fragmentation, and local fuel-type inputs.
- South American regions regress under curing enhancement, suggesting that monthly P/T/Dbar/GPP cannot reliably separate productive fire-season drying from over-broad warm-season amplification there.
- BONA still remains below original Model C, though the accepted final preserves BONA near P2F3 and avoids the large wet-suppression collapse. Full BONA recovery likely requires snow, lightning, boreal fuel structure, or ignition timing information absent from the contract.
- AUST is materially improved by curing, but not fully solved; remaining seasonal limitations likely need vegetation-specific curing, management, submonthly rainfall, or ignition timing.

Final judgement:
- `ED-next-curing-hotwet-1` is the best global/public and best balanced continuation model found.
- P2F3 remains the best regional-broad alternate if preserving the full set of weak-region gains is prioritized over the global/public step.
- Further gains under the fixed input contract appear constrained by tradeoffs between curing-driven global/spatial/AUST gains and climate-only inability to distinguish land-use/human/fuel-type regional patterns. Additional smooth mechanisms were explored enough to make `ED-next-curing-hotwet-1` a defensible stopping point, while explicitly preserving P2F3 as a regional-broad alternate.

## Reproducibility artifacts

Accepted final:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- Source diagnostic candidate: `runs/candidates/next_curing_hotwet_grid_1/`

Previous best/regional alternate:
- `runs/candidates/p2f3_seed_current/params.json`
- `runs/candidates/p2f3_seed_current/burntArea.nc`

Scripts:
- `scripts/search_p2f3_continued.py`
- `scripts/search_p2f3_next.py`
- `scripts/search_p2f3_curing_refine.py`

Official ILAMB outputs:
- P2F3 global: `ilamb/output_candidates_p2f3_corrected_global/scalar_database.csv`
- P2F3 regional: `ilamb/output_regions_ED-p2f3-seed2/scalar_database.csv`
- New global candidates: `ilamb/output_candidates_next_global/scalar_database.csv`
- Curing warmwet global: `ilamb/output_candidates_curing_warmwet_global/scalar_database.csv`
- Curing scale global: `ilamb/output_candidates_curing_scale_global/scalar_database.csv`
- Hotwet global: `ilamb/output_candidates_curing_hotwet_global/scalar_database.csv`
- Final accepted regional: `ilamb/output_regions_ED-next-curing-hotwet-1/scalar_database.csv`
- Rejected top-scalar regional: `ilamb/output_regions_ED-next-curing-warmwet-nowarmgate/scalar_database.csv`

Public TRENDY/firepipe:
- Accepted final: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`
- Rejected top-scalar: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-warmwet-nowarmgate/scalar_database.csv`

Tables:
- `runs/tables/continued_next_global_scores.md`
- `runs/tables/continued_next_regional_scores.md`
- `runs/tables/public_ED-next-curing-hotwet-1_top.md`
- `runs/tables/public_ED-next-curing-warmwet-nowarmgate_top.md`

Updated logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`
