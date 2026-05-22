# Final Report: Constrained Model C Fire-Model Improvement Run

## Executive conclusion

Best model found in this workspace: `ED-C2-rain_ignition_shift`.

This candidate is a single global mechanistic extension of original Model C. It keeps the Model C core fixed and replaces the independent monthly air-temperature ignition term with a monthly rain-conditioned ignition threshold, then applies a global rate-power compression before the ED annual-rate to monthly burned-fraction transform.

Local official ILAMB result:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.755836 | 0.675267 |
| Original ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |

C2-rain improves local official Overall by +0.003738, with gains in Bias, RMSE, and Seasonal Cycle. It gives up Spatial Distribution (-0.016515), but unlike the rejected C1/C2 wetness variants, the spatial loss is moderate and regional behavior improves in nearly all initially weak regions.

Public TRENDY/firepipe comparison:

| Public rank | Model | Overall |
|---:|---|---:|
| 1 | ED-ModelC-baseline | 0.675085 |
| 2 | ED-C2-rain_ignition_shift | 0.675020 |
| 3 | CLASSIC | 0.666048 |
| 4 | CLM6.0 | 0.660644 |

In the public clean benchmark root, C2-rain is effectively tied with but very slightly below the included public ED-ModelC-baseline by 0.000065. Therefore I do not claim an unequivocal public leaderboard replacement. I do claim that C2-rain is the most defensible new mechanistic candidate from this run because it improves the local official global score and substantially improves many regional failures while satisfying the fixed input contract.

## Final formula

Original Model C core:

```
base_rate_C = [ onset(Dbar) * suppress(Dbar)
                * precip_floor(P_ann) * precip_dampen(P_month)
                * gpp_hump(GPP_month)
                * old_ign(T_air) ] ^ fire_exp_C
```

C2-rain global extension:

```
old_ign(T) = sigmoid(T_air; ign_k_C, ign_c_C)
new_ign(T, Pm) = sigmoid(T_air; ign_k2, ign_c_C + rain_shift * log1p(P_month))
rain_ignition_ratio = clip(new_ign / (old_ign + 1e-6), 0.02, 5.0)
raw_rate = base_rate_C * rain_ignition_ratio
compressed_rate = raw_rate ^ rate_power
burntArea_monthly = (1 - exp(-min(compressed_rate, 5.0))) / 12
```

Final parameters added by C2-rain:

```
rain_shift = 1.8584561329682763
ign_k      = 0.6241606715796371
rate_power = 0.700475533169256
```

All other Model C parameters are unchanged from `models/C/params.json`.

Mechanistic interpretation:
- Monthly precipitation acts as a humidity/wet-fuel proxy.
- Wet months raise the effective ignition/spread temperature threshold, so hot conditions do not contribute as strongly when fuels and atmosphere are wet.
- The global `rate_power` is an intensity/patchiness compression analogous to Model C's existing global exponent. Ablations show it cannot explain the gain alone.

Detailed formula documentation is in:
`models/research/ED-C2-rain_ignition_shift/formula.md`

## Baseline verification

Required documents were read before modifications/evaluation:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `README.md`
- `WRITEUP.md`
- `models/C/formula.md`

Commands run:
- `.venv/bin/python scripts/verify.py`
- `.venv/bin/python scripts/reproduce_modelC.py`
- `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/ilamb bash scripts/run_ilamb.sh`

Verification found all pinned input arrays, params, and GFED/GPP data present and hash-matched. Two pre-existing generated artifacts differed in size from `CHECKSUMS.txt` before regeneration:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13600931 bytes, got 13466737.
- `out_terms/modelC_terms.nc`: expected 112006460 bytes, got 116077308.

Baseline `burntArea.nc` was regenerated before scoring. Regeneration diagnostics:
- land cells: 13826 / 64800
- raw rate land mean: 0.09018 yr^-1
- max raw rate: 0.9987
- transformed land mean: 0.00610759
- GFED land mean: 0.00298745
- ratio: 2.044

## Initial regional triage

Official regional ILAMB was run with built-in ILAMB regions:

`global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust`

The regional scalar database did not include regional Overall Score rows, so I used the diagnostic tier-style regional aggregate:

`(2*Bias + 2*RMSE + Seasonal + Spatial) / 6`

Worst original Model C regions:

| Region | Bias | RMSE | Seasonal | Spatial | Diagnostic aggregate | Main failure |
|---|---:|---:|---:|---:|---:|---|
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3613 | severe bias/RMSE/spatial failure |
| euro | 0.3935 | 0.2618 | 0.8082 | 0.0805 | 0.3665 | severe spatial/RMSE failure |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3907 | poor spatial/RMSE |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3918 | poor spatial/RMSE |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4887 | wet/high-productivity mismatch |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5016 | bias/RMSE/spatial mismatch |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5024 | wet rainforest/peat/cropland heterogeneity |

