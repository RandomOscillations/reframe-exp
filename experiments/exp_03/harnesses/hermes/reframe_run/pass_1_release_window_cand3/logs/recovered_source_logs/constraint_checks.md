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
## 2026-05-18 21:42:17 continuation cycle 2: third-order mechanism design
- Re-read all user-required files before modifications: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, research_log.md, eval_log.md, regional_analysis.md, candidate_registry.md, constraint_checks.md, final_report.md. Also re-read README.md, WRITEUP.md, and models/C/formula.md.
- Current best-so-far inferred from logs: `ED-Cand3-release_window_wetcap`, official diagnostic global 0.687439 and public Overall 0.678312, with regional gains in 12/14 non-global regions but BONA -0.0120 and NHSA -0.0029.
- Carried forward failure learnings: blunt wet suppression repairs weak wet/temperate regions but loses global Spatial; fuel charging alone damages African/boreal belts; naked dbar drydown is prunable; a simple temperature activation interlock failed screening.
- New structural analogies used to define testable families: relay-protection grid (release gate with cold/short-season guard), supply-chain/F1 bottleneck synchronization (fuel, warmth, no recent rain, dryness all aligned), senescence/curing as live-fuel drawdown rather than dbar derivative, and combustion corridor balance between hyperarid fuel absence and wet-canopy nonflammability.
- Created `scripts/explore_third_order_candidates.py` with four one-global-formula families: `guarded_release`, `senescence_release`, `dual_corridor_balance`, and `warm_dry_supply_chain`. Inputs remain only dbar, annual/monthly precipitation, air temperature, and monthly GPP transforms; GFED is used only for screening.
## 2026-05-19 00:03:05 continuation cycle 2 constraint compliance
- New scripts `scripts/explore_third_order_candidates.py`, `scripts/explore_pareto_release_candidates.py`, and `scripts/ablate_pareto_guarded_corridor.py` use only allowed transformations of original Model C inputs: dbar, annual/monthly precipitation, air temperature, and monthly GPP. Annual temperature, warm-month fraction, rolling precipitation, GPP annual mean/drop, and related gates are derived from these allowed fields.
- No latitude/longitude terms, named-region routing, per-cell lookup tables, external runtime inputs, residual correction fields, or direct cell-identity fitting were introduced.
- GFED/public benchmark files were used only for Optuna screening/evaluation and ILAMB/public scoring, not as model inputs.
- `ED-Cand4Abl-no_hotboost` has official global/regional ILAMB, clean public benchmark comparison, mechanistic explanation, and ablation support. It remains a tradeoff candidate rather than a broad regional replacement because regional behavior worsens in several weak regions.

