# Constraint Checks

## Allowed inputs used

All candidates use only the fixed workspace inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- Existing masks/reference data only for baseline-compatible reproduction and evaluation.

Derived quantities used across the run:
- `p_month/(p_ann/12)` precipitation concentration.
- annual T_air climatology and T_air amplitude.
- annual wet-canopy suppressor from `P_ann`.
- arid fuel-continuity deficit ratio `Dbar/(P_ann + ratio_p0)`.
- dbar tendency `Dbar[t] - Dbar[t-1]` for drying/curing phase.
- wet/productive gates from allowed P_ann and GPP.

## Disallowed shortcuts not used

- No new external data as model input.
- No latitude/longitude terms in formulas.
- No named-region IDs or named-region routing.
- No per-cell lookup tables.
- No per-region formulas.
- No arbitrary residual correction coefficients.
- No direct fitting to GFED by cell identity.

Regional labels were used only for official ILAMB evaluation and post-hoc diagnostics, never in formulas.

## Final balanced formula compliance

Final balanced model retained after loop 13: `ED-next-curing-hotwet-1`, stored as `runs/candidates/p2f3_curing_hotwet_final/`.

Formula summary:
```text
base_rate = original Model C annual rate after fire_exp
P2F3_rate = base_rate * wet_canopy_suppress(P_ann) * arid_soft(Dbar/P_ann) * arid_desert(Dbar/P_ann)

curing = sigmoid(Dbar[t]-Dbar[t-1]) * drymonth(p_month/(P_ann/12)) * warm_month(T_air)
wetmonth = sigmoid(p_month/(P_ann/12))
warm_climate_gate = sigmoid(T_air_annual_climatology)

fire_rate = P2F3_rate * (1 + cure_amp * curing) * (1 - wet_amp_month * wetmonth * warm_climate_gate)
burntArea_month = (1 - exp(-min(fire_rate, FIRE_MAX_RATE))) / 12
```

This is one global, smooth, interpretable formula. It acts differently by climate/fuel/moisture regime only through allowed physical inputs, not through region/cell identity.

## Loop 13 rejected formula compliance

Loop 13 candidates also complied with the input contract. They added only:
- cold/high-amplitude gates derived from T_air climatology,
- arid-deficit curing attenuation from `Dbar/(P_ann+p0)`,
- wet/productivity curing attenuation from `P_ann` and GPP.

They were rejected for regional tradeoffs, not for constraint violations.

## Ablation/diagnostic support

- P2F3 full: official 0.677073; public 0.676846. Broad weak-region gains; regional-broad alternate.
- ED-next-curing-hotwet-1: official 0.687626; public 0.687405. Best balanced accepted model.
- ED-next-curing-warmwet-nowarmgate: official 0.688603; public 0.688384. Rejected due BONA/BOAS damage.
- ED-loop13-combined: official 0.690564; public 0.690353. Rejected due BONA/BOAS damage.
- ED-loop13-aridatt: official 0.690378; public 0.690170. Rejected due BONA/BOAS collapse and AUST regression.
- ED-loop13-aridboreal-5: official 0.690073; public 0.689864. Boreal protection partially helps but still not balanced.
- ED-loop13-borealdiag: official 0.688133. Marginal global gain; not a step and BONA below hotwet-1.

## Final state

The final accepted balanced candidate remains isolated under:
- `runs/candidates/p2f3_curing_hotwet_final/params.json`
- `runs/candidates/p2f3_curing_hotwet_final/burntArea.nc`

Highest scalar rejected candidate:
- `runs/candidates/loop13_combined_protect_attenuate_opt300/params.json`
- `runs/candidates/loop13_combined_protect_attenuate_opt300/burntArea.nc`

The baseline `models/C/params.json`, previous P2F3 artifacts, `pass_1_artifacts`, and `pass_2_artifacts` were not modified.
