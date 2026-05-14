# Final Report — ED Model C constrained fire-formula improvement

## Executive summary
This run started from original Model C and tested whether a unified, interpretable burned-area functional form could improve global fit and regional behavior under the fixed input contract.

Best balanced accepted model: C7, a global Model C extension with two smooth multiplicative mechanisms:

1. active dry-down / curing gate from `Dbar - mean(Dbar previous 3 months)`, and
2. humid-regime suppression from high annual precipitation.

C7 official global ILAMB:
- Overall: 0.673264 vs baseline 0.671529 (+0.001735)
- Bias: 0.731755 vs 0.728089 (+0.003666)
- RMSE: 0.508111 vs 0.505759 (+0.002352)
- Seasonal: 0.851062 vs 0.845690 (+0.005372)
- Spatial: 0.767279 vs 0.772351 (-0.005072)

The scalar global gain is modest, but C7 is more regionally defensible than baseline: it improves CEAM, SHSA, SEAS, EQAS, NHSA, TENA, EURO, CEAS, NHAF, and BOAS. It slightly worsens SHAF, BONA, and AUST. The best regional variant is C6b (humid suppression only, floor=0), which gives the strongest EQAS gain (+0.082 Overall) and best SHSA/SEAS humid-tropical behavior, but C7 is the better global/balanced choice because it also recovers seasonal/dry-down behavior.

Clean public TRENDY/firepipe for C7: 0.673022, above public baseline-current 0.671274 and all non-ED public models in the benchmark table, but behind a pre-existing benchmark-source ED-ModelC-pass2-P2F3 model at 0.676846. The known JSBACH ILAMB IndexError occurred; score table was produced.

The defensible stopping point is: accept C7 as the final balanced candidate and record C6b as the best regional/humid-tropical model. Further gains under this input contract appear limited by missing human ignition/suppression, land-use/cropland, lightning, vegetation structure, and management variables; more tuning of tested families mostly creates spatial tradeoffs.

## Required files read before work
Read before code changes:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

## Baseline reproduction and benchmark context
Verification:
- Command: `.venv/bin/python scripts/verify.py`
- Result: PASS; 24/24 artifacts present and hash OK.

Official baseline global ILAMB:
- Command: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh`

Official baseline regional ILAMB:
- Command: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh`

Baseline official global score:
| Model | Overall | Bias | RMSE | Seasonal | Spatial |
|---|---:|---:|---:|---:|---:|
| C0 baseline Model C | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 |

Baseline regional diagnosis:
- Strong regions: BONA, BOAS, CEAS/AUST/NHAF/SHAF reasonably high Overall.
- Weak regions: EURO 0.361, CEAM 0.376, TENA 0.381, MIDE 0.383, SEAS 0.487, EQAS 0.507, SHSA 0.507.
- Dominant failure mode: weak-region spatial distribution, especially EURO 0.080, MIDE 0.091, CEAM 0.126, TENA 0.160, EQAS 0.177.
- Australia has good Overall but poor Seasonal Cycle 0.580.

## Final accepted model: C7 humid-regime suppression + active dry-down
Output files:
- Candidate metadata: `candidates/C7_humid_dryrate_added_only.json`
- Candidate NetCDF: `candidates/C7_humid_dryrate_added_only/burntArea.nc`
- Final model copy: `final_model/params_and_metadata.json`
- Final model NetCDF: `final_model/burntArea.nc`
- Formula note: `final_model/formula.md`

Formula:

```text
base = onset(Dbar) * suppress(Dbar)
     * precip_floor(P_ann) * precip_dampen(P_month)
     * gpp_hump(GPP_month) * air_temp_ign(T_air)

dry_gate = dry_floor
         + (1 - dry_floor) * sigmoid(Dbar - mean(Dbar previous 3 months), dry_k, dry_c)

humid_gate = humid_floor
           + (1 - humid_floor) / (1 + (P_ann / humid_half)^humid_pow)

fire_rate_yr = (base * dry_gate * humid_gate)^fire_exp
burntArea_month = (1 - exp(-min(fire_rate_yr, 5.0))) / 12
```

