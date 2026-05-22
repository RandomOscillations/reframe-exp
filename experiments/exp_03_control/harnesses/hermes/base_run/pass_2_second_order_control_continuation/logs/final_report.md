# Final Report: Continued Constrained Model C Fire-Formula Improvement Run

## Executive conclusion

I did not find a defensible replacement for original Model C under the fixed input contract.

Best final model: original Model C (C0), reproduced in this workspace.

Reason: the continuation cycle tested the mechanism families that were missing from the first pass: second-order wet suppression gated by antecedent dryness, wet productive forest/closed-canopy suppression, hyperarid low-fuel limits, cool/uncured ignition interactions, and productivity-shape variants. The strongest continuation candidate, H4 dry-gated wet-month suppression, improved every weak region but collapsed global Spatial Distribution and global Overall. This repeats the same empirical wall seen in H1-H3: under the five allowed inputs, regional overprediction can be reduced only by suppressing cell states that overlap with regimes carrying the original model's global spatial skill.

Final recommendation: retain C0 for global/public benchmark use. H3 remains the least-damaging regional-compromise alternative from the first cycle, but it still loses to C0 globally and publicly. H4 is useful as diagnostic evidence, not as a candidate model.

## Constraints and scope

Workspace boundary:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_03_control/hermes/base`

Read before changes in this run or prior cycle:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `README.md`
- `WRITEUP.md`
- `models/C/formula.md`
- current logs/reports: `research_log.md`, `eval_log.md`, `regional_analysis.md`, `candidate_registry.md`, `constraint_checks.md`, `final_report.md`

Allowed model inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files for scoring only.

No candidate used external model inputs, latitude/longitude hacks, named-region routing, per-region formulas, per-cell lookup tables, direct cell-identity fitting, arbitrary residual correction, or evidence from prior experiment/archive folders.

## Baseline C0

Original Model C formula:

`fire = [ onset(Dbar) * suppress(Dbar) * precip_floor(P_ann) * precip_dampen(P_month) * gpp_hump(GPP_month) * air_temp_ign(T_air) ] ^ fire_exp`

Official global/regional ILAMB for reproduced C0:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| C0 original Model C | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 |

Clean public TRENDY/firepipe benchmark:
- C0 public Overall 0.6713.
- Tied copied `ED-ModelC-baseline` and ranked #1 above CLASSIC 0.6660 and CLM6.0 0.6606.

## Starting failure triage

Official C0 weak regions by Overall:

| Region | Bias | RMSE | Seasonal | Spatial | Overall | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| euro | 0.3934 | 0.2618 | 0.8082 | 0.0805 | 0.3611 | Cool, productive, fragmented low-fire region; likely land-use/human suppression missing. |
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3762 | Humid/tropical mosaic; magnitude and spatial failures. |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3815 | Temperate mosaic; overprediction and spatial placement. |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3828 | Dry/low-fuel/human water-use constraints likely missing. |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4872 | Humid monsoon region. |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5072 | Productive mixed dry/wet-season region. |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5074 | Very wet/high-GPP/low-deficit region. |

Continuation diagnostics in `artifacts/region_allowed_input_diagnostics.csv` showed C0 overpredicts weak-region mean burned area by large factors: MIDE 18.88x, TENA 14.88x, EURO 13.61x, CEAM 10.46x, EQAS 8.95x, SEAS 7.88x, SHSA 6.68x. However, those weak regions are not one clean physical class under the allowed inputs. For example, MIDE and AUST are both dry/low-productivity regimes, but AUST is already well calibrated. EURO/TENA are cool productive mosaics, while EQAS is very wet/high-productivity/low-deficit. This made broad smooth suppression intrinsically risky.

## First-cycle mechanisms already completed

| ID | Family | Mechanism | Official global Overall | Global Spatial | Decision |
|---|---|---|---:|---:|---|
| H1 | Annual humid suppression | `1/(1+(P_ann/P_humid)^q)` with retuned base | 0.6384 | 0.5837 | Reject |
| H1m | Mild annual humid suppression | Same, fixed C0 base, mild params | 0.6538 | 0.6828 | Reject |
| H2 | Wet-month logistic | `supp(P_month; wet_k, wet_c)` | 0.6534 | 0.6524 | Reject |
| H3 | Seasonal contrast/curing | `1/(1+(P_month/(P_ann/12+eps))^q)` | 0.6654 | 0.7267 | Reject as final; regional-compromise alternative |

H3 public benchmark:
- Overall 0.6652, below C0 0.6713 and CLASSIC 0.6660.

First-cycle learning carried forward: wetness/curing suppression is physically plausible and consistently repairs weak regions, but broad precipitation/curing gates damage global spatial pattern. The continuation cycle therefore tested second-order gates designed to act only in physically uncured/wet/productive/cool/low-fuel states.

## Continuation mechanisms and results

### Additional diagnostics

Created/ran:
- `scripts/region_diagnostics_allowed_inputs.py`
- output `artifacts/region_allowed_input_diagnostics.csv`

Key learning: the weak regions span mutually conflicting allowed-input states. This foreshadowed why no global smooth factor could isolate them cleanly.

### H4: dry-gated wet-month suppression

Mechanistic hypothesis:
Current-month rain should suppress active burning mainly when antecedent drying is insufficient to cure fuels. This should be more selective than H2 wet-month suppression and should preserve dry savanna fires.

Formula factor:

`dry_gated_wet = 1 - wet_alpha * supp(Dbar; drygate_k,drygate_c) * (1 - supp(P_month; wet_k,wet_c))`

Search:
- 500 Optuna proxy trials.
- Artifact: `artifacts/search2/dry_gated_wetmonth_500.json`
- Params: `models/H4_dry_gated_wetmonth/params.json`
- NetCDF: `ilamb/MODELS/ED-H4-dry-gated-wetmonth/burntArea.nc`

Best proxy looked promising:
- Proxy global Overall 0.6878.
- Proxy weak mean 0.3722.
- Promoted to official evaluation.

Official ILAMB command:
`ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_H4_regions`

Official H4 global result:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| H4 dry-gated wetmonth | 0.7246 | 0.5162 | 0.8490 | 0.5786 | 0.6369 |
| C0 original Model C | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 |

H4 weak-region Overalls:

| Region | C0 | H4 | Delta |
|---|---:|---:|---:|
| euro | 0.3611 | 0.5148 | +0.1537 |
| ceam | 0.3762 | 0.4707 | +0.0945 |
| tena | 0.3815 | 0.4998 | +0.1183 |
| mide | 0.3828 | 0.4266 | +0.0438 |
| seas | 0.4872 | 0.5527 | +0.0655 |
| shsa | 0.5072 | 0.6208 | +0.1136 |
| eqas | 0.5074 | 0.6622 | +0.1548 |

Decision: rejected. H4 is scientifically informative but not acceptable. It repaired weak regions even better than H3, but global Overall fell by -0.0346 and global Spatial fell by -0.1938. It was not run through the public TRENDY/firepipe comparison because official global/regional ILAMB was already far below C0 and H3, so it no longer met the serious-candidate threshold.

### P1: dry-gated annual humid suppression

Mechanism:
Annual high-rainfall suppression gated by low accumulated Dbar.

Search:
- 500 Optuna proxy trials.
- Artifact: `artifacts/search2/dry_gated_humid_500.json`

Proxy result:
- Global Overall 0.6523.
- Spatial 0.4328.
- Weak mean 0.3848.

Decision: rejected before official. Less promising than H4 and already showed poor proxy spatial behavior; H4 then failed official decisively.

### P2: wet productive forest / closed-canopy proxy

Mechanism:
Suppress high-GPP, high-annual-precipitation, low-Dbar cells as a smooth global proxy for wet productive forest/closed canopy.

Search:
- 500 Optuna proxy trials.
- Artifact: `artifacts/search2/wet_productive_forest_500.json`

Proxy result:
- Global Overall 0.5927.
- Seasonal 0.3290.
- Spatial 0.4645.
- Weak mean 0.3845.

Decision: rejected before official. It over-suppressed productive regimes and damaged seasonality/spatial structure.

### P3: hyperarid low-fuel suppression

Mechanism:
Suppress low annual precipitation × low GPP cells as a fuel-discontinuity/desert limit.

Search:
- 64-point deterministic grid.
- Artifact: `artifacts/search2/hyperarid_fuel_grid.json`

Proxy result:
- Global Overall 0.5525.
- Weak mean 0.3240.

Decision: rejected before official. Mechanistic discrimination failed: MIDE is overpredicted, but AUST has similarly low GPP/dryness and is already well calibrated. The allowed inputs cannot separate these regimes without a forbidden region/human/land-use signal.

### P4: cool uncured ignition interaction

Mechanism:
Suppress cool, insufficiently cured months using air temperature × low Dbar.

Search:
- 500 Optuna proxy trials.
- Artifact: `artifacts/search2/cool_uncured_supp_500.json`

Proxy result:
- Global Overall 0.5684.
- Weak mean 0.3443.

Decision: rejected before official. It was not competitive and did not resolve spatial placement.

### P5: productivity-shape grid

Mechanism:
Probe whether retuning global GPP/productivity shape, fire exponent, and monthly precipitation half-saturation can reduce weak-region overprediction without new wet gates.

Search:
- 360-point deterministic grid.
- Artifact: `artifacts/search2/productivity_shape_grid.json`

Best proxy result:
- Global Overall 0.6185.
- Weak mean 0.3477.

Decision: rejected before official. Less promising than H4 proxy; since H4 failed official badly, this lower-quality proxy was not a serious candidate. Also, Model C was already produced from a broad 12-parameter Optuna fit, so a small productivity retune is unlikely to produce a step-function official improvement.

## Full candidate comparison

Official global ILAMB:

| Run | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---:|---:|---:|---:|---:|---|
| C0 original Model C | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 | Best global/public |
| H1 retuned annual humid | 0.7243 | 0.5173 | 0.8496 | 0.5837 | 0.6384 | Reject |
| H1m mild humid | 0.7263 | 0.5068 | 0.8460 | 0.6828 | 0.6538 | Reject |
| H2 wet-month | 0.7290 | 0.5168 | 0.8521 | 0.6524 | 0.6534 | Reject |
| H3 seasonal contrast | 0.7304 | 0.5110 | 0.8480 | 0.7267 | 0.6654 | Reject as final; best compromise |
| H4 dry-gated wetmonth | 0.7246 | 0.5162 | 0.8490 | 0.5786 | 0.6369 | Reject |

Weak-region Overall comparison:

| Region | C0 | H1 | H1m | H2 | H3 | H4 |
|---|---:|---:|---:|---:|---:|---:|
| euro | 0.3611 | 0.5173 | 0.4096 | 0.4932 | 0.4198 | 0.5148 |
| ceam | 0.3762 | 0.5039 | 0.4269 | 0.4327 | 0.4104 | 0.4707 |
| tena | 0.3815 | 0.4727 | 0.4258 | 0.4865 | 0.4289 | 0.4998 |
| mide | 0.3828 | 0.4191 | 0.4101 | 0.4089 | 0.4115 | 0.4266 |
| seas | 0.4872 | 0.5749 | 0.5377 | 0.5272 | 0.5149 | 0.5527 |
| shsa | 0.5072 | 0.6404 | 0.5755 | 0.5844 | 0.5551 | 0.6208 |
| eqas | 0.5074 | 0.6801 | 0.5694 | 0.6268 | 0.5525 | 0.6622 |
| global | 0.6715 | 0.6384 | 0.6538 | 0.6534 | 0.6654 | 0.6369 |

Updated comparison artifact:
`artifacts/official_candidate_regional_scores_v2.csv`

## Public TRENDY/firepipe comparison

Public clean benchmark was run for C0 and H3, the only candidate after the first cycle close enough to be serious.

| Run | Public Overall | Public decision |
|---|---:|---|
| C0 original Model C | 0.6713 | Rank #1/tied copied baseline; final best |
| H3 seasonal contrast | 0.6652 | Below C0 and CLASSIC; reject as final |

H4 did not receive a public run because official global/regional ILAMB was much worse than C0 and H3. Running public comparison for H4 would not change the acceptance decision and would not satisfy the step-function improvement goal.

## Mechanistic interpretation of the failure boundary

The continuation cycle changes the strength of the final conclusion. The first pass could have been interpreted as “precipitation gates are too crude.” The second pass tested less crude, more mechanistic second-order gates:
- wet suppression conditioned on lack of accumulated drying,
- annual humid suppression conditioned on lack of accumulated drying,
- wet productive forest/closed-canopy proxy,
- hyperarid low-fuel proxy,
- cool uncured ignition interaction,
- productivity-shape retuning.

None produced a defensible replacement. H4 is the strongest evidence: it encodes a plausible fire-physics rule and substantially improves weak regions, but it still destroys global spatial skill. This means the failing regions are not separable by the available local climate/productivity state without also suppressing real fire regimes in boreal, African, Australian, and central Asian patterns.

Likely missing variables/processes under the fixed contract:
- human ignition and suppression,
- cropland/pasture fragmentation,
- fire management in Europe/Temperate North America/Middle East,
- irrigation and low-fuel discontinuity not captured by annual precipitation/GPP alone,
- peat/deforestation fire type in Equatorial/Southeast Asia,
- lightning/human ignition geography,
- sub-grid fuel continuity and vegetation structure.

These mechanisms are not available as inputs. Encoding them via named regions, lat/lon, lookup tables, or residual corrections is forbidden and would not be scientifically defensible under the contract.

## Final recommendation

Use original Model C (C0) as the final model for this constrained run.

Do not replace it with H1/H1m/H2/H3/H4. H3 may be documented as the least damaging regional-compromise alternative if the objective changes away from global/public rank, but it is not a better final model under the stated criteria. H4 should be retained only as diagnostic evidence that even dry-gated wet suppression cannot preserve global spatial structure.

## Reproducibility map

Required logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`

