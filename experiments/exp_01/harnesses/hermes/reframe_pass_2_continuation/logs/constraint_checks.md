# Constraint Checks Pass 2

Allowed inputs remain only:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing masks/reference/evaluation assets

Pass-2 rules:
- Continue from F3b, not original C.
- One global interpretable formula only.
- No external data, latitude/longitude hacks, named-region routing, per-cell lookup tables, per-region formulas, arbitrary residual correction coefficients, or direct GFED cell-identity fitting.

## Candidate compliance

### P2F1 curing gate

Inputs used beyond F3b: Dbar, month-to-month Dbar change derived from Dbar, current-month precipitation anomaly `P_month / (P_ann/12)`. All are allowed transformations of existing drivers.

Formula is one global smooth multiplicative gate. It uses no latitude/longitude, region ID, per-cell lookup table, external data, per-region formula, or residual correction coefficients.

### P2F2 seasonal wet inhibition

Inputs used: P_ann, P_month relative to P_ann, one-month antecedent P_month relative to P_ann, plus existing Model C/F3b drivers. All are allowed current/temporal transforms.

Formula is one global smooth wet-inhibition function. Regional labels were used only after evaluation.

### P2F3 final two-threshold arid limiter

Inputs used beyond Model C core and F3b wet suppressor:
- `deficit_ratio = Dbar / (P_ann + ratio_p0)`.
- Two global sigmoids of `deficit_ratio`.

This is compliant:
- one global formula applied identically to every grid cell/month;
- no latitude/longitude feature;
- no named-region routing;
- no per-cell or per-region coefficient;
- no external model input;
- no residual correction table;
- no direct GFED cell-identity fitting.

### P2F4 hybrid

Inputs used are the union of P2F2 and P2F3 allowed transformations. It is compliant but rejected for performance/complexity.

## Script/reproducibility compliance

- `scripts/research_fire_pass2.py` loads the pass-1 F3b incumbent from `research_candidates/F3abl_no_cool.json` even if `models/C/params.json` is overwritten by pass-2 candidates. This prevents accidental chaining from the last emitted pass-2 candidate.
- `scripts/reproduce_modelC.py` now supports original Model C, pass-1 F3b, and pass-2 two-arid-threshold schemas.
- `models/C/params.json` stores the accepted P2F3 parameters, including the retained F3b wet suppressor and the two arid thresholds.

Final P2F3 is constraint-compliant.