C7 added parameters:
| Parameter | Value | Meaning |
|---|---:|---|
| dry_floor | 0.7427444437 | Lower bound for dry-down gate; avoids hard zero outside active dry-down |
| dry_k | 0.0598131832 | Steepness of dry-down response |
| dry_c | 75.98500904 | Dry-down threshold in Dbar units |
| dry_lag_window | 3 | Dbar previous-month averaging window |
| humid_floor | 0.0590929766 | Humid-gate lower bound |
| humid_half | 2129.912069 | Annual precipitation midpoint for humid suppression |
| humid_pow | 5.993080469 | Shape/steepness of humid suppression |

Mechanistic explanation:
- Model C already contains dryness onset/suppression, precipitation floor/dampening, GPP hump, and warm-temperature ignition.
- `dry_gate` adds a dynamic flammability/curing mechanism: fire is favored when fuels are actively drying, not merely when the accumulated dry index is high. This is globally applied and uses only Dbar history.
- `humid_gate` adds a missing wet-fuel/evergreen humid-regime ceiling: annual precipitation above roughly 2.1 m/yr suppresses fire risk sharply. This separates humid tropical forest regimes from seasonal savanna/cropland fire regimes without named regions or external land-cover data.

## Highest global-score model
Highest official global score from candidates generated in this run: C7.

| Candidate | Overall | Bias | RMSE | Seasonal | Spatial |
|---|---:|---:|---:|---:|---:|
| C0 baseline | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 |
| C2 dryrate | 0.672542 | 0.729561 | 0.507665 | 0.852988 | 0.764830 |
| C6b humid suppress | 0.672691 | 0.732340 | 0.507491 | 0.845969 | 0.770162 |
| C7 humid+dryrate | 0.673264 | 0.731755 | 0.508111 | 0.851062 | 0.767279 |

## Best regional model if different
Best regional/humid-tropical model: C6b, the humid annual-precipitation suppression with `humid_floor=0`.

C6b is not the final balanced model because C7 has higher global Overall and better seasonal/dry-down behavior, but C6b is the regional winner for EQAS and strong in SHSA/SEAS/CEAM:
- EQAS: 0.589676 vs baseline 0.507395 (+0.082281)
- SHSA: 0.529248 vs 0.507249 (+0.021999)
- SEAS: 0.505065 vs 0.487193 (+0.017872)
- CEAM: 0.394321 vs 0.376153 (+0.018168)

## Baseline vs serious candidates regional ILAMB table
Overall Score:
| Region | Baseline | C2 dryrate | C6b humid | C7 humid+dry | Best delta vs baseline |
|---|---:|---:|---:|---:|---:|
| bona | 0.789806 | 0.787680 | 0.789910 | 0.788504 | +0.000104 |
| tena | 0.381473 | 0.387950 | 0.385201 | 0.387201 | +0.006477 |
| ceam | 0.376153 | 0.388136 | 0.394321 | 0.395297 | +0.019144 |
| nhsa | 0.605824 | 0.612135 | 0.612635 | 0.614489 | +0.008665 |
| shsa | 0.507249 | 0.514548 | 0.529248 | 0.524389 | +0.021999 |
| euro | 0.361128 | 0.368368 | 0.362372 | 0.366309 | +0.007240 |
| mide | 0.382769 | 0.385654 | 0.382955 | 0.384436 | +0.002885 |
| nhaf | 0.645855 | 0.647620 | 0.646670 | 0.648910 | +0.003055 |
| shaf | 0.646693 | 0.644307 | 0.645391 | 0.643847 | -0.001302 |
| boas | 0.728733 | 0.730300 | 0.728764 | 0.729999 | +0.001567 |
| ceas | 0.670499 | 0.674705 | 0.670835 | 0.672759 | +0.004206 |
| seas | 0.487193 | 0.496964 | 0.505065 | 0.505368 | +0.018175 |
| eqas | 0.507395 | 0.526712 | 0.589676 | 0.574394 | +0.082281 |
| aust | 0.670219 | 0.670222 | 0.668985 | 0.669813 | +0.000003 |

