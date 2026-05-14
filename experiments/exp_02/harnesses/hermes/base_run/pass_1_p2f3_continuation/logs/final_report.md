# Final Report — Continued ED Fire Model Improvement

## Executive summary

The previous `final_report.md` was premature. I treated it as an interim checkpoint and continued the autoresearch loop from its evidence.

The continuation found a materially better unified formula: `ED-p2f3-seed2`, stored as `runs/candidates/p2f3_seed_current/`. It improves official global ILAMB Overall from 0.671529 to 0.677073 (+0.005544), ranks at the top of the public TRENDY/firepipe table, and improves most weak regions without repeating the BONA/BOAS spatial collapse caused by the earlier wet-temperature candidate.

Accepted final model: P2F3 wet-canopy + two-threshold arid fuel-continuity limiter.

Formula summary:
```text
base_rate = original Model C annual rate after fire_exp

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)

deficit_ratio = Dbar / (P_ann + ratio_p0)
arid_soft   = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)

fire_rate = base_rate * wet_suppress * arid_soft * arid_desert
burntArea_month = (1 - exp(-min(fire_rate, FIRE_MAX_RATE))) / 12
```

Final accepted parameters:
```text
wet_amp    = 0.8844066447148519
wet_k      = 0.03746225268483959
wet_c      = 1733.7962048788854
ratio_p0   = 10.550923117584711
arid_amp1  = 0.09765875631019073
arid_k1    = 8.862392037192233
arid_c1    = 0.8190773026156323
arid_amp2  = 0.872802820380493
arid_k2    = 1.2991349033470558
arid_c2    = 5.00184048998816
```

Decision:
- Accept `ED-p2f3-seed2` / `p2f3_seed_current` as the best model found in this continued run.
- `ED-p2f3-nolow2` is a credible parsimonious alternate: slightly lower global Overall (0.676981 vs 0.677073) but better global Spatial and BONA/AUST preservation. I retain full P2F3 because the low arid threshold is mechanistic and improves target dryland weak regions.
- Remaining unresolved failures are BONA spatial tradeoff and AUST seasonality, likely requiring unavailable inputs such as boreal ignition/snow/lightning, vegetation-specific curing, human fire management, cropland/land-use, fuel type, or submonthly timing.

## Baseline reproduction and context

Before any changes, I read:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

Baseline verification:
```bash
.venv/bin/python scripts/verify.py
```
Result: PASS.

Original Model C official global ILAMB:
```text
Overall 0.671529
Bias    0.728089
RMSE    0.505759
Seasonal 0.845690
Spatial 0.772351
```

Baseline regional triage identified weak regions TENA, CEAM, EURO, MIDE, SEAS, and EQAS. The first continuation signal was that naive wet-temperature suppression improved many weak regions but severely damaged BONA/BOAS spatial structure, so preserving BONA/BOAS became an explicit design constraint.

## Mechanisms tried in the full run

### 1. Original Model C re-optimization
- Same 12-parameter formula.
- 500 Optuna trials in this run.
- Warm-start remained best in proxy scorer.
- Rejected: no evidence of remaining parameter-only slack.

### 2. Lagged/cured fuel memory
- GPP hump used current/3-6 month lagged GPP mixture.
- 500 Optuna trials plus deterministic checks.
- Best collapsed to zero lag.
- Rejected and pruned.

### 3. Dry-shifted GPP saturation
- GPP hump high-productivity decay scale increased under a smooth dbar dryness gate.
- 500 Optuna trials plus grid.
- Best collapsed to zero dry boost.
- Rejected and pruned.

### 4. Rain-pulse suppression
- Multiplied Model C by `exp(-pulse_a * max(p_month/(p_ann/12)-pulse_c,0))`.
- 500 Optuna trials plus grid.
- Official global 0.671705; balanced but negligible.
- Rejected as too small.

### 5. Naive wet-temperature interaction
- Wet months raised effective ignition temperature threshold.
- 500 Optuna trials plus grid.
- Official global 0.674491, but BONA and BOAS spatial collapsed.
- Rejected despite early global improvement.

### 6. Liquid/warm-gated wet-temperature variants
- Tried liquid-rain wetness proxy and annual thermal gate to avoid suppressing boreal/snow precipitation.
- Deterministic grids and official candidates.
- `ED-warm-gate-c8` preserved BONA/BOAS much better and reached 0.672605, but not material.
- Rejected.