This pattern suggested missing physics around wet-fuel suppression, rain/humidity-conditioned ignition, high-precipitation fire suppression, and relative dry-season gating.

## Research loops performed

### Loop 1: broad full-refit mechanism families

Script: `scripts/research_model_variants.py`.

Each family was searched with 500 Optuna trials and baseline enqueue. These were global formulas using only the allowed inputs.

Families:
- `wet_gpp_supp`: wet/high-GPP live-fuel or closed-canopy suppression.
- `annual_p_hump`: annual precipitation supplies fuel at low values but suppresses fire in very wet climates.
- `rain_temp_shift`: monthly rain raises ignition temperature threshold.
- `dry_season_gate`: month must be dry relative to annual water supply.
- `base_refit`: broad 12-parameter Model C refit.

Results:

| Candidate | Official Overall | Decision |
|---|---:|---|
| ED-C1-rain_temp_shift | 0.6568 | rejected as global replacement; regional diagnostic |
| ED-C1-annual_p_hump | 0.6426 | rejected; global spatial collapse |
| ED-C1-wet_gpp_supp | identical to C0 | no-op selected |
| ED-C1-dry_season_gate | identical to C0 | no-op selected |
| ED-C1-base_refit | identical to C0 | original params selected |

Loop 1 conclusion: wetness/rain mechanisms can improve weak regions, but broad full refits overcorrect and sacrifice global spatial structure. This led to targeted fixed-core searches.

### Loop 2: targeted fixed-core mechanism gates

Script: `scripts/search_targeted_mechanisms.py`.

Each family used 1000 Optuna trials while keeping the original Model C core fixed.

Official global ILAMB:

| Model | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---:|---:|---:|---:|---:|---|
| ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.755836 | 0.675267 | best |
| ED-C2-combined_wet_rain | 0.732270 | 0.519013 | 0.847854 | 0.747125 | 0.673055 | rejected by parsimony |
| ED-C2-wet_gpp_amp | 0.735033 | 0.512834 | 0.848808 | 0.748156 | 0.671533 | near tie; not meaningful |
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | baseline |
| ED-C2-annual_wet_amp | 0.733769 | 0.511839 | 0.846820 | 0.738642 | 0.668582 | rejected |

Loop 2 conclusion: rain-conditioned ignition is the best-supported mechanism. The combined wet/rain candidate is more complex and worse than rain-only. Wet-GPP and annual-wet gates help regions but do not provide a meaningful global improvement.

## Regional behavior of final candidate

C2-rain regional diagnostic aggregate vs C0:

| Region | C0 diag | C2-rain diag | Change |
|---|---:|---:|---:|
| ceam | 0.3613 | 0.4281 | +0.0668 |
| euro | 0.3665 | 0.5335 | +0.1670 |
| tena | 0.3907 | 0.4652 | +0.0745 |
| mide | 0.3918 | 0.4249 | +0.0331 |
| seas | 0.4887 | 0.5151 | +0.0264 |
| shsa | 0.5016 | 0.5327 | +0.0311 |
| eqas | 0.5024 | 0.5598 | +0.0574 |
| nhsa | 0.5884 | 0.6030 | +0.0146 |
| shaf | 0.6655 | 0.6528 | -0.0127 |
| nhaf | 0.6664 | 0.6748 | +0.0084 |

C2-rain improves all initially weakest regions. The main tradeoff is a small decline in Southern Africa and a moderate global Spatial Distribution decline. This is acceptable as a candidate because the improvement is not confined to one named region; it follows a global rain-conditioned ignition mechanism.

## Ablations

Ablation artifacts:
- `ED-C2-ablate-rate_power_only`
- `ED-C2-ablate-rain_no_power`

Official global ILAMB:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.755836 | 0.675267 |
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| ED-C2-ablate-rate_power_only | 0.713197 | 0.496505 | 0.846275 | 0.753624 | 0.661221 |
| ED-C2-ablate-rain_no_power | 0.726811 | 0.522298 | 0.849220 | 0.680497 | 0.660225 |

Ablation conclusion: the improvement is not a scalar exponent trick. The rate-power compression alone fails, and the rain-conditioned ignition gate alone fails. The accepted candidate needs the combined physically motivated rain ignition replacement plus global compression.

## Public benchmark

Command:

`MODEL_NAME=ED-C2-rain_ignition_shift SRC=$PWD/ilamb/MODELS/ED-C2-rain_ignition_shift/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`

Output:
`public_benchmark_clean/ilamb/output_with_ED-C2-rain_ignition_shift/scalar_database.csv`