C7 component details for selected weak regions:
| Region | Overall | Bias | RMSE | Seasonal | Spatial |
|---|---:|---:|---:|---:|---:|
| tena | 0.387201 | 0.445488 | 0.312120 | 0.694408 | 0.171867 |
| ceam | 0.395297 | 0.336977 | 0.325592 | 0.853464 | 0.134857 |
| euro | 0.366309 | 0.404679 | 0.267692 | 0.808543 | 0.082937 |
| mide | 0.384436 | 0.439416 | 0.311521 | 0.766612 | 0.093107 |
| seas | 0.505368 | 0.541070 | 0.391427 | 0.827774 | 0.375143 |
| eqas | 0.574394 | 0.615140 | 0.560690 | 0.849325 | 0.286124 |
| aust | 0.669813 | 0.746970 | 0.652718 | 0.579719 | 0.716941 |

## Public TRENDY/firepipe ranking table
Clean public run used C7 after deleting the previous public model/build directories.

Command:
```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```

Known caveat: JSBACH raised the documented ILAMB `IndexError`, then completed during collective post-processing; the score table was produced.

| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial | Period mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 2 | ED-ModelC-formal-candidate (C7) | 0.673022 | 0.731755 | 0.508111 | 0.851062 | 0.766069 | 0.547347 |
| 3 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| 4 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| 5 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| 6 | ED-ModelC-curing-lag-v1-current | 0.671767 | 0.727997 | 0.505755 | 0.848710 | 0.770616 | 0.614471 |
| 7 | ED-ModelC-lag-fuel-v1-current | 0.671600 | 0.728075 | 0.505767 | 0.848154 | 0.770237 | 0.622335 |
| 8 | ED-ModelC-opt-wet-v1-current | 0.671436 | 0.730475 | 0.506667 | 0.845975 | 0.767397 | 0.567266 |
| 9 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| 10 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| 11 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |

Note: The public benchmark directory already contained previous ED-ModelC variants, including `ED-ModelC-pass2-P2F3`; those were treated as comparison context, not as allowed model inputs for this run.

## Mechanisms tried
1. Lagged GPP fuel persistence (C1): rejected; optimum collapsed to current GPP and proxy worsened.
2. Active dry-down/curing (C2): accepted as useful; improves Seasonal and many weak regions but costs Spatial.
3. Antecedent wet-season precipitation fuel gate (C3): rejected; near-identity optimum.
4. Full lagged/wet/dry combo (C4): rejected; complexity not justified.
5. Dryrate plus base retune (C5): rejected; broad retune worsened proxy, implying baseline parameters are robust.
6. Humid high-annual-precipitation suppression (C6/C6b/C6d): accepted; strongest regional mechanism, especially EQAS.
7. Humid suppression plus active dry-down (C7): accepted final balanced model.

## Optuna/search setup and trial counts
Search script: `scripts/explore_mechanisms.py`.

The proxy objective approximated ILAMB tier-2 behavior with Bias and RMSE double-weighted:
`overall = (2*Bias + 2*RMSE + Seasonal + Spatial) / 6`.
Official ILAMB, not the proxy, determined acceptance.

| Candidate | Search type | Trials |
|---|---|---:|
| C1 lagged GPP | Optuna added params | 500 |
| C2 dryrate | Optuna added params | 500 |
| C3 wetdry | Optuna added params | 500 |
| C4 combo | Optuna added params | 700 |
| C5 dryrate retuned | Optuna all params | 1000 |
| C6 humid suppression | Optuna added params | 700 |
| C6b/C6c/C6d | deterministic ablations | 4 variants |
| C7 humid+dryrate | Optuna added params | 1000 |

## Ablation results and complexity pruning
Humid suppression ablations:
- C6: three free humid parameters; official Overall 0.672531.
- C6b: `humid_floor=0`; official Overall 0.672691 and best EQAS regional score. This showed that a strong/high-precipitation ceiling is meaningful, not a fragile tuning artifact.
- C6c: lower power 4; proxy fell, indicating a sharp threshold-like humid ceiling is more consistent with the data.
- C6d: rounded `humid_half=2000`, `humid_pow=6`, `humid_floor=0.05`; official Overall 0.672686, near C6b. This supports pruning toward a simple physical threshold if desired.

