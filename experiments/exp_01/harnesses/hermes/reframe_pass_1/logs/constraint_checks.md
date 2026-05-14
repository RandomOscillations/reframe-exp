# Constraint Checks

## Global constraints from program/manifest

Allowed inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- Existing masks/reference/evaluation assets

Disallowed:
- external model inputs
- latitude/longitude hacks
- named-region routing or per-region formulas
- per-cell lookup tables
- arbitrary residual correction coefficients
- direct fitting to GFED by cell identity

## Baseline C0

- Uses only allowed inputs: yes.
- One global formula: yes.
- No named-region routing/per-region formulas: yes.
- No external data: yes.
- No per-cell lookup/residual correction: yes.

## Candidate families checked

### F1 antecedent fuel / wet-dry pulse
- Inputs: allowed GPP, Dbar, P_ann, P_month temporal summaries.
- Formula: one global smooth multiplicative term.
- Region routing/cell lookup: no.
- Decision: rejected because best search ablated back to baseline.

### F2 precipitation window
- Inputs: P_ann only beyond Model C core.
- Formula: one global smooth high-precipitation suppressor.
- Region routing/cell lookup: no.
- Decision: rejected as standalone.

### F3/F3b final wet/arid suppressors
- Inputs beyond Model C core:
  - P_ann in wet suppressor.
  - Dbar / (P_ann + ratio_p0) in arid fuel-discontinuity suppressor.
- Formula: one global formula applied identically to every cell/month.
- Region labels used in formula: no.
- Latitude/longitude used in formula: no.
- Per-cell/per-region coefficients: no.
- External data inputs: no.
- Residual correction: no; terms are mechanistic limiters, not residual tables.
- Evaluation used regional masks only post hoc for diagnostics and official scoring.

Final F3b formula is compliant.

## Reproducibility state

- `models/C/params.json` stores final pruned F3b suppressor parameters.
- `models/C/params.BASELINE-before-research.json` preserves the original Model C core parameters.
- `scripts/reproduce_modelC.py` was updated to reproduce either original Model C-style parameter files or the final suppressor schema.
- Current final output file: `ilamb/MODELS/ED-ModelC-final/burntArea.nc`.
