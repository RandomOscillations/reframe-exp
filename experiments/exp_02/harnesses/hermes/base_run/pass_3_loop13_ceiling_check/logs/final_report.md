# Final Report — Continued ED Fire Model Improvement After ED-next-curing-hotwet-1

## Executive summary

I continued from `ED-next-curing-hotwet-1` as the current best-so-far, not as an endpoint. The new continuation tested whether a unified, mechanistic, interpretable formula could produce a further step-function improvement in both global/public score and regional behavior.

Conclusion: no new balanced replacement was found. `ED-next-curing-hotwet-1` remains the best balanced model. New loop 13 candidates raised official/public global scores to about 0.690, but the additional scalar gain consistently came with renewed BONA/BOAS degradation and/or loss of AUST/wet-region balance. These candidates are useful diagnostics of the empirical ceiling, but they are not acceptable final replacements.

Best balanced model retained:
- Model: `ED-next-curing-hotwet-1`
- Artifact: `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- Official global ILAMB Overall: 0.687626
- Public TRENDY/firepipe Overall: 0.687405

Highest scalar/public candidate found in loop 13, rejected:
- Model: `ED-loop13-combined`
- Artifact: `runs/candidates/loop13_combined_protect_attenuate_opt300/burntArea.nc`
- Official global ILAMB Overall: 0.690564
- Public TRENDY/firepipe Overall: 0.690353
- Rejection reason: BONA 0.703762 and BOAS 0.701550, far below hotwet-1 BONA/BOAS 0.769133/0.729333. The scalar gain is not regionally defensible.

Best partial dryland/global diagnostic, rejected:
- `ED-loop13-aridatt`: official 0.690378, public 0.690170.
- It improves TENA/EURO/MIDE but collapses BONA/BOAS to 0.695631/0.693656.

Best partial boreal-protected scalar diagnostic, rejected:
- `ED-loop13-aridboreal-5`: official 0.690073, public 0.689864.
- It partly restores BONA/BOAS vs aridatt but remains below hotwet-1 in BONA/BOAS/AUST and worsens CEAM/SEAS/EQAS.

Therefore, the answer to the continuation objective is: a further scalar step over ED-next-curing-hotwet-1 exists, but a further defensible step in both global and regional behavior was not found under the fixed input contract. ED-next-curing-hotwet-1 remains the accepted final balanced model; loop 13 scalar leaders are rejected.

## Starting point: ED-next-curing-hotwet-1

Formula retained from the previous pass:
```text
base_rate = original Model C annual rate after fire_exp

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)
deficit_ratio = Dbar / (P_ann + ratio_p0)
arid_soft   = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)
P2F3_rate = base_rate * wet_suppress * arid_soft * arid_desert

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

This model was retained because it gives a large public/global improvement over P2F3 while preserving BONA/BOAS near P2F3 and improving AUST.

## Failure triage before loop 13

`ED-next-curing-hotwet-1` vs P2F3:
- Global +0.010553.
- BONA -0.002074, BOAS +0.000603: preserved near P2F3.
- AUST +0.013943: material improvement.
- TENA +0.005032 and EURO +0.018760: further weak-region gains.
- Regressions: CEAM -0.009901, NHSA -0.021675, SHSA -0.028208, MIDE -0.026021, SEAS -0.007160, EQAS -0.007943.

The remaining physical question was whether a global formula could retain hotwet's global/AUST/Africa gains while recovering P2F3-like MIDE/CEAM/SEAS/EQAS and original Model C-like BONA behavior.

## Loop 13 mechanisms tried

### 1. Boreal-protected wet-month compensation

Hypothesis: high-scalar wet compensation fails because it suppresses cold/boreal wet months. A cold/high-temperature-amplitude gate derived only from T_air climatology might protect BONA/BOAS without region routing.

Formula addition:
```text
cold = 1 - sigmoid(T_air_annual_climatology, cold_k, cold_c)
continental = sigmoid(T_air_amplitude, amp_k, amp_c)
protect = protect_amp * cold * continental
wet_eff = wetmonth * warm_gate * (1 - protect)
```

Search: 500 Optuna trials plus deterministic diagnostics.

Result:
- `ED-loop13-borealprotect`: official 0.688726, but BONA 0.699840 and BOAS 0.698280.
- `ED-loop13-borealdiag`: official 0.688133, BONA 0.751941, BOAS 0.729618.

Decision: rejected. Protection partially helps but either still damages BONA or gives only a tiny scalar gain over hotwet-1.

### 2. Arid-deficit curing attenuation

Hypothesis: MIDE and some dryland regressions come from over-broad curing enhancement in high arid-deficit cells. Attenuating curing at high `Dbar/(P_ann+p0)` should restore dryland spatial behavior.

Formula addition:
```text
arid = sigmoid(Dbar/(P_ann+p0), arid_k, arid_c)
curing_eff = curing * (1 - arid_att * arid)
```

Search: 500 Optuna trials.

