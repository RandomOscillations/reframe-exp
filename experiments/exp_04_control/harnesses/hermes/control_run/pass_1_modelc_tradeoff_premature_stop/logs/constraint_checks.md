# Constraint Checks

## Standing constraints
- One global formula only.
- Use only allowed in-workspace inputs:
  - `data/crujra/dbar_monthly.npy`
  - `data/crujra/p_ann_monthly.npy`
  - `data/crujra/p_month_monthly.npy`
  - `data/crujra/t_air_monthly.npy`
  - `data/trendy_v14/EDv3_S3_gpp.nc`
  - existing GFED/reference/evaluation files already present in this workspace.
- No external data as model input.
- No latitude/longitude hacks in the formula.
- No per-cell lookup tables.
- No named-region routing.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct cell-identity fitting to GFED.
- No evidence from prior experiment folders, archive folders, or unrelated local benchmark outputs.

## Baseline
Original Model C complies with the fixed input contract and one-global-formula requirement.

## Candidate search script compliance review
`scripts/run_modelC_mechanism_experiments.py`:
- Uses only allowed drivers loaded through the existing `reproduce_modelC.py` pipeline and GFED for scoring.
- Region masks are used only for diagnostic/scoring objective during search and not as model inputs or routing variables.
- Candidate formulas do not receive region labels, latitude, longitude, or cell IDs.
- Mechanism families are smooth global functions of allowed physical inputs.
- Candidate outputs are written as global TRENDY-format `burntArea.nc` artifacts under `ilamb/MODELS/<model_name>/`.

Potential caveat:
- The search objective includes regional aggregate diagnostics. This is allowed as evaluation/tuning feedback, but candidate formulas must remain global and physically interpretable. Accept/reject decisions must be based on official global/regional ILAMB plus mechanism/ablation evidence, not on proxy objective alone.