Core scripts created/updated:
- `scripts/fire_explore.py`
- `scripts/region_diagnostics_allowed_inputs.py`
- `scripts/grid_hyperarid_family.py`
- `scripts/grid_productivity_shape.py`
- `scripts/compare_candidates_v2.py`
- `scripts/summarize_ilamb_scores.py`
- `scripts/summarize_any_ilamb.py`
- `scripts/grid_humid_ablation.py`
- `scripts/grid_other_families.py`
- `scripts/compare_candidates.py`

Candidate params:
- `models/H1_annual_humid_supp/params.json`
- `models/H1m_mild_humid/params.json`
- `models/H2_wetmonth/params.json`
- `models/H3_seasonal_contrast/params.json`
- `models/H4_dry_gated_wetmonth/params.json`

Candidate NetCDFs:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- `ilamb/MODELS/ED-H1-annual-humid-supp/burntArea.nc`
- `ilamb/MODELS/ED-H1m-mild-humid/burntArea.nc`
- `ilamb/MODELS/ED-H2-wetmonth/burntArea.nc`
- `ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc`
- `ilamb/MODELS/ED-H4-dry-gated-wetmonth/burntArea.nc`

Official ILAMB outputs:
- `ilamb/output_modelC/scalar_database.csv`
- `ilamb/output_modelC_regions/scalar_database.csv`
- `ilamb/output_H1_regions/scalar_database.csv`
- `ilamb/output_H1m_regions/scalar_database.csv`
- `ilamb/output_H2_regions/scalar_database.csv`
- `ilamb/output_H3_regions/scalar_database.csv`
- `ilamb/output_H4_regions/scalar_database.csv`

Public benchmark outputs:
- `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-repro/scalar_database.csv`
- `public_benchmark_clean/ilamb/output_with_ED-H3-seasonal-contrast/scalar_database.csv`

Derived artifacts:
- `artifacts/region_allowed_input_diagnostics.csv`
- `artifacts/official_candidate_regional_scores.csv`
- `artifacts/official_candidate_regional_scores_v2.csv`
- `artifacts/search2/dry_gated_humid_500.json`
- `artifacts/search2/dry_gated_wetmonth_500.json`
- `artifacts/search2/wet_productive_forest_500.json`
- `artifacts/search2/hyperarid_fuel_grid.json`
- `artifacts/search2/cool_uncured_supp_500.json`
- `artifacts/search2/productivity_shape_grid.json`
- `artifacts/search2/H4_official_summary.txt`
- `artifacts/search2/official_candidate_regional_scores_v2_summary.txt`