Result:
- `ED-loop13-aridatt`: official 0.690378; public 0.690170.
- TENA 0.443947, EURO 0.435917, MIDE 0.417546: dryland gains over hotwet-1.
- BONA 0.695631, BOAS 0.693656, AUST 0.677449: unacceptable regressions.

Decision: rejected. It demonstrates a real dryland/global scalar signal but violates the BONA/BOAS preservation criterion.

### 3. Wet/productive curing attenuation

Hypothesis: South America and wet tropics regress because curing is over-amplified in productive wet regimes. Attenuate curing using P_ann and GPP-derived gates.

Search: 500 Optuna trials.

Result:
- `ED-loop13-wetprodatt`: official 0.688892.
- EQAS modestly improves vs hotwet-1 (0.624751 vs 0.621145), but BONA/BOAS are damaged (0.705924/0.703660), and broader regional recovery is inadequate.

Decision: rejected.

### 4. Combined protection/attenuation

Hypothesis: combine boreal protection, arid attenuation, and wet-climate attenuation to retain scalar gains while controlling regional damage.

Search: 300 Optuna trials after the combined all-family run timed out; plus deterministic arid+boreal grids.

Result:
- `ED-loop13-combined`: official 0.690564; public 0.690353, highest found.
- It improves TENA, EURO, MIDE, NHAF, SHAF and global components.
- But BONA 0.703762 and BOAS 0.701550 are unacceptable.

Deterministic arid+boreal grid:
- `ED-loop13-aridboreal-5`: official 0.690073; public 0.689864.
- BONA/BOAS partially recover to 0.729587/0.720784, but remain below hotwet-1 and AUST/CEAM/SEAS/EQAS worsen.

Decision: rejected. The combined family confirms the tradeoff rather than solving it.

## Official global ILAMB table

Full table: `runs/tables/continued_loop13_global_scores.md`.

| Model | Official Overall | Bias | RMSE | Seasonal | Spatial | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ED-loop13-combined | 0.690564 | 0.745298 | 0.522464 | 0.859230 | 0.803364 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridatt | 0.690378 | 0.745436 | 0.523449 | 0.857251 | 0.802306 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridboreal-5 | 0.690073 | 0.745667 | 0.522883 | 0.856854 | 0.802077 | Rejected: not balanced |
| ED-loop13-wetprodatt | 0.688892 | 0.744718 | 0.521065 | 0.857322 | 0.800290 | Rejected: boreal damage |
| ED-loop13-borealprotect | 0.688726 | 0.744697 | 0.520973 | 0.857421 | 0.799568 | Rejected: boreal damage |
| ED-loop13-borealdiag | 0.688133 | 0.744463 | 0.519621 | 0.857194 | 0.799763 | Rejected: marginal, BONA loss |
| ED-next-curing-hotwet-1 | 0.687626 | 0.744018 | 0.518584 | 0.857581 | 0.799362 | Retained best balanced |
| ED-p2f3-seed2 | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 | Regional-broad alternate |
| ED-ModelC-final | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | Original baseline |

## Public TRENDY/firepipe table

Full table: `runs/tables/public_ED-loop13-combined_top.md`.

| Model | Public Overall | Bias | RMSE | Seasonal | Spatial |
| --- | ---: | ---: | ---: | ---: | ---: |
| ED-loop13-combined | 0.690353 | 0.745298 | 0.522464 | 0.859230 | 0.802308 |
| ED-loop13-aridatt | 0.690170 | 0.745436 | 0.523449 | 0.857251 | 0.801261 |
| ED-loop13-aridboreal-5 | 0.689864 | 0.745667 | 0.522883 | 0.856854 | 0.801031 |
| ED-next-curing-warmwet-nowarmgate | 0.688384 | 0.744397 | 0.520711 | 0.858030 | 0.798069 |
| ED-next-curing-hotwet-1 | 0.687405 | 0.744018 | 0.518584 | 0.857581 | 0.798259 |
| ED-p2f3-current-final | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 |
| ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 |
| ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 |

Known caveat: JSBACH again produced the known ILAMB `IndexError`, but candidate score tables completed.

## Regional comparison of serious candidates

Hotwet-1 reference:
- BONA 0.769133
- BOAS 0.729333
- AUST 0.681726
- CEAM 0.393815
- MIDE 0.392997
- SEAS 0.504324
- EQAS 0.621145

Loop 13:
- `ED-loop13-combined`: BONA 0.703762, BOAS 0.701550, AUST 0.681661, CEAM 0.392152, MIDE 0.411305, SEAS 0.503258, EQAS 0.617358.
- `ED-loop13-aridatt`: BONA 0.695631, BOAS 0.693656, AUST 0.677449, CEAM 0.391989, MIDE 0.417546, SEAS 0.503162, EQAS 0.614031.
- `ED-loop13-aridboreal-5`: BONA 0.729587, BOAS 0.720784, AUST 0.677449, CEAM 0.391989, MIDE 0.417530, SEAS 0.503162, EQAS 0.614031.
- `ED-loop13-borealdiag`: BONA 0.751941, BOAS 0.729618, AUST 0.682525, MIDE 0.394218.