Dryrate ablation/retune:
- C2 added dryrate only improved official global and weak regions.
- C5 retuned all base parameters plus dryrate for 1000 trials and worsened proxy; broad retuning was not pursued as final because it looked like unstable parameter fitting rather than mechanism discovery.

Rejected complexity:
- Lagged GPP and wet-season precipitation gates were rejected because Optuna pushed them near identity or because official/proxy scores did not justify added complexity.
- C4 combo was worse than the simpler C2/C6/C7 pathways.

## Constraint compliance
C7 and all candidates use only allowed model inputs:
- Dbar monthly
- Annual precipitation
- Monthly precipitation
- Monthly air temperature
- Monthly EDv3 GPP

C7 derived variables are global transforms:
- `Dbar - mean(Dbar previous 3 months)`
- smooth function of annual precipitation

No candidate used:
- external data as model input,
- latitude/longitude hacks,
- named-region routing,
- per-cell lookup tables,
- per-region formulas,
- arbitrary residual correction coefficients,
- direct GFED cell-identity fitting.

Regional labels were used only for diagnostics/evaluation, not in the formula.

## Remaining regional/fire-regime failures
Remaining weak spots after C7:
- EURO and MIDE Spatial remain extremely low (0.083 and 0.093). These likely reflect cropland/human suppression/ignition fragmentation and land-management effects absent from the allowed inputs.
- CEAM/TENA improve but remain low Overall because spatial placement is still poor.
- EQAS improves strongly but Spatial is still only 0.286, suggesting humid-tropical fire placement needs land-use/drainage/peat/agricultural burning information not available here.
- Australia Seasonal remains low (~0.580) despite dryrate; timing likely needs wind/lightning/human ignitions or vegetation/fuel type information beyond current inputs.
- SHAF slightly worsens under C7, indicating a tradeoff between humid/tropical suppression and Southern Africa savanna spatial/magnitude behavior.

## Why remaining failures appear unresolved under current constraints
The five allowed drivers capture broad climate/productivity controls but not several known first-order controls on regional fire:
- human ignition and suppression,
- cropland/pasture land use and fragmentation,
- lightning and wind extremes,
- fuel continuity/grass fraction/canopy openness,
- peat/drainage/agricultural fire practices,
- explicit management by region.

The mechanisms tested here represent the plausible smooth global transformations available from the fixed drivers. The supported mechanisms (humid suppression and active dry-down) produce real regional gains. Additional low-dimensional variants either collapsed to identity, degraded scores, or caused regional tradeoffs. Further exploration within the same families would likely be score fitting rather than discovering a new interpretable mechanism.

## Exact output directories and reproducibility evidence
Key files:
- `scripts/explore_mechanisms.py` — candidate generation/search script.
- `candidates/C7_humid_dryrate_added_only.json` — final candidate metadata/params.
- `candidates/C7_humid_dryrate_added_only/burntArea.nc` — final candidate NetCDF.
- `final_model/params_and_metadata.json` — final accepted model metadata copy.
- `final_model/burntArea.nc` — final accepted model NetCDF copy.
- `final_model/formula.md` — final formula summary.
- `artifacts/baseline/burntArea.baseline.nc` — baseline NetCDF backup.
- `artifacts/evals/C7_humid_dryrate_added_only_output_modelC/scalar_database.csv` — official global C7 scalar database.
- `artifacts/evals/C7_humid_dryrate_added_only_output_regions_official/scalar_database.csv` — official regional C7 scalar database.
- `artifacts/evals/C7_public_trendy_firepipe_clean.log` — clean public benchmark log.
- `artifacts/evals/C6b_pann_suppress_floor0_output_regions_official/scalar_database.csv` — best regional/humid candidate evidence.
- `research_log.md`, `candidate_registry.md`, `eval_log.md`, `regional_analysis.md`, `constraint_checks.md` — persistent logs.

Current workspace state note:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc` was restored to the baseline artifact after candidate evaluation.
- Final accepted candidate is preserved in `final_model/` and `candidates/C7_humid_dryrate_added_only/` rather than silently replacing baseline.
