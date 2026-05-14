# Final Report — ED Fire Model Improvement Run

## Executive summary

This run started from original Model C and pushed several constrained, mechanistic formula families to a defensible stopping point under the fixed input contract.

Best accepted model: F3b, a pruned global wet/arid limiter on top of original Model C.

Final official global ILAMB:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| Baseline Model C | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| Final F3b | 0.738225 | 0.511898 | 0.844302 | 0.776393 | 0.676543 |
| Delta | +0.010136 | +0.006139 | -0.001388 | +0.004042 | +0.005014 |

Public TRENDY/firepipe:
- Final candidate `ED-ModelC-formal-candidate`: Overall 0.676313, rank #1 in the produced public score table.
- Baseline current in the same public table: Overall 0.671274.
- Caveat: JSBACH produced the known ILAMB IndexError during pair execution, but the benchmark completed and produced a score table.

Scientific conclusion:
- The strongest defensible improvement is not a wholesale retune of Model C, but adding two global, interpretable missing limiters:
  1. high-annual-precipitation wet/canopy-moisture inhibition;
  2. hyperarid fuel-discontinuity inhibition using `Dbar / (P_ann + ratio_p0)`.
- These terms reduce Model C's systematic overprediction in several weak regions while mostly preserving its strong seasonal phase.
- Remaining failures are mostly spatial/regional and plausibly require inputs unavailable under the contract: land use, cropland/fragmentation, human suppression/ignition, lightning, vegetation/fuel type, and subgrid fuel continuity.

## Baseline reproduction and benchmark context

Required files read before code changes:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

Baseline verification:
- Command: `.venv/bin/python scripts/verify.py`
- Result: PASS, 24/24 files present, 24/24 hashes OK.

Official baseline global ILAMB:
- Output: `ilamb/output_modelC`
- Overall: 0.671529.

Official baseline regional ILAMB:
- Output: `ilamb/output_regions_official`
- Weak regions: EURO, CEAM, TENA, MIDE, SEAS, SHSA, EQAS.
- Failure mode: mostly overprediction and poor spatial distribution, not seasonal phase.

Public benchmark context:
- Final public run output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-formal-candidate`
- Final candidate ranked #1 in that produced table.

## Final accepted model

Final model ID: F3b.

Formula:

```
base_fire = original Model C

deficit_ratio = Dbar / (P_ann + ratio_p0)

wet_suppress  = 1 - wet_amp  * sigmoid(P_ann,        wet_k,  wet_c)
arid_suppress = 1 - arid_amp * sigmoid(deficit_ratio, arid_k, arid_c)

