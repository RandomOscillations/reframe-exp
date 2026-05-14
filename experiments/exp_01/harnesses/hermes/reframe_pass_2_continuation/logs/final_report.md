# Final Report Pass 2 — ED Fire Model Improvement Continuation

## Executive summary

Pass 2 continued from the completed pass-1 F3b model state, not from original Model C. The scientific question was whether a unified, mechanistic, interpretable burned-area functional form could improve beyond F3b under the fixed input contract.

Best accepted pass-2 model: P2F3, a refinement of F3b that keeps the pass-1 wet/canopy suppressor and replaces F3b's single arid fuel-discontinuity sigmoid with a two-threshold global arid fuel-continuity limiter.

Final official global ILAMB:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| F3b incumbent | 0.738225 | 0.511898 | 0.844302 | 0.776393 | 0.676543 |
| P2F3 final | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.677073 |
| Delta | +0.000441 | +0.001074 | +0.003777 | -0.003720 | +0.000530 |

Public TRENDY/firepipe:
- P2F3 with unique model name `ED-ModelC-pass2-P2F3`: Overall 0.676846, rank #1 in the produced table.
- Known caveat: JSBACH showed the known ILAMB IndexError, but the benchmark completed and produced a score table.

Scientific conclusion:
- A defensible improvement beyond F3b exists, but it is small and tradeoff-bearing.
- The best supported pass-2 mechanism is not more seasonal wet gating; it is a refined arid fuel-continuity/percolation limiter.
- F3b's single arid threshold was too blunt. P2F3 represents gradual fuel-network fragmentation: a weak early semi-arid loss of redundancy plus a strong high-deficit desert cutoff.
- Remaining failures, especially AUST seasonal timing and very low spatial scores in EURO/TENA/MIDE/CEAM, appear unresolved under the current input contract without land use, fuel type, ignition/suppression, lightning, vegetation structure, or submonthly timing information.

## Required context read

Before pass-2 changes, these files were read:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `final_report.md`
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `models/C/formula.md`
- `models/C/params.json`
- `scripts/research_fire_candidates.py`

## Starting point: pass-1 F3b

Pass 1 accepted F3b:

```
base_fire = original Model C

deficit_ratio = Dbar / (P_ann + ratio_p0)

wet_suppress  = 1 - wet_amp  * sigmoid(P_ann,        wet_k,  wet_c)
arid_suppress = 1 - arid_amp * sigmoid(deficit_ratio, arid_k, arid_c)

fire_rate_yr = base_fire * wet_suppress * arid_suppress
burntArea_month = (1 - exp(-min(fire_rate_yr, FIRE_MAX_RATE))) / 12
```

F3b pass-1 evidence:
- Official global Overall 0.676543.
- Public TRENDY/firepipe Overall 0.676313, rank #1.
- Regional gains in many weak regions, especially EQAS, SHSA, CEAM, MIDE, TENA, SEAS, and EURO.
- Remaining issues: low spatial scores in EURO/TENA/MIDE/CEAM, low AUST seasonal score, BONA/NHSA/BOAS tradeoffs.

## Final accepted model: P2F3

Formula:

```
base_fire = original Model C

deficit_ratio = Dbar / (P_ann + ratio_p0)

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)

arid_soft_1  = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert  = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)

fire_rate_yr = base_fire * wet_suppress * arid_soft_1 * arid_desert
burntArea_month = (1 - exp(-min(fire_rate_yr, FIRE_MAX_RATE))) / 12
```

Final parameters:

