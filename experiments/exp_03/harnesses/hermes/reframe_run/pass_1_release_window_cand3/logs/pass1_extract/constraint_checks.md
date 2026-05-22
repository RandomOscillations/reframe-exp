# Constraint Checks

## Fixed input contract
Allowed inputs only:
- data/crujra/dbar_monthly.npy
- data/crujra/p_ann_monthly.npy
- data/crujra/p_month_monthly.npy
- data/crujra/t_air_monthly.npy
- data/trendy_v14/EDv3_S3_gpp.nc
- existing GFED/reference/evaluation files already present in workspace for scoring/evaluation only.

## Forbidden methods status
- New external model inputs: not used.
- Latitude/longitude hacks: not used in formulas. Latitude/cos(latitude) appears only in evaluation weighting and existing dbar construction, not as a candidate routing predictor.
- Per-cell lookup tables: not used.
- Named-region routing: not used.
- Per-region formulas: not used.
- Arbitrary residual correction coefficients: not used.
- Direct cell-identity fitting to GFED: not used.
- Prior experiment/archive evidence: not used.

## Baseline compliance
Original Model C formula uses one global multiplicative mechanistic formula with global parameters and allowed inputs only. Output is interpreted as annual rate and transformed by ED-consistent `(1-exp(-min(rate, fire_max)))/12`.

## Candidate admissibility rule for this run
A candidate can be considered serious only if it has:
- One global formula using allowed input transforms.
- Official global ILAMB run.
- Official regional ILAMB run or reproducible regional ILAMB workflow.
- Clean public TRENDY/firepipe comparison if it is a serious contender and public_benchmark_clean remains available.
- Mechanistic explanation.
- Diagnostic or ablation support.

## Current environment caveats
- `ilamb-run` is available at `.venv/bin/ilamb-run`, not on default PATH.
- Official ILAMB requires `ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb` because `ilamb/DATA` in the local root is absent/empty while the clean benchmark root contains GFED reference data.
- `scripts/run_ilamb.sh` works when invoked with `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb`.

## Continuation cycle checks
- New script scripts/explore_second_order_candidates.py uses only dbar, p_ann, p_month rolling means, t_air, and GPP rolling/current transforms as candidate predictors.
- Candidate families are one global formula with global parameters. No latitude/longitude, region identifiers, per-cell lookup tables, residual fields, direct cell identity fitting, or external inputs are used.
- GFED/reference data are used only in the screening objective and official/public evaluation, consistent with the fixed input contract.

## Continuation candidate compliance
- `scripts/explore_second_order_candidates.py`, `scripts/ablate_curing_window.py`, `scripts/explore_release_window.py`, and `scripts/explore_release_window_temp.py` were inspected/created in this workspace and use only allowed predictors/transforms: Dbar, annual precipitation, monthly precipitation rolling means where applicable, monthly GPP, and air temperature.
- Final candidate `ED-Cand3-release_window_wetcap` is one global formula with global parameters. It contains no named-region routing, no lat/lon predictors, no per-cell lookup table, no residual correction field, no direct cell-identity fitting, and no external input data.
- GFED and public benchmark files were used only for Optuna screening/evaluation and official/public ILAMB scoring, not as runtime model inputs.
- The temperature-conditioned variant was rejected at screening; no forbidden BONA-specific or region-specific mechanism was introduced to protect BONA.