Leaderboard rows with Overall:

| Rank | Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---:|---|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-baseline | 0.734518 | 0.509637 | 0.849154 | 0.772477 | 0.675085 |
| 2 | ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.754600 | 0.675020 |
| 3 | CLASSIC | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.666048 |
| 4 | CLM6.0 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.660644 |

The public script reported an IndexError for JSBACH but completed and wrote scores for models with Overall rows. C2-rain is not public rank #1, but it remains above CLASSIC and CLM6.0 and essentially tied with public Model C.

## Constraint compliance

C2-rain uses only allowed inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`

No violations found:
- No external data inputs.
- No latitude/longitude hacks in the formula.
- No per-cell lookup tables.
- No named-region routing.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct cell-identity fitting to GFED.
- No prior/archive experiment evidence outside this workspace.

## Remaining failures and why they appear unresolved under the fixed contract

Even C2-rain leaves low diagnostic regional aggregates in:
- `mide`: 0.4249
- `ceam`: 0.4281
- `tena`: 0.4652
- `seas`: 0.5151
- `euro`: 0.5335, despite a large improvement

The persistent failures are largely spatial-structure problems. Under the fixed inputs, the model has climate, GPP, and dryness information, but not the drivers likely needed for these regions:
- cropland/land-use extent and management,
- human ignition and suppression pressure,
- grazing/fuel continuity,
- peat/fire type distinctions,
- forest/canopy/fuel-structure information beyond monthly GPP,
- lightning or population/road proxies.

Adding further wetness gates can improve weak regions but consistently costs global Spatial Distribution or adds complexity without beating C2-rain. Continuing to search within the same input contract therefore appears likely to tune tradeoffs rather than discover a more defensible global mechanism.

## Best model set

Best local official global model:
- `ED-C2-rain_ignition_shift`, Overall 0.675267.

Best public benchmark model in this workspace:
- `ED-ModelC-baseline`, Overall 0.675085, with C2-rain second at 0.675020.

Best regional diagnostic alternatives:
- `ED-C2-rain_ignition_shift`: best balance; improves all initially worst regions with acceptable complexity.
- `ED-C2-combined_wet_rain`: slightly stronger in some wet regions but lower global Overall and much more complex.
- `ED-C1-annual_p_hump`: strong regional diagnostic improvements but unacceptable global Spatial collapse.

Chosen final candidate:
- `ED-C2-rain_ignition_shift`, because it is the only candidate with local official global improvement, broad regional improvement, public comparator evidence, ablation support, and a compact mechanistic explanation.

## Reproducibility artifacts

Core logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`

Scripts:
- `scripts/research_model_variants.py`
- `scripts/search_targeted_mechanisms.py`
- `scripts/run_public_trendy_firepipe_clean.sh`

Best candidate artifacts:
- `models/research/ED-C2-rain_ignition_shift/params.json`
- `models/research/ED-C2-rain_ignition_shift/formula.md`
- `models/research/ED-C2-rain_ignition_shift.search.log`
- `ilamb/MODELS/ED-C2-rain_ignition_shift/burntArea.nc`

Official ILAMB outputs:
- Baseline global: `ilamb/output_modelC/scalar_database.csv`
- Baseline regional: `ilamb/output_modelC_regions/scalar_database.csv`
- C1 selected global: `ilamb/output_C1_selected_global_full/scalar_database.csv`
- C1 selected regional: `ilamb/output_C1_selected_regions/scalar_database.csv`
- C2 annual regional/global: `ilamb/output_C2_annual_regions/`, `ilamb/output_C2_annual_global_full/`
- C2 wet-GPP regional/global: `ilamb/output_C2_wetgpp_regions/`, `ilamb/output_C2_wetgpp_global_full/`
- C2 rain regional/global: `ilamb/output_C2_rainign_regions/`, `ilamb/output_C2_rainign_global_full/`
- C2 combined regional/global: `ilamb/output_C2_combined_regions/`, `ilamb/output_C2_combined_global_full/`
- C2 ablations: `ilamb/output_C2_ablation_global_full/`

Public benchmark output:
- `public_benchmark_clean/ilamb/output_with_ED-C2-rain_ignition_shift/scalar_database.csv`

## Final stopping statement

I stopped after two distinct outer loops, multiple mechanistic families, targeted follow-up searches, official global/regional ILAMB evaluation, public TRENDY/firepipe comparison, and ablations. C2-rain is the empirical ceiling found for a compact mechanistic improvement under the fixed contract. More complex wetness/productivity variants did not produce a defensible improvement over rain-conditioned ignition, and remaining regional errors appear tied to excluded predictors rather than a missing smooth transform of the available inputs.
