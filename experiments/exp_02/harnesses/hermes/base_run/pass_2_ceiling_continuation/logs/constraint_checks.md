# Constraint Checks

## Allowed inputs used

All continuation candidates use only the fixed workspace inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- Existing masks/reference data only for baseline-compatible reproduction and evaluation.

Derived quantities used across the run:
- `p_month/(p_ann/12)` precipitation concentration.
- liquid-precipitation proxy from `p_month * sigmoid(T_air)` in rejected tests.
- annual thermal gate from monthly `T_air`.
- temperature amplitude from monthly `T_air` climatology.
- annual wet-canopy suppressor from `P_ann`.
- arid fuel-continuity deficit ratio `Dbar/(P_ann + ratio_p0)`.
- dbar tendency `Dbar[t] - Dbar[t-1]` for drying/curing phase.

## Disallowed shortcuts not used

- No new external data as model input.
- No latitude/longitude terms in formulas.
- No named-region IDs or named-region routing.
- No per-cell lookup tables.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct fitting to GFED by cell identity.

Regional labels were used only for official ILAMB evaluation and post-hoc diagnostics, never in the formula.

## Final accepted continuation formula compliance

Accepted final model: `ED-next-curing-hotwet-1`, stored as `runs/candidates/p2f3_curing_hotwet_final/`.

Formula summary:
```text
base_rate = original Model C annual rate after fire_exp

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)
deficit_ratio = Dbar / (P_ann + ratio_p0)
arid_soft   = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)
P2F3_rate = base_rate * wet_suppress * arid_soft * arid_desert

drying = sigmoid(Dbar[t] - Dbar[t-1], drying_k, drying_c)
drymonth = 1 / (1 + (p_month/(P_ann/12) / pconc_half)^pconc_pow)
warm_month = sigmoid(T_air, temp_k, temp_c)
curing = drying * drymonth * warm_month

wetmonth = sigmoid(p_month/(P_ann/12), wet_k_month, wet_c_month)
warm_climate_gate = sigmoid(T_air_annual_climatology, warm_k, warm_c)

fire_rate = P2F3_rate * (1 + cure_amp * curing) *
            (1 - wet_amp_month * wetmonth * warm_climate_gate)

burntArea_month = (1 - exp(-min(fire_rate, FIRE_MAX_RATE))) / 12
```

This is one global, smooth, interpretable formula. It acts differently by climate/fuel/moisture regime only through allowed physical inputs, not through region/cell identity.

## Final accepted parameters

From `runs/candidates/p2f3_curing_hotwet_final/params.json`:
```text
P2F3 core:
wet_amp    = 0.8844066447148519
wet_k      = 0.03746225268483959
wet_c      = 1733.7962048788854
ratio_p0   = 10.550923117584711
arid_amp1  = 0.09765875631019073
arid_k1    = 8.862392037192233
arid_c1    = 0.8190773026156323
arid_amp2  = 0.872802820380493
arid_k2    = 1.2991349033470558
arid_c2    = 5.00184048998816

Curing/hotwet continuation:
drying_k    = 0.151909755193002
drying_c    = 71.10327035972242
pconc_half  = 0.17733668059544083
pconc_pow   = 3.6607083389419017
temp_k      = 0.5483001798421393
temp_c      = 6.554353498957058
cure_amp    = 1.5049730144952744
wet_k_month = 1.9603357957179453
wet_c_month = 0.6295980601621034
wet_amp_month = 0.65
warm_k      = 0.5
warm_c      = 8
warm_floor  = 0.0
```

## Ablation/diagnostic support

- P2F3 full: official global 0.677073; public 0.676846. Broad weak-region gains; previous best.
- Cold continental relaxation: 0.676930. Slight BONA/BOAS relief but no global improvement; rejected.
- Pure curing phase: 0.684534. Major global/AUST/spatial improvement with BONA/BOAS preserved; revealed real missing mechanism.
- Pure curing amplitude scans: 0.680952 at 0.35x, 0.684994 at 1.25x. Stronger curing raises global but worsens some weak regions, so curing alone is not fully balanced.
- Curing + ungated wet compensation: 0.688603 official and 0.688384 public, but BONA/BOAS spatial damage; rejected despite top scalar.
- Accepted hot/warm-gated wet compensation: 0.687626 official and 0.687405 public, while preserving BONA/BOAS near P2F3.

## Final state

The final accepted continuation candidate is isolated under:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`

The baseline `models/C/params.json`, the previous P2F3 artifacts, and archived `pass_1_artifacts` were not modified.