Full regional table: `runs/tables/continued_loop13_regional_scores.md`.

Regional judgement:
- Loop 13 improves MIDE/TENA/EURO in the arid attenuation family, but BONA/BOAS and AUST/wet-region behavior degrade.
- Boreal protection partially mitigates but does not solve the BONA/BOAS loss while preserving scalar gains.
- No loop 13 candidate beats hotwet-1 in both global and regional behavior.

## Constraint compliance

All loop 13 candidates used only allowed inputs and smooth transformations:
- Dbar and Dbar tendency.
- P_ann.
- P_month and precipitation concentration.
- T_air, T_air annual climatology, and T_air amplitude.
- GPP for wet/productive attenuation.

No candidate used:
- external model inputs,
- latitude/longitude,
- named-region routing,
- per-region formulas,
- per-cell lookup tables,
- arbitrary residual correction coefficients,
- direct GFED cell-identity fitting.

Regional labels were used only for official evaluation and diagnostics.

## Empirical ceiling assessment

The loop 13 continuation is informative because it found a repeatable scalar direction beyond hotwet-1:
- Arid-deficit curing attenuation and broader wet compensation improve global Bias/RMSE/Spatial and dryland weak regions such as TENA/EURO/MIDE.
- The public benchmark reaches 0.690353 for `ED-loop13-combined`.

But the same direction repeatedly damages BONA/BOAS. Deterministic boreal-protection gates using allowed T_air climatology partially repair the damage but do not restore hotwet-1 regional behavior while keeping the scalar gain. Wet/productive attenuation similarly fails to recover South American/wet-region tradeoffs without boreal damage.

This suggests the current fixed input contract is hitting a tradeoff surface:
- To improve MIDE/TENA/EURO and scalar Spatial/RMSE, the formula suppresses or redistributes too much boreal fire.
- To preserve BONA/BOAS and AUST, the formula must use the more conservative hotwet-1 gating, leaving some MIDE/CEAM/SEAS/EQAS failures unresolved.

Likely missing inputs for further clean improvement:
- boreal lightning/snow/fuel structure and ignition timing,
- land-use/cropland/suppression/management and human ignition,
- fuel type and fragmentation independent of climate/GPP,
- submonthly rainfall/wind/fire-weather extremes,
- vegetation-specific curing and fuel residence times.

## Final decision

Accepted final balanced model remains:
- `ED-next-curing-hotwet-1`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- official global 0.687626
- public 0.687405

Highest scalar/public model found but rejected:
- `ED-loop13-combined`
- `runs/candidates/loop13_combined_protect_attenuate_opt300/burntArea.nc`
- official global 0.690564
- public 0.690353
- rejected because BONA/BOAS collapse.

Regional-broad alternate remains:
- `ED-p2f3-seed2`
- `runs/candidates/p2f3_seed_current/burntArea.nc`
- official global 0.677073
- public 0.676846
- better for the broadest P2F3 weak-region set, but lower global/public than hotwet-1.

## Reproducibility artifacts

Final balanced model:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`
- official regional: `ilamb/output_regions_ED-next-curing-hotwet-1/scalar_database.csv`
- public: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-next-curing-hotwet-1/scalar_database.csv`

Loop 13 scripts/artifacts:
- `scripts/search_hotwet_next.py`
- `runs/candidates/loop13_boreal_protected_wetcomp_opt500/`
- `runs/candidates/loop13_arid_curing_attenuation_opt500/`
- `runs/candidates/loop13_wet_productivity_curing_attenuation_opt500/`
- `runs/candidates/loop13_combined_protect_attenuate_opt300/`
- `runs/candidates/loop13_arid_boreal_grid_*/`

Loop 13 official outputs:
- `ilamb/output_candidates_loop13_global/scalar_database.csv`
- `ilamb/output_candidates_loop13_aridboreal_global/scalar_database.csv`
- `ilamb/output_regions_ED-loop13-combined/scalar_database.csv`
- `ilamb/output_regions_ED-loop13-aridatt/scalar_database.csv`
- `ilamb/output_regions_ED-loop13-aridboreal-5/scalar_database.csv`
- `ilamb/output_regions_ED-loop13-borealdiag/scalar_database.csv`

Loop 13 public outputs:
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-loop13-combined/scalar_database.csv`
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-loop13-aridatt/scalar_database.csv`
- `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-loop13-aridboreal-5/scalar_database.csv`

Tables:
- `runs/tables/continued_loop13_global_scores.md`
- `runs/tables/continued_loop13_regional_scores.md`
- `runs/tables/public_ED-loop13-combined_top.md`
- `runs/tables/public_ED-loop13-aridatt_top.md`
- `runs/tables/public_ED-loop13-aridboreal-5_top.md`
- earlier continuation tables: `runs/tables/continued_next_global_scores.md`, `runs/tables/continued_next_regional_scores.md`

Updated logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`