### 7. Annual wet-canopy, dry-month, annual precipitation hump, low-amplitude climate suppressors
- Distinct formulations based on persistent wetness and precipitation seasonality.
- Deterministic grids; official `ED-drymonth-norm` and `ED-ann-wet`.
- Annual wet suppression revealed strong EQAS/SEAS signal but did not improve global alone.
- Rejected standalone.

### 8. Warm-gated wet + annual wet hybrid
- Combined weak-region gains from warm-gated wet ignition and annual wet-canopy suppression.
- Official `ED-combo-warm-ann` global 0.672911.
- Rejected as balanced but still too small.

### 9. Wet-canopy + two-threshold arid fuel-continuity limiter (P2F3)
- Physical hypothesis: remaining failures require persistent wet-canopy inhibition plus arid/hyperarid fuel-network fragmentation, not monthly wet-temperature suppression.
- Search: `scripts/search_p2f3_continued.py`, 600 Optuna trials in the current workspace, seeded with the P2F3 mechanism and ablations.
- Official global/regional and public TRENDY/firepipe completed.
- Accepted.

## Search setup and trial counts

Optuna/search counts in this run:
- C reopt: 500 trials.
- lagged fuel: 500 trials.
- dry-shifted GPP: 500 trials.
- rain-pulse suppression: 500 trials.
- wet-temperature interaction: 500 trials.
- dry-shifted GPP rerun after implementation fix: 500 trials.
- P2F3 continued search: 600 trials.
- Additional deterministic grids: liquid/warm-gated wet ignition, annual wet suppression, dry-month concentration, annual precipitation hump, low-amplitude climate suppression, warm+annual hybrid, P2F3 ablations.

Proxy metrics were used only for inner-loop screening. Serious candidates were judged by official global ILAMB, official regional ILAMB, and public TRENDY/firepipe when serious.

## Official global ILAMB table

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

P2F3 is the first candidate in this run to produce a meaningful global step beyond the 0.671-0.674 diagnostic range.

## Official regional ILAMB: baseline vs accepted P2F3

| Region | Baseline Overall | P2F3 Overall | Delta | Notes |
| --- | ---: | ---: | ---: | --- |
| global | 0.671529 | 0.677073 | +0.005544 | Material global gain |
| bona | 0.789806 | 0.771207 | -0.018599 | Tradeoff, but no wet-temp collapse |
| tena | 0.381473 | 0.414691 | +0.033218 | Major weak dryland gain |
| ceam | 0.376153 | 0.403716 | +0.027563 | Major gain |
| nhsa | 0.605824 | 0.606292 | +0.000468 | Preserved/slight gain |
| shsa | 0.507249 | 0.545642 | +0.038393 | Major gain |
| euro | 0.361128 | 0.385437 | +0.024309 | Gain |
| mide | 0.382769 | 0.419018 | +0.036249 | Major gain |
| nhaf | 0.645855 | 0.653435 | +0.007580 | Gain |
| shaf | 0.646693 | 0.656661 | +0.009968 | Gain |
| boas | 0.728733 | 0.728730 | -0.000003 | Preserved |
| ceas | 0.670499 | 0.679173 | +0.008674 | Gain |
| seas | 0.487193 | 0.511484 | +0.024291 | Gain |
| eqas | 0.507395 | 0.629088 | +0.121693 | Largest gain |
| aust | 0.670219 | 0.667783 | -0.002436 | Slight loss; seasonal unresolved |

Regional judgement: P2F3 improves most weak regions, preserves BOAS, and turns the earlier BONA/BOAS failure into a modest BONA tradeoff. AUST remains unresolved.

## Public TRENDY/firepipe table

Public command:
```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
MODEL_NAME="ED-p2f3-current-final" \
SRC="$PWD/runs/candidates/p2f3_seed_current/burntArea.nc" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```

Known caveat: JSBACH showed the known ILAMB `IndexError`, but candidate comparisons completed and the score table was produced.

Top rows:

| Model | Overall Score | Bias Score | RMSE Score | Seasonal Cycle Score | Spatial Distribution Score | Period Mean (original grids) |
| --- | --- | --- | --- | --- | --- | --- |
| ED-p2f3-current-final | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| ED-wet-temp-grid | 0.674241 | 0.731839 | 0.513465 | 0.845167 | 0.767269 | 0.514447 |
| ED-ModelC-formal-candidate | 0.673022 | 0.731755 | 0.508111 | 0.851062 | 0.766069 | 0.547347 |
| ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |

The duplicate `ED-ModelC-pass2-P2F3` row is an existing benchmark-root model with identical output/scores; the unambiguous artifact generated in this workspace is `ED-p2f3-current-final` from `runs/candidates/p2f3_seed_current/burntArea.nc`.

