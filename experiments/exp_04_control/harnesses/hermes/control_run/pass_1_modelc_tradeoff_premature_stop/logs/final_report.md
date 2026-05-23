# Final Report — Model C Fire-Model Improvement Run

## Executive conclusion

The defensible stopping point for this workspace is: keep original/reproduced Model C as the final model.

Original Model C remains the best official global ILAMB model found in this run:

| Model | Bias | RMSE | Seasonal | Spatial | Official global Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| ED-ModelC-temp_window | 0.725506 | 0.511461 | 0.841213 | 0.706360 | 0.659200 |
| ED-ModelC-fuel_moisture_balance | 0.731075 | 0.511184 | 0.839058 | 0.693227 | 0.657146 |
| ED-ModelC-humid_suppression | 0.718573 | 0.505759 | 0.829925 | 0.686248 | 0.649253 |
| ED-ModelC-base_refit | 0.722189 | 0.507389 | 0.834902 | 0.668848 | 0.648144 |
| ED-ModelC-precip_shape | 0.715627 | 0.509039 | 0.841352 | 0.656438 | 0.646299 |

The search did find real regional tradeoff candidates. In particular, precipitation-shape and fuel-moisture-balance mechanisms improved regional diagnostic means or worst-region scores. But none produced the required step-function global + regional improvement. Every regional-improving candidate paid a large official global penalty, primarily through degraded spatial distribution and/or seasonal score.

Therefore no modified candidate is acceptable as the final model under the stated acceptance criteria. The best global model is original Model C; the best regional-diagnostic alternatives are recorded but rejected as replacements.

## Workspace and constraint compliance

