# Program

## Objective

Start from original Model C and push the burned-area model-improvement process to a defensible stopping point.

The scientific goal is not merely to increase one scalar metric. The goal is to test whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

## Fixed Input Contract

Allowed model inputs are the existing ED autoresearch inputs in this workspace:

- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files already present in this workspace

These fields may be transformed into physically interpretable quantities.

## Formula Requirement

The final model must be one global formula. It may behave differently across cells only because allowed physical inputs imply different physical states.

Smooth ceilings, floors, saturations, humps, thresholds, piecewise functions, interactions, or regime gates are allowed if every term has a physical explanation and uses only allowed inputs.

## Required Research Loop

Run repeated outer and inner loops:

1. inspect global and regional failures,
2. explain what physical mechanism may be missing,
3. propose a unified mechanism family,
4. search or tune it with deterministic scans and/or Optuna where appropriate,
5. regenerate TRENDY-format `burntArea.nc`,
6. run official global ILAMB,
7. run official regional ILAMB or create a reproducible regional ILAMB workflow if absent,
8. run public TRENDY/firepipe only if a clean benchmark root is available inside this workspace or explicitly provided by the operator,
9. perform ablations and diagnostics,
10. accept or reject based on global, regional, public, mechanistic, and constraint evidence,
11. use the failure pattern to choose the next hypothesis.

Do not treat one Optuna/search run as exhaustion of the research process.

## Candidate Acceptance

A candidate is not acceptable unless it has:

- official global ILAMB,
- official regional ILAMB,
- public TRENDY/firepipe comparison if serious and if a clean public benchmark root is available,
- mechanistic explanation,
- constraint compliance,
- ablation or diagnostic support when feasible.

If a clean public benchmark root is unavailable, record that limitation explicitly instead of using contaminated or unrelated local benchmark outputs.

## Forbidden

Do not use:

- new external data as model input,
- latitude/longitude hacks,
- per-cell lookup tables,
- named-region routing,
- per-region formulas,
- arbitrary residual correction coefficients,
- direct cell-identity fitting to GFED,
- files from prior experiment folders or archive folders as model evidence.

## Logs

Maintain and update these files throughout:

- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`

When exploration is exhausted, write `final_report.md` with:

- best model found,
- global and regional comparisons to original Model C,
- public benchmark result if cleanly available,
- mechanisms tried,
- search details,
- ablations,
- rejected candidates and why they failed,
- constraint compliance,
- remaining failures,
- exact artifact paths for reproducibility.
