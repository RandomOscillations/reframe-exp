# Final Report: Formal Base Local-Search ED Fire Model Improvement

## Executive conclusion

Best accepted model: original Model C.

Highest scalar-score trial: LAG-FUEL-v1, but rejected.

Final decision: under the fixed input contract and acceptance criteria in `program.md`, no tested unified mechanistic functional-form extension improves the model defensibly. Original Model C remains the best accepted model because the only candidate with a higher official global/public Overall score, LAG-FUEL-v1, achieves a small scalar gain mainly through Seasonal Cycle while damaging multiple official regional ILAMB scores. Other physically plausible moisture/wetness candidates improve several weak humid or temperate regions but reduce global/spatial performance and/or damage African savanna fire regimes.

The final workspace artifact is restored to original Model C:

```text
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
306b833a4aeed362d67cd510793e75e1ca9a5e2735b2ebdd0c57175bcaae1883  out_terms/modelC_terms.nc
```

Important input/reference distinction: GFED was used as reference/evaluation data and to define the existing evaluation/mask workflow in the baseline reproduction script. It was not added as a new model predictor or fitted explanatory input for any candidate functional form.

## Protocol compliance

Required files read before work:

- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`

Required live logs are present and were used as the audit trail:

- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `stuck_state.md` as supporting stuck-state documentation

This `final_report.md` is the required final stopping artifact.

The final pass in this current execution environment verified hashes of the restored artifacts. A full rerun of `scripts/verify.py` was attempted with `python3` but could not pass because this archived workspace currently lacks the raw `data/` input bundle and `.venv/` referenced by the original run commands. This does not alter the prior official ILAMB evidence already written in the output directories and logs; the final claims below are based on existing official output CSVs in this workspace and archived public benchmark CSVs.

## Model C baseline mechanism

Original Model C is a single global formula:

```text
fire(cell, month) = [
  dryness_onset(Dbar)
  * hyperarid_dryness_suppression(Dbar)
  * annual_precip_floor(P_ann)
  * monthly_precip_dampening(P_month)
  * monthly_GPP_hump(GPP_month)
  * warm_air_temperature_ignition(T_air)
]^fire_exp
```

Allowed predictive inputs used by the model are the listed CRUJRA dryness/precipitation/temperature arrays and EDv3 monthly GPP. No external data, coordinate hacks, named-region routing, per-cell lookup tables, per-region formulas, or arbitrary residual corrections were introduced.

## Candidate mechanisms explored

### 1. WET-SUPP-v1: annual wetness ceiling

Hypothesis: perhumid climates can maintain high fuel moisture and humid canopy/boundary-layer conditions that suppress combustion despite abundant fuel.

Unified functional form:

```text
wet_supp(P_ann) = 1 / (1 + (P_ann / P_wet_half)^P_wet_pow)
Model C product := Model C product * wet_supp(P_ann)
```

Search:

```text
P_wet_half in [400, 600, 800, 1000, 1250, 1500, 2000, 3000, 5000]
P_wet_pow  in [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
Best deterministic proxy: P_wet_half=3000, P_wet_pow=3.0
```

Verdict: rejected. It is mechanistically plausible and improves many humid/tropical regional scores, but official global Overall declines and NHAF/SHAF/AUST are damaged.

### 2. LAG-FUEL-v1: antecedent/cured GPP fuel

Hypothesis: burned area responds partly to prior productivity after curing, not only same-month GPP.

Unified functional form:

```text
GPP_eff = (1 - alpha) * GPP_month + alpha * mean(GPP[t-1] ... GPP[t-window])
Use GPP_eff inside the existing Model C GPP hump.
```

Search:

```text
gpp_lag_window in [1, 2, 3, 4, 6, 9, 12]
gpp_lag_alpha  in [0.25, 0.5, 0.75, 1.0]
Best deterministic proxy: gpp_lag_window=12, gpp_lag_alpha=1.0
```

Verdict: rejected as accepted model, retained as highest scalar-score trial. It improves official global Overall by +0.000745 and public benchmark Overall by +0.000740 relative to the uncontaminated baseline public run, but official regional ILAMB shows damage in TENA, EURO, MIDE, NHAF, SHAF, BOAS, CEAS, and SEAS.

### 3. LAG+WET-v1: combined antecedent fuel and wetness ceiling

Hypothesis: lagged fuel may improve seasonal phase while wetness suppression mitigates humid overprediction.

Unified functional form: simultaneous activation of WET-SUPP-v1 and LAG-FUEL-v1 at their best deterministic settings.

Verdict: rejected. It preserves some humid/tropical improvements and improves global Overall relative to baseline, but does not fix the LAG-FUEL regional-damage failure mode and has lower global Overall than pure LAG-FUEL-v1.

### 4. PRECIP-MEM-v1: antecedent precipitation moisture

Hypothesis: fuel moisture and access respond to recent rainfall memory, not only precipitation in the fire month.

Unified functional form:

```text
P_month_eff = (1 - alpha) * P_month + alpha * mean(P_month[t-1] ... P_month[t-window])
p_damp = 1 / (1 + P_month_eff / pre_dampen_half)
```

Search:

```text
precip_memory_window in [1, 2, 3, 4, 6]
precip_memory_alpha  in [0.25, 0.5, 0.75, 1.0]
Best deterministic proxy: precip_memory_window=1, precip_memory_alpha=0.25
```

Verdict: rejected. It improves many weak regions, including TENA, CEAM, NHSA, SHSA, EURO, MIDE, SEAS, EQAS, and AUST, but official global Overall declines by -0.001336, Spatial Distribution declines by -0.009597, and NHAF/SHAF are damaged.

## Official global ILAMB comparison

Scores from official global ILAMB output directories:

| Model | Status | Bias | RMSE | Seasonal | Spatial | Overall | Period Mean |
|---|---|---:|---:|---:|---:|---:|---:|
| Original Model C | best accepted/final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | 0.611164 |
| WET-SUPP-v1 | rejected | 0.729325 | 0.506214 | 0.845835 | 0.769334 | 0.671384 | 0.583389 |
| LAG-FUEL-v1 | rejected; highest scalar global | 0.727752 | 0.505788 | 0.850890 | 0.771151 | 0.672274 | 0.620074 |
| LAG+WET-v1 | rejected | 0.728988 | 0.506241 | 0.850932 | 0.768463 | 0.672173 | 0.592258 |
| PRECIP-MEM-v1 | rejected | 0.728316 | 0.506595 | 0.846707 | 0.762754 | 0.670193 | 0.582927 |

Interpretation:

- LAG-FUEL-v1 has the highest official global Overall: 0.672274 vs baseline 0.671529.
- The +0.000745 gain comes mainly from Seasonal Cycle (+0.005200).
- Bias and Spatial Distribution slightly decline for LAG-FUEL-v1.
- WET-SUPP-v1 and PRECIP-MEM-v1 confirm that moisture/wetness mechanisms can move important regional scores, but official global and spatial components do not support accepting them.

## Official regional ILAMB comparison

Regional Overall scores and deltas versus baseline:

| Region | Baseline | WET-SUPP delta | LAG-FUEL delta | LAG+WET delta | PRECIP-MEM delta |
|---|---:|---:|---:|---:|---:|
| global | 0.671529 | -0.000145 | +0.000745 | +0.000644 | -0.001336 |
| bona | 0.789806 | -0.000026 | +0.000016 | -0.000009 | -0.000449 |
| tena | 0.381473 | +0.003254 | -0.001043 | +0.002185 | +0.011514 |
| ceam | 0.376153 | +0.009207 | +0.000030 | +0.009225 | +0.011640 |
| nhsa | 0.605824 | +0.008031 | +0.000129 | +0.008154 | +0.015017 |
| shsa | 0.507249 | +0.010717 | -0.000014 | +0.010324 | +0.025846 |
| euro | 0.361128 | +0.001478 | -0.001970 | -0.000523 | +0.012152 |
| mide | 0.382769 | +0.000458 | -0.007065 | -0.006575 | +0.010737 |
| nhaf | 0.645855 | -0.001487 | -0.000398 | -0.001855 | -0.017440 |
| shaf | 0.646693 | -0.002719 | -0.000875 | -0.003575 | -0.005173 |
| boas | 0.728733 | +0.000251 | -0.000248 | +0.000010 | +0.001144 |
| ceas | 0.670499 | +0.000455 | -0.000851 | -0.000376 | +0.001800 |
| seas | 0.487193 | +0.009698 | -0.003994 | +0.005185 | +0.025434 |
| eqas | 0.507395 | +0.027613 | +0.000034 | +0.027650 | +0.011763 |
| aust | 0.670219 | -0.000805 | +0.008933 | +0.008112 | +0.010295 |

Regional interpretation:

- Baseline weak regions include EURO, CEAM, TENA, MIDE, SEAS, EQAS, and SHSA, with especially low spatial scores in CEAM, EURO, MIDE, TENA, and EQAS.
- WET-SUPP-v1 helps humid/tropical failures, especially EQAS, SHSA, SEAS, CEAM, and NHSA, but damages NHAF/SHAF/AUST and lowers global Overall.
- LAG-FUEL-v1 improves Australia and global seasonality, but damages several weak or important regions: MIDE (-0.007065), SEAS (-0.003994), EURO (-0.001970), TENA (-0.001043), CEAS (-0.000851), SHAF (-0.000875), NHAF (-0.000398), and BOAS (-0.000248).
- LAG+WET-v1 confirms the ablation: adding wetness suppression helps humid/tropical regions but does not remove LAG-FUEL damage in EURO/MIDE/African regions.
- PRECIP-MEM-v1 is the strongest diagnostic for many weak regions, but at unacceptable cost to NHAF (-0.017440), SHAF (-0.005173), and global Spatial Distribution.

## Public TRENDY/firepipe benchmark comparison

Uncontaminated baseline public output:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-13_181113__ed_fire_exp01_hermes_base_prompt_completed_run/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-baseline-formal`

Serious candidate public output:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-13_181113__ed_fire_exp01_hermes_base_prompt_completed_run/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-pure-v1`

Known caveats:

- JSBACH hit the documented public benchmark `IndexError`; this was already logged and does not invalidate completed comparisons.
- The public benchmark wrapper symlinked model files. During the LAG-FUEL public run, the `ED-ModelC-baseline-formal` symlink pointed at the current candidate file, so that candidate-run baseline row is contaminated. The uncontaminated baseline score is from the baseline public output directory.

Public ranking evidence:

| Rank | Model | Public Overall | Notes |
|---:|---|---:|---|
| 1 | ED-ModelC-lag-fuel-pure-v1 | 0.672014 | highest public scalar trial; rejected by official regional criteria |
| 1/2 | Original Model C baseline | 0.671274 | uncontaminated baseline public run; ranked #1 before rejected candidate |
| 3 | CLASSIC | 0.666048 | comparator |
| 4 | CLM6.0 | 0.660644 | comparator |
| 5 | CLM-FATES | 0.656831 | comparator |
| 6 | ELM-FATES | 0.656788 | comparator |
| 7 | JULES-ES | 0.590519 | comparator |
| 8 | ELM | 0.556381 | comparator |
| 9 | VISIT-UT | 0.554455 | comparator |
| 10 | LPJmL | 0.548547 | comparator |
| 11 | LPJ-GUESS | 0.479233 | comparator |
| 12 | EDv3 | 0.477410 | comparator |
| 13 | LPJ-EOSIM | 0.463542 | comparator |

Public conclusion: LAG-FUEL-v1 is scalar rank #1 in the public benchmark, but this is insufficient for acceptance because official regional ILAMB reveals hidden damage.

## Constraint compliance

All serious candidates:

- used only allowed existing drivers (`P_ann`, `P_month`, monthly GPP, dryness, temperature) already within the workspace input contract;
- did not add external model inputs;
- did not use latitude/longitude hacks;
- did not use per-cell lookup tables;
- did not use named-region routing;
- did not use per-region formulas;
- did not add arbitrary residual correction coefficients;
- retained one global functional form with smooth, physically motivated operations;
- had official global ILAMB;
- had official regional ILAMB;
- had public TRENDY/firepipe comparison when serious as a best scalar candidate;
- had ablation/diagnostic support where feasible.

GFED reference/evaluation data was not used as a new model predictor or direct fitted explanatory input.

## Why no candidate is accepted

The protocol explicitly rejects accepting a candidate merely because one global scalar score improves. A candidate must improve or preserve regional behavior defensibly.

LAG-FUEL-v1 fails this test:

- Official global Overall improves only +0.000745.
- Improvement is concentrated in Seasonal Cycle.
- Bias and Spatial Distribution decline slightly.
- Official regional Overall declines in multiple weak/important regions, notably MIDE, SEAS, EURO, TENA, CEAS, SHAF, NHAF, and BOAS.

WET-SUPP-v1 and PRECIP-MEM-v1 fail differently:

- They provide diagnostic evidence that humid/tropical/temperate failures respond to moisture and wetness mechanisms.
- However, they introduce global/spatial loss and African savanna damage, especially NHAF/SHAF.

LAG+WET-v1 fails as an ablation/combination:

- It confirms that the candidate effects are not simply complementary missing mechanisms.
- It still leaves regional damage and does not beat LAG-FUEL-v1 globally.

Thus, original Model C remains the only model that is both fully evaluated and acceptable under the multidimensional criteria.

## Remaining failures and likely causes

Remaining regional/fire-regime failures:

- Low Spatial Distribution in CEAM, EURO, MIDE, TENA, and EQAS.
- Sensitivity of African savanna regimes, especially NHAF and SHAF, to moisture-memory or wetness suppression changes.
- Persistent trade-off between humid/tropical corrections and savanna/global spatial realism.
- Australia improves under lagged fuel and precipitation memory, but those same changes hurt other regions.
- Bias/period-mean tension remains: suppressing humid overprediction often lowers period mean or spatial variance in ways penalized by ILAMB.

Likely missing processes under current constraints:

- vegetation/fuel type and continuity,
- human ignition/suppression,
- land use and fragmentation,
- cropland/pasture management,
- grazing,
- lightning/ignition climatology,
- sub-grid fuel structure.

These processes cannot be added as model inputs in this run. Under the allowed inputs, the same smooth variables must explain both humid tropical suppression and high-flammability savanna behavior. The official regional evidence indicates these regimes demand opposing adjustments that cannot be separated cleanly without forbidden region routing, external predictors, coordinate hacks, lookup tables, or arbitrary residual corrections.

## Defensible stopping rationale

The local search covered the most plausible unified, smooth, mechanistic extensions available from the existing input contract:

1. high annual precipitation wetness suppression;
2. antecedent/cured productivity fuel;
3. combined antecedent fuel plus wetness suppression;
4. antecedent precipitation/fuel-moisture memory.

The explored candidates do not move the model toward a clearly better global/regional optimum. Instead, they reveal a trade-off surface:

- moisture/wetness memory improves humid and several weak regions but harms African savanna and global spatial performance;
- lagged fuel improves seasonal phase and Australia but damages MIDE/EURO/SEAS/TENA and other regions;
- combining gates redistributes, rather than resolves, the damage.

Additional parameter tuning around these forms is likely to interpolate among already observed trade-offs. Pure hyperparameter fitting without a new mechanism is disallowed. More complex routing-like forms would risk violating the global-formula and no-region-routing constraints.

Therefore, constrained exploration is exhausted for this formal base local-search phase.

## Final answer

Final accepted model: original Model C.

Final rejected scalar-best trial: LAG-FUEL-v1.

Reason for final choice: original Model C is the only fully evaluated, constraint-compliant model that does not achieve its score by hiding regional damage. LAG-FUEL-v1 improves global/public Overall slightly but fails the official regional acceptance criterion. WET-SUPP-v1, LAG+WET-v1, and PRECIP-MEM-v1 provide useful mechanistic diagnostics but do not satisfy the combined global/regional criteria.

Required final artifact written: `final_report.md`.