I worked inside:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_04-control/hermes/control`

Required files read before model changes:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `README.md`
- `WRITEUP.md`
- `models/C/formula.md`

Constraints followed:
- One global formula for each candidate.
- No external model inputs.
- No latitude/longitude formula hacks.
- No per-cell lookup tables.
- No named-region routing.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct cell-identity fitting to GFED.
- No prior experiment folders or archive outputs used as evidence.

Regional masks were used only for evaluation and search-objective diagnostics, never as model inputs.

## Baseline reproduction

Before changing model code or parameters, I ran:

1. `.venv/bin/python scripts/verify.py`
2. `.venv/bin/python scripts/reproduce_modelC.py`
3. `PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh`
4. Official regional ILAMB over GFED regions.

`verify.py` initially reported size/hash mismatches for generated NetCDF artifacts only:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- `out_terms/modelC_terms.nc`

All fixed input data and `models/C/params.json` were OK. I recorded the mismatch before proceeding and regenerated `burntArea.nc` from original Model C.

Baseline reproduction diagnostics from `scripts/reproduce_modelC.py`:
- land cells: 13826 / 64800
- raw rate land-mean: 0.09018 yr^-1
- max raw rate: 0.9987 yr^-1
- ED-transformed land-mean: 0.00610759
- GFED land-mean: 0.00298745
- ratio: 2.044

Official baseline global ILAMB:
- Output: `ilamb/output_modelC/scalar_database.csv`
- Bias Score: 0.728089000000
- RMSE Score: 0.505759000000
- Seasonal Cycle Score: 0.845690000000
- Spatial Distribution Score: 0.772351000000
- Overall Score: 0.671529000000

## Baseline regional triage

Official regional ILAMB was run over ILAMB's built-in GFED regions:
`bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust`

Output:
`ilamb/output_modelC_regions/scalar_database.csv`

ILAMB emitted regional component scores but no regional `Overall Score`. I therefore used the same tier-2 style diagnostic formula `(2*Bias + 2*RMSE + Seasonal + Spatial)/6` only for triage. Official regional component scores remain the primary evidence.

Weakest baseline regions by derived diagnostic:

| Region | Bias | RMSE | Seasonal | Spatial | Derived diagnostic |
|---|---:|---:|---:|---:|---:|
| ceam | 0.286887 | 0.310422 | 0.847470 | 0.125564 | 0.361275 |
| euro | 0.393450 | 0.261763 | 0.808165 | 0.080499 | 0.366842 |
| tena | 0.437076 | 0.307975 | 0.694036 | 0.160304 | 0.390740 |
| mide | 0.436689 | 0.310067 | 0.765840 | 0.091179 | 0.391755 |
| seas | 0.496169 | 0.377266 | 0.826697 | 0.358569 | 0.488689 |
| shsa | 0.473091 | 0.429758 | 0.820024 | 0.383616 | 0.501556 |
| eqas | 0.477132 | 0.523149 | 0.836452 | 0.177092 | 0.502034 |

Pattern:
- Model C is globally strong because large-fire regions and global seasonal cycle are well represented.
- Failures concentrate in low-fire or spatially heterogeneous regions: CEAM, EURO, TENA, MIDE.
- Humid/monsoon tropical regions have spatial allocation issues: EQAS, SEAS.
- Australia has good magnitude/spatial behavior but weaker seasonality.

## Mechanism families tried

I implemented and searched five candidate families in:
`scripts/run_modelC_mechanism_experiments.py`

Each family was a single global formula using only allowed fields.

1. `base_refit`
   - Same Model C formula.
   - Purpose: determine whether regional failures can be improved by retuning only.
   - Search: 500 Optuna trials.

2. `precip_shape`
   - Adds global exponents on annual precipitation floor and monthly precipitation dampening.
   - Mechanistic idea: precipitation controls may be too rigid; fire response to fuel-building annual rainfall and fire-suppressing monthly rainfall may need nonlinear elasticity.
   - Search: 500 Optuna trials.

3. `temp_window`
   - Adds high-temperature suppression on top of warm-temperature ignition.
   - Mechanistic idea: very hot conditions may correspond to fuel-limited or physiological-stress regimes where ignition likelihood alone overpredicts burning.
   - Search: 500 Optuna trials.

4. `humid_suppression`
   - Adds smooth annual-precipitation humid/fuel-moisture suppression.
   - Mechanistic idea: persistently humid, high-precipitation regions may remain too wet despite monthly rainfall dampening and GPP hump.
   - Search: 500 Optuna trials.

5. `fuel_moisture_balance`
   - Adds smooth dryness relief of monthly rainfall dampening.
   - Mechanistic idea: the same monthly rainfall amount should suppress less in cells with accumulated dryness than in persistently humid cells.
   - Search: 500 Optuna trials.

Total search: 2500 Optuna trials across five mechanism families.

Search artifacts:
- `experiments/modelC_mechanism_search/summary.json`
- candidate JSON files under `experiments/modelC_mechanism_search/*.json`
- candidate NetCDF files under `ilamb/MODELS/ED-ModelC-*/burntArea.nc`

## Official candidate evaluation

Official global ILAMB output:
`ilamb/output_candidates_global_full/scalar_database.csv`

Official regional ILAMB output:
`ilamb/output_candidates_regions/scalar_database.csv`

Parsed score tables:
- `experiments/modelC_mechanism_search/official_global_scores.csv`
- `experiments/modelC_mechanism_search/official_regional_scores.csv`

No candidate beat original Model C globally.

Regional diagnostic summary from official regional component scores:

| Model | Mean regional diagnostic | Min | Max | Decision |
|---|---:|---:|---:|---|
| ED-ModelC-precip_shape | 0.615108 | 0.357003 | 0.782779 | Rejected: best regional mean, but global Overall fell to 0.646299. |
| ED-ModelC-humid_suppression | 0.601833 | 0.347296 | 0.728462 | Rejected: regional gains, but global Overall fell to 0.649253. |
| ED-ModelC-fuel_moisture_balance | 0.594038 | 0.421151 | 0.701360 | Rejected: best worst-region repair, but global Overall fell to 0.657146. |
| ED-ModelC-base_refit | 0.590194 | 0.403365 | 0.726535 | Rejected: refit tradeoff, global Overall fell to 0.648144. |
| ED-ModelC-temp_window | 0.589537 | 0.364386 | 0.775945 | Rejected: closest global candidate, but still below baseline at 0.659200. |
| ED-ModelC-final | 0.560591 | 0.361275 | 0.805502 | Accepted as final: best official global model. |

Best-by-region diagnostics were split:
- Original Model C remained best for BONA, NHAF, SHAF.
- `precip_shape` helped BOAS, EQAS, EURO, SEAS, SHSA.
- `humid_suppression` helped AUST, CEAM, NHSA.
- `fuel_moisture_balance` helped MIDE and TENA.

This is the central result of the run: different regions prefer different physical modifications, but no single global modification improved both the official global benchmark and regional behavior enough to justify replacing Model C.

## Ablations and diagnostics

Ablation script:
`scripts/run_proxy_ablations.py`

Output:
`experiments/modelC_mechanism_search/proxy_ablation_scores.csv`

Proxy ablations neutralized the added term within each fitted candidate while keeping the refit parameters. They were used as diagnostic support for rejection, not as official acceptance evidence.

Findings:
- `precip_shape`: neutralizing precipitation exponents had almost no proxy objective effect, so the official regional gain is not cleanly attributable to the added exponent mechanism alone.
- `temp_window`: high-temperature suppression improved proxy global spatial but did not improve regional robustness enough; official global score stayed below Model C.
- `humid_suppression`: added humid suppression improved proxy global spatial but slightly worsened regional mean/min relative to its neutralized refit.
- `fuel_moisture_balance`: added dryness relief improved proxy global spatial, but regional mean/min were not clearly better than the neutralized refit.

Conclusion from ablations: the regional gains mostly reflect a tradeoff frontier exposed by refitting and regional weighting, not a clean, robust, interpretable step-function mechanism over Model C.

## Public TRENDY/firepipe comparison

Clean public benchmark root was available and used:
`public_benchmark_clean`

Command:
`MODEL_NAME=ED-ModelC-final-reproduced SRC="$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe_clean.sh`