## Ablation and complexity pruning

| Candidate | Official global Overall | Interpretation |
| --- | ---: | --- |
| P2F3 full | 0.677073 | Accepted final; best global and broad regional gains |
| P2F3 no low/soft arid threshold | 0.676981 | Near-tie and more spatially conservative; weaker target dryland gains |
| P2F3 no high/desert threshold | 0.676040 | High threshold important for best global and MIDE/TENA behavior |
| P2F3 Optuna 600 refinement | 0.676764 | Proxy-optimal but official below seed; rejected |

Complexity decision:
- Retain annual wet-canopy suppressor: standalone signal was strong for EQAS/SEAS and full P2F3 needs it.
- Retain high arid threshold: ablation lowers global and dryland performance.
- Retain low arid threshold: small global increment over no-low but interpretable as early fuel-network redundancy loss and helps dryland targets. If parsimony or spatial preservation were the sole criterion, no-low is an alternate.

## Mechanistic interpretation

The final model replaces the rejected monthly wet-temperature idea with slower, more structural controls:

1. Persistent wet-canopy inhibition:
   - High annual precipitation implies closed, humid, wet-canopy/fire-resistant regimes.
   - This addresses EQAS/SEAS and other wet-region overprediction without using region labels.

2. Arid fuel-continuity/percolation limiter:
   - `Dbar/(P_ann + p0)` represents dryness pressure relative to fuel-supplying rainfall.
   - A low/soft threshold represents early loss of redundant connected fine-fuel pathways.
   - A high/desert threshold represents near-total fuel discontinuity in hyperarid conditions.

This matches the failure pattern: weak dry/wet regions improve without a BONA/BOAS spatial collapse because the formula is driven by annual wetness and arid fuel continuity rather than blindly suppressing all wet months.

## Constraint compliance

The accepted model uses only allowed inputs:
- Dbar
- P_ann
- P_month indirectly through original Model C
- T_air indirectly through original Model C
- monthly GPP indirectly through original Model C

No candidate formula used:
- external model inputs,
- latitude/longitude terms,
- named-region routing,
- per-region formulas,
- per-cell lookup tables,
- arbitrary residual correction coefficients,
- GFED cell-identity fitting.

Regional labels were used only for official ILAMB scoring and diagnostics.

## Remaining failures and why they appear unresolved

Remaining issues:
- BONA loses Overall 0.0186, driven by spatial degradation, though far less severe than the wet-temperature candidate.
- AUST loses 0.0024 and still has poor seasonal cycle.
- EURO/TENA/MIDE/CEAM spatial scores remain low despite overall gains.

Likely missing inputs under current contract:
- boreal lightning/snow/fuel structure and ignition timing,
- Australian vegetation-specific curing and fire management,
- cropland and human ignition/suppression,
- land-use fragmentation and fuel continuity independent of climate/GPP,
- peat/soil organic fire regimes,
- submonthly precipitation and wind extremes.

Further gains from smooth transformations of P/T/GPP/Dbar appear possible only at the margin or through regional tradeoffs. The accepted P2F3 is therefore a defensible stopping point: it gives a real global step, broad weak-region gains, official global/regional/public evidence, and ablation support while obeying the fixed input contract.

## Reproducibility artifacts

Core accepted candidate:
- `runs/candidates/p2f3_seed_current/params.json`
- `runs/candidates/p2f3_seed_current/burntArea.nc`
- `scripts/search_p2f3_continued.py`

Official ILAMB outputs:
- Baseline global: `ilamb/output_modelC/scalar_database.csv`
- Baseline regional: `ilamb/output_regions_official/scalar_database.csv`
- Continued global table: `ilamb/output_candidates_p2f3_corrected_global/scalar_database.csv`
- Accepted P2F3 regional: `ilamb/output_regions_ED-p2f3-seed2/scalar_database.csv`
- No-low ablation regional: `ilamb/output_regions_ED-p2f3-nolow2/scalar_database.csv`
- No-high ablation regional: `ilamb/output_regions_ED-p2f3-nohigh2/scalar_database.csv`

Public TRENDY/firepipe:
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-p2f3-current-final/scalar_database.csv`

Logs updated:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`

Final state note:
- I preserved original baseline `models/C/params.json` and `ilamb/MODELS/ED-ModelC-final/burntArea.nc` for hash-stable comparison.
- The accepted final candidate is isolated under `runs/candidates/p2f3_seed_current/` and evaluated as `ED-p2f3-seed2` / `ED-p2f3-current-final`.
