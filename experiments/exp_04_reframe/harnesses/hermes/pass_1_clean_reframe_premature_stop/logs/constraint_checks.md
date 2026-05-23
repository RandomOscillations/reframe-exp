# Constraint Checks

## Active constraints from program

Allowed inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files already present in this workspace

Forbidden:
- new external data as model input
- latitude/longitude hacks
- per-cell lookup tables
- named-region routing
- per-region formulas
- arbitrary residual correction coefficients
- direct cell-identity fitting to GFED
- files from prior/archive/unrelated workspaces as model evidence

## Baseline compliance

Original Model C uses one global formula with 12 parameters and only fixed allowed inputs: dbar, annual precipitation, monthly precipitation, monthly GPP, and monthly air temperature. It is compliant.

## Verification caveat

Initial `scripts/verify.py` showed generated-artifact size differences for `burntArea.nc` and `modelC_terms.nc`, but all fixed inputs and `models/C/params.json` matched. This is recorded before proceeding. Candidate evidence will be generated inside this workspace only.


## Candidate compliance checks

All Loop 1 formulas are one global function and use only allowed cell/month inputs:
- dbar (`dbar_monthly.npy`)
- annual precipitation (`p_ann_monthly.npy`)
- monthly precipitation (`p_month_monthly.npy`)
- monthly GPP (`EDv3_S3_gpp.nc`)
- monthly air temperature (`t_air_monthly.npy`)

No candidate formula uses latitude, longitude, named regions, per-cell lookup tables, new external data, region routing, or residual correction coefficients.

Evaluation uses GFED and ILAMB reference files already in the workspace, as permitted. Region masks are used only for evaluation/triage objectives in `scripts/experiment_fire_search.py`, not as model inputs.

Rejected candidates C1-C3 are not constraint violations; they are rejected scientifically because they trade weak-region improvements for unacceptable global or high-fire-region degradation.

C4 is compliant but demoted because official global Overall and clean public benchmark are worse than C0 despite a small Spatial Distribution gain.