Output:
`public_benchmark_clean/ilamb/output_with_ED-ModelC-final-reproduced/scalar_database.csv`

Top public comparison results:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-baseline | 0.734518 | 0.509637 | 0.849154 | 0.772477 | 0.675085 |
| ED-ModelC-final-reproduced | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.671274 |
| CLASSIC | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.666048 |
| CLM6.0 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.660644 |
| CLM-FATES | 0.725026 | 0.525205 | 0.801922 | 0.706800 | 0.656831 |
| ELM-FATES | 0.724021 | 0.511529 | 0.860476 | 0.676384 | 0.656788 |

The public run reported a JSBACH pair `IndexError`, but post-processing completed and scalar outputs were produced. The reproduced final Model C remains ahead of public comparator models CLASSIC and CLM6.0 in this clean benchmark run. The clean root's pre-existing `ED-ModelC-baseline` artifact scores slightly higher than the regenerated `ED-ModelC-final-reproduced`; I did not use that external-root artifact as a replacement model for this workspace, but recorded it as public benchmark context.

## Why no replacement was accepted

A candidate was required to have:
- official global ILAMB,
- official regional ILAMB,
- public TRENDY/firepipe comparison if serious,
- mechanistic explanation,
- constraint compliance,
- ablation or diagnostic support when feasible.

The modified candidates satisfy the formula/input compliance requirement and received official global/regional ILAMB, but they fail the scientific acceptance criterion: none improves global fit and regional behavior together. Regional gains are real but accompanied by a large global Overall drop of roughly 0.012 to 0.025.

The strongest conclusion is that Model C is close to the ceiling for a formula using only:
- dryness accumulator,
- annual precipitation,
- monthly precipitation,
- monthly air temperature,
- monthly GPP.

The remaining failures appear to require information not present in the fixed input contract, especially:
- land cover / vegetation type / fire type,
- cropland and pasture management,
- human ignition and suppression,
- lightning ignition,
- fuel continuity/fragmentation,
- explicit woody/herbaceous fuel structure,
- regionally varying observation/reporting or management effects.

Those variables could explain why CEAM, EURO, TENA, MIDE, EQAS, SEAS, and AUST prefer different corrections. Encoding those differences without new inputs would require forbidden named-region routing, lat/lon hacks, or residual correction.

## Best models by use case

- Best official global model: `ED-ModelC-final`
  - Official global Overall: 0.671529
  - Artifact: `ilamb/MODELS/ED-ModelC-final/burntArea.nc`

- Best regional-mean diagnostic candidate: `ED-ModelC-precip_shape`
  - Derived regional mean: 0.615108
  - Official global Overall: 0.646299
  - Artifact: `ilamb/MODELS/ED-ModelC-precip_shape/burntArea.nc`
  - Not accepted because global loss is too large.

- Best worst-region diagnostic candidate: `ED-ModelC-fuel_moisture_balance`
  - Derived regional min: 0.421151
  - Official global Overall: 0.657146
  - Artifact: `ilamb/MODELS/ED-ModelC-fuel_moisture_balance/burntArea.nc`
  - Not accepted because global loss is too large.

- Closest modified global candidate: `ED-ModelC-temp_window`
  - Official global Overall: 0.659200
  - Artifact: `ilamb/MODELS/ED-ModelC-temp_window/burntArea.nc`
  - Not accepted because it remains clearly below Model C and does not provide a regional step-function improvement.

## Reproducibility artifacts

Logs maintained:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `decision_trace.md`

Core scripts added:
- `scripts/run_modelC_mechanism_experiments.py`
- `scripts/summarize_official_candidates.py`
- `scripts/run_proxy_ablations.py`

Important outputs:
- `ilamb/output_modelC/scalar_database.csv`
- `ilamb/output_modelC_regions/scalar_database.csv`
- `ilamb/output_candidates_global_full/scalar_database.csv`
- `ilamb/output_candidates_regions/scalar_database.csv`
- `experiments/modelC_mechanism_search/summary.json`
- `experiments/modelC_mechanism_search/official_global_scores.csv`
- `experiments/modelC_mechanism_search/official_regional_scores.csv`
- `experiments/modelC_mechanism_search/proxy_ablation_scores.csv`
- `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-reproduced/scalar_database.csv`

Final selected model artifact:
`ilamb/MODELS/ED-ModelC-final/burntArea.nc`

Final decision: retain original Model C. Exploration is exhausted for the tested constrained mechanism families because all interpretable global extensions that improved regional diagnostics produced unacceptable official global losses, and the remaining regional failures likely require forbidden or unavailable explanatory variables under the fixed input contract.