fire_rate_yr = base_fire * wet_suppress * arid_suppress
burntArea_month = (1 - exp(-min(fire_rate_yr, FIRE_MAX_RATE))) / 12
```

Final parameters:

```
wet_amp   = 0.8844066447148519
wet_k     = 0.03746225268483959
wet_c     = 1733.7962048788854
ratio_p0  = 76.48116496519896
arid_amp  = 0.7463784815617368
arid_k    = 1.8318106083501675
arid_c    = 4.018565692385908
cool_amp  = 0.0
```

Mechanistic explanation:
- Wet suppressor: annual precipitation is both a fuel-supply proxy and, at high values, a persistent-moisture/canopy-curing inhibitor. This converts Model C's annual precipitation floor into a more realistic combustion window without adding external data.
- Arid suppressor: high dryness alone is insufficient where rainfall/fuel continuity is too low. The ratio `Dbar / (P_ann + ratio_p0)` acts as a global proxy for hyperarid fuel discontinuity.
- Structural analogy: fire spread resembles percolation or epidemic spread. Ignition and dryness matter only if a connected susceptible/fuel network exists. It also resembles a chemical reactor where substrate supply helps at first but excess moisture inhibits the reaction.

## Highest global-score model

Highest official global score found: F3a full suppressor family, Overall 0.676544.

However, F3a included a cool suppressor whose ablation changed official global Overall only from 0.676544 to 0.676543. Because the cool term added complexity without material support, the final accepted model is F3b, the pruned wet+arid form.

## Best regional model

F3b is also the best regional compromise found. It improves most weak regions materially, especially EQAS, SHSA, CEAM, MIDE, TENA, SEAS, and EURO. It slightly worsens already-good BONA and small losses in NHSA/BOAS, mainly via spatial score tradeoffs.

## Baseline vs final global ILAMB table

| Metric | Baseline C0 | Final F3b | Delta |
|---|---:|---:|---:|
| Bias Score | 0.728089 | 0.738225 | +0.010136 |
| RMSE Score | 0.505759 | 0.511898 | +0.006139 |
| Seasonal Cycle Score | 0.845690 | 0.844302 | -0.001388 |
| Spatial Distribution Score | 0.772351 | 0.776393 | +0.004042 |
| Overall Score | 0.671529 | 0.676543 | +0.005014 |

Final verification after updating `scripts/reproduce_modelC.py`:
- Command: `OUT="$PWD/ilamb/output_final_current_global" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh`
- Result: Overall 0.6765, matching F3b.

## Baseline vs serious candidates regional ILAMB table

| Region | Baseline Overall | F3b Overall | Delta |
|---|---:|---:|---:|
| global | 0.671529 | 0.676543 | +0.005014 |
| bona | 0.789806 | 0.777787 | -0.012019 |
| tena | 0.381473 | 0.406672 | +0.025199 |
| ceam | 0.376153 | 0.403003 | +0.026850 |
| nhsa | 0.605824 | 0.602484 | -0.003340 |
| shsa | 0.507249 | 0.543078 | +0.035829 |
| euro | 0.361128 | 0.376821 | +0.015693 |
| mide | 0.382769 | 0.408459 | +0.025690 |
| nhaf | 0.645855 | 0.652601 | +0.006746 |
| shaf | 0.646693 | 0.657096 | +0.010403 |
| boas | 0.728733 | 0.727964 | -0.000769 |
| ceas | 0.670499 | 0.678107 | +0.007608 |
| seas | 0.487193 | 0.509196 | +0.022003 |
| eqas | 0.507395 | 0.628943 | +0.121548 |
| aust | 0.670219 | 0.670563 | +0.000344 |

Full component table is in `eval_log.md` and official output directory `ilamb/output_F3b_no_cool_regions`.

## Public TRENDY/firepipe ranking table

From final public run:

| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial |
|---:|---|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-formal-candidate | 0.676313 | 0.738225 | 0.511898 | 0.844302 | 0.775242 |
| 2 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 |
| 3 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 |
| 4 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 |
| 5 | ED-ModelC-curing-lag-v1-current | 0.671767 | 0.727997 | 0.505755 | 0.848710 | 0.770616 |
| 8 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 |
| 9 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 |
| 10 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 |

## Mechanisms tried

1. F1 antecedent fuel / wet-dry pulse
   - Prior GPP memory, drying release, current wetness quench.
   - Rejected: 500-trial search ablated back to baseline; GPP memory replacement was slightly worse.

2. F2 annual precipitation combustion window
   - High annual precipitation suppressor inside the precip term.
   - Rejected as standalone: 500-trial best was internally worse than baseline.

3. F3 wet/arid/cool suppressors on fixed Model C core
   - Wet canopy/cold fuel moisture suppressor.
   - Hyperarid fuel-discontinuity suppressor.
   - Cool ignition suppressor.
   - Accepted family: official global Overall improved to 0.676544.

4. F3b pruned wet+arid suppressors
   - Cool term removed by ablation.
   - Accepted final: official global Overall 0.676543 with lower complexity.

5. F4 full 22-parameter retune
   - Model C core plus suppressors all retuned.
   - Rejected: 1000-trial search did not beat baseline-equivalent internal candidate and was less stable/interpretable.

## Optuna/search setup and trial counts

| Candidate | Family | Trials | Objective/evaluation role |
|---|---|---:|---|
| F1a | wet-dry pulse | 500 | Fast ILAMB-aligned internal simple score |
| F1b | GPP memory replacement | 500 | Fast ILAMB-aligned internal simple score |
| F2a | precipitation window | 500 | Fast ILAMB-aligned internal simple score |
| F3a | fixed suppressors | 800 | Fast internal screen, then official global/regional ILAMB |
| F3 ablations | remove wet/arid/cool | deterministic ablations | Official global ILAMB |
| F4a | full retune plus suppressors | 1000 | Fast internal screen; rejected before official because no meaningful improvement |

All substantial searches stayed within the requested 500-2000 trial range.

## Ablation results and complexity pruning

| Model | Overall | Interpretation |
|---|---:|---|
| F3a full wet+arid+cool | 0.676544 | Best raw official global score |
| No wet | 0.6729 | Wet suppressor is important |
| No arid | 0.6753 | Arid suppressor contributes |
| No cool | 0.676543 | Cool term is unnecessary |

Pruning decision:
- Drop cool suppressor because it has negligible official effect and increases complexity.
- Keep wet and arid suppressors because both improve or protect the final score and have clear physical interpretations.

## Constraint compliance

Final F3b uses only:
- original Model C core inputs: Dbar, P_ann, P_month, T_air, monthly GPP;
- transformed allowed inputs: `Dbar / (P_ann + ratio_p0)`.

No use of:
- external model inputs;
- latitude/longitude features;
- named-region routing;
- per-region formulas;
- per-cell lookup tables;
- arbitrary residual correction coefficients;
- direct GFED cell-identity fitting.

Regional labels were used only for post-hoc diagnostics and official ILAMB scoring, not in the formula.

## Remaining regional/fire-regime failures

Remaining weak areas:
- EURO, TENA, MIDE, CEAM still have low spatial scores, although their bias/RMSE/Overall improved.
- AUST seasonal score remains low.
- BONA loses some spatial score, though it remains high overall.
- NHSA/BOAS have slight tradeoffs, likely because P_ann is an imperfect proxy for true wet-forest fire limitation.

Why unresolved under current constraints:
- Many remaining failures likely depend on unavailable drivers: land cover, cropland fraction, grazing, roads/fragmentation, human suppression, lightning/ignition source, vegetation/fuel type, peat, and subgrid fuel continuity.
- The allowed inputs can infer broad climate/productivity regimes, but cannot distinguish human-managed croplands from natural grasslands or fragmented landscapes with the same climate/GPP/P_ann.
- Further smooth global transforms of the same inputs risk score-fitting or damaging regions already improved; the F4 full-retune attempt supports this risk.

## Reproducibility paths and files

Important files changed/created:
- `models/C/params.json`: final F3b suppressor parameters.
- `models/C/params.BASELINE-before-research.json`: original Model C core parameter backup.
- `models/C/formula.md`: final formula documentation.
- `scripts/research_fire_candidates.py`: research search/emit script.
- `scripts/reproduce_modelC.py`: updated to reproduce original Model C-style params or final suppressor schema.
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: current final TRENDY-format output.
- `research_candidates/F3a_fixed_suppressors.json`: accepted full suppressor candidate.
- `research_candidates/F3abl_no_cool.json`: final pruned candidate source.

Evidence directories:
- Baseline global: `ilamb/output_modelC`
- Baseline regional: `ilamb/output_regions_official`
- F3a global: `ilamb/output_F3a_global`
- F3a regional: `ilamb/output_F3a_regions`
- F3b final regional: `ilamb/output_F3b_no_cool_regions`
- Final current global verification: `ilamb/output_final_current_global`
- Public TRENDY/firepipe: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-formal-candidate`

Reproduce final output:

```bash
.venv/bin/python scripts/reproduce_modelC.py
OUT="$PWD/ilamb/output_final_current_global" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh
OUT="$PWD/ilamb/output_F3b_no_cool_regions" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh
```

## Final judgement

Accept F3b as the best defensible model found in this constrained run.

It improves official global ILAMB, improves most weak regional Overalls, ranks #1 in the public TRENDY/firepipe table, has a clear mechanistic story, survives ablation-based pruning, and remains compliant with the fixed input contract. Further exploration of smooth global transforms was attempted and either ablated to baseline or worsened the internal objective; remaining failures appear to require information not present in the allowed inputs.
