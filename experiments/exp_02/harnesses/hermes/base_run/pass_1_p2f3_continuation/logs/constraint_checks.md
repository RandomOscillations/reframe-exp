# Constraint Checks

## Allowed inputs used
All continuation candidates use only the fixed workspace inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- Existing masks/reference data only for baseline-compatible reproduction and evaluation.

Derived quantities used:
- `p_month/(p_ann/12)` precipitation concentration.
- liquid-precipitation proxy from `p_month * sigmoid(T_air)`.
- annual thermal gate from monthly `T_air`.
- annual wet-canopy suppressor from `P_ann`.
- arid fuel-continuity deficit ratio `Dbar/(P_ann + ratio_p0)`.

## Disallowed shortcuts not used
- No new external data as model input.
- No latitude/longitude terms in formulas.
- No named-region IDs or named-region routing.
- No per-cell lookup tables.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct fitting to GFED by cell identity.

Regional labels were used only for official ILAMB evaluation and post-hoc diagnostics, never in the formula.

## Accepted formula compliance

Accepted P2F3 formula:
```text
base_rate = original Model C annual rate after fire_exp
wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)
deficit_ratio = Dbar / (P_ann + ratio_p0)
arid_soft = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)
fire_rate = base_rate * wet_suppress * arid_soft * arid_desert
burntArea_month = (1 - exp(-min(fire_rate, FIRE_MAX_RATE))) / 12
```

This is one global, smooth, interpretable formula. It acts differently by climate/fuel regime only through allowed physical inputs, not through region/cell identity.

## Ablation support

- Full P2F3: official global Overall 0.677073.
- No low/soft arid threshold: 0.676981. Nearly as good and more spatially conservative, but weaker dryland target gains.
- No high/desert threshold: 0.676040. High threshold is important.
- Optuna refinement: 0.676764. Seeded mechanistic candidate remains best official global/regional compromise.

## Final state

The accepted candidate is stored in isolated artifacts rather than overwriting the verified baseline:
- `runs/candidates/p2f3_seed_current/params.json`
- `runs/candidates/p2f3_seed_current/burntArea.nc`

The baseline `models/C/params.json` and `ilamb/MODELS/ED-ModelC-final/burntArea.nc` remain unchanged for reproducible comparison.