```
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

Mechanistic explanation:
- The retained wet suppressor represents persistent wet-canopy/fuel-moisture inhibition in high annual precipitation regimes.
- The two arid thresholds represent gradual loss of fuel-network connectivity as dryness overwhelms rainfall/fuel supply.
- The small low-deficit threshold represents early loss of redundancy in semi-arid fuel pathways.
- The strong high-deficit threshold represents desert-like fuel discontinuity.

Structural analogy:
- Fire spread is analogous to packet routing or epidemic spread on a network. The system loses robustness before it fully fragments. A single threshold only captures collapse; two thresholds capture both redundancy loss and final disconnection.

## Highest global-score model

Highest official global score found in pass 2: P2F3 full two-threshold arid limiter, Overall 0.677073.

The pruned no-low-threshold ablation scored 0.676981, only 0.000092 lower and with better global Spatial, but it gave weaker dryland target-region gains. Because the low threshold is physically interpretable and gives the highest official global score while improving TENA/EURO/MIDE, the final accepted pass-2 model keeps it.

## Best regional model

There is no single uniformly best regional model.

- P2F1 curing gate gave broad tiny improvements in many weak regions but worsened BONA and had lower global score than P2F3.
- P2F2 seasonal wet improved global Spatial but worsened key wet weak regions: CEAM, SHSA, SEAS, EQAS.
- P2F3 gives the best dry/subtropical weak-region improvement package and best official global score, but worsens BONA and AUST.
- P2F3 no-low-threshold is a more spatially conservative variant but gives lower global score and weaker target dryland gains.

Final judgement: accept P2F3 as best overall scientific/global/regional compromise from pass 2, while explicitly noting BONA/AUST/spatial tradeoffs.

## Official global ILAMB table

| Candidate | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---:|---:|---:|---:|---:|---|
| F3b incumbent | 0.738225 | 0.511898 | 0.844302 | 0.776393 | 0.676543 | Pass-2 baseline |
| P2F1 curing gate | 0.738469 | 0.512636 | 0.845672 | 0.773679 | 0.676618 | Serious comparison, rejected as final |
| P2F2 seasonal wet | 0.737437 | 0.510878 | 0.846213 | 0.778162 | 0.676714 | Rejected: weak wet-region tradeoffs |
| P2F3 two-threshold arid | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.677073 | Final accepted |
| P2F3 no low threshold | 0.738300 | 0.512151 | 0.845262 | 0.777043 | 0.676981 | Ablation, lower global/target gains |
| P2F3 no high threshold | 0.737042 | 0.510722 | 0.850117 | 0.771599 | 0.676040 | Ablation rejected |

## Regional ILAMB table: F3b vs P2F3

| Region | F3b Overall | P2F3 Overall | Delta | Main interpretation |
|---|---:|---:|---:|---|
| global | 0.676543 | 0.677073 | +0.000530 | Bias/RMSE/seasonal improve; spatial falls |
| bona | 0.777787 | 0.771207 | -0.006580 | Spatial tradeoff in already strong region |
| tena | 0.406672 | 0.414691 | +0.008019 | Dryland amplitude/RMSE improvement |
| ceam | 0.403003 | 0.403716 | +0.000713 | Essentially preserved/slight gain |
| nhsa | 0.602484 | 0.606292 | +0.003808 | Recovers pass-1 tradeoff slightly |
| shsa | 0.543078 | 0.545642 | +0.002564 | Slight improvement |
| euro | 0.376821 | 0.385437 | +0.008616 | Bias/RMSE and slight spatial gain |
| mide | 0.408459 | 0.419018 | +0.010559 | Strong dryland/desert cutoff gain |
| nhaf | 0.652601 | 0.653435 | +0.000834 | Slight gain |
| shaf | 0.657096 | 0.656661 | -0.000435 | Essentially preserved |
| boas | 0.727964 | 0.728730 | +0.000766 | Slight gain |
| ceas | 0.678107 | 0.679173 | +0.001066 | Slight gain |
| seas | 0.509196 | 0.511484 | +0.002288 | Slight gain |
| eqas | 0.628943 | 0.629088 | +0.000145 | Preserved |
| aust | 0.670563 | 0.667783 | -0.002780 | Seasonal failure remains unresolved |

## Public TRENDY/firepipe ranking table

Output directory:
`/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_pass2_P2F3_fresh`

| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 1 | ED-ModelC-formal-candidate | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 3 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| 4 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| 5 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| 9 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| 10 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| 11 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |

Note: `ED-ModelC-formal-candidate` matches P2F3 in this fresh public output because the public helper copied the current pass-2 candidate into that model slot during the attempted public run. The unique `ED-ModelC-pass2-P2F3` row is the unambiguous pass-2 record.

## Mechanisms tried in pass 2

1. Seasonal curing/synchronization gate (P2F1)
   - Missing mechanism: timing alignment among dry state, drying tendency, and rain-free month.
   - Search: 600 Optuna trials.
   - Outcome: small global/weak-region gains but global Spatial and BONA worsened; AUST unresolved.

2. Seasonal wet/canopy inhibition (P2F2)
   - Missing mechanism: wet suppression should depend on current/antecedent rainfall timing.
   - Search: 700 Optuna trials.
   - Outcome: higher global Spatial/Seasonal but worse CEAM/SHSA/SEAS/EQAS; rejected as final.

3. Two-threshold arid fuel-continuity limiter (P2F3)
   - Missing mechanism: dryland fuel networks fragment gradually, not at one threshold.
   - Search: 600 Optuna trials.
   - Outcome: best official global score, public rank #1, improved several weak dry/subtropical regions; accepted.

4. Seasonal wet + two-threshold arid hybrid (P2F4)
   - Missing mechanism: combine timing-aware wetness with refined arid fragmentation.
   - Search: 800 Optuna trials.
   - Outcome: internal score below P2F3/F3b; rejected before official.

## Optuna/search setup and trial counts

| Candidate | Family | Trials | Role |
|---|---|---:|---|
| P2F1 | curing/synchronization gate | 600 | Serious candidate; official global/regional |
| P2F2 | seasonal wet inhibition | 700 | Serious candidate; official global/regional |
| P2F3 | two-threshold arid limiter | 600 | Final accepted; official global/regional/public |
| P2F3 ablations | deterministic | 2 ablations | Complexity pruning |
| P2F4 | seasonal wet + arid hybrid | 800 | Rejected by internal screen |

All Optuna searches stayed within the requested 500-2000 trial range.

## Ablation and complexity pruning

| Ablation | Overall | Interpretation |
|---|---:|---|
| P2F3 full | 0.677073 | Highest official global; accepted |
| P2F3 no low threshold | 0.676981 | Low threshold contributes only +0.000092 global, but improves target dryland regions |
| P2F3 no high threshold | 0.676040 | High-deficit desert cutoff is essential |

Complexity decision:
- Retain high threshold: strongly supported.
- Retain low threshold: small but interpretable and improves official global/target dryland regions. If a stricter parsimony criterion were imposed, the no-low variant would be defensible, but it was not selected because pass 2's goal included improving weak regional fire behavior, not only pruning parameters.
- Reject P2F4 hybrid: too flexible and underperforms.

## Constraint compliance

Final P2F3 uses only:
- original Model C inputs: Dbar, P_ann, P_month, T_air, monthly GPP;
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

Remaining weak or tradeoff areas:
- EURO/TENA/MIDE/CEAM still have very low Spatial Distribution Scores even after P2F3 gains.
- AUST seasonal score remains low and worsens slightly under P2F3.
- BONA loses spatial/overall skill relative to F3b.
- Global Spatial declines vs F3b despite global Bias/RMSE/Seasonal/Overall gains.

Why unresolved under current constraints:
- Many remaining failures likely depend on unavailable drivers: land cover, cropland fraction, grazing, roads/fragmentation, human suppression, lightning/ignition source, vegetation/fuel type, peat, and subgrid fuel continuity.
- AUST timing likely depends on vegetation-specific curing, submonthly rainfall/monsoon timing, ignition patterns, and fire management that cannot be inferred robustly from monthly Dbar/P_ann/P_month/T_air/GPP alone.
- The allowed inputs can infer broad climate/productivity regimes, but cannot distinguish human-managed croplands from natural grasslands or fragmented landscapes with the same climate/GPP/P_ann.
- Further smooth global transforms were tested and either produced weak tradeoffs (P2F1/P2F2) or underperformed internally (P2F4).

## Reproducibility paths and files

Files changed/created in pass 2:
- `scripts/research_fire_pass2.py`: pass-2 search/emit script.
- `scripts/reproduce_modelC.py`: updated to reproduce original C, pass-1 F3b, and pass-2 P2F3 schema.
- `models/C/params.json`: final pass-2 P2F3 parameters.
- `models/C/formula.md`: final pass-2 formula documentation.
- `research_candidates_pass2/P2F1_curing_gate.json`
- `research_candidates_pass2/P2F2_seasonal_wet.json`
- `research_candidates_pass2/P2F3_arid_two_threshold.json`
- `research_candidates_pass2/P2F3abl_no_low_threshold.json`
- `research_candidates_pass2/P2F3abl_no_high_threshold.json`
- `research_candidates_pass2/P2F4_seasonal_wet_arid2.json`
- `research_log_pass2.md`
- `candidate_registry_pass2.md`
- `eval_log_pass2.md`
- `regional_analysis_pass2.md`
- `constraint_checks_pass2.md`

Evidence directories:
- P2F1 global: `ilamb/output_P2F1_curing_gate_global`
- P2F1 regional: `ilamb/output_P2F1_curing_gate_regions`
- P2F2 global: `ilamb/output_P2F2_seasonal_wet_global`
- P2F2 regional: `ilamb/output_P2F2_seasonal_wet_regions`
- P2F3 global: `ilamb/output_P2F3_arid_two_threshold_global`
- P2F3 regional: `ilamb/output_P2F3_arid_two_threshold_regions`
- P2F3 no-low global: `ilamb/output_P2F3abl_no_low_global`
- P2F3 no-low regional: `ilamb/output_P2F3abl_no_low_regions`
- P2F3 no-high global: `ilamb/output_P2F3abl_no_high_global`
- Final current reproduction: `ilamb/output_pass2_final_current_global`
- Public TRENDY/firepipe: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_pass2_P2F3_fresh`

Reproduce final output:

```bash
.venv/bin/python scripts/reproduce_modelC.py
OUT="$PWD/ilamb/output_pass2_final_current_global" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh
OUT="$PWD/ilamb/output_P2F3_arid_two_threshold_regions" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
MODEL_NAME="ED-ModelC-pass2-P2F3" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_pass2_P2F3_fresh" TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh
```

## Final judgement

Accept P2F3 as the best defensible pass-2 model.

It improves official global Overall from 0.676543 to 0.677073, improves Bias/RMSE/Seasonal, improves several weak dry/subtropical regions, ranks #1 in the public TRENDY/firepipe table, has a clear mechanistic story, remains fully constraint-compliant, and survives ablation in the sense that the high-deficit arid threshold is essential while the low threshold provides a small but interpretable target-region gain.

The improvement is modest and not uniformly regional. If strict parsimony were prioritized over every other criterion, the no-low-threshold variant would be a credible alternate. However, P2F3 is the best model found for the stated pass-2 objective: a unified, mechanistic functional form that improves global fit and regional fire behavior under the fixed input contract.
