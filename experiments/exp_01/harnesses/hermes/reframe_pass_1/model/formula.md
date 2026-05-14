# Model C+ — Pruned Global Wet/Arid Limiter Candidate

Final accepted candidate from this research run: original Model C multiplied by two smooth global suppressors.

Official global ILAMB Overall Score: 0.676543 (candidate F3b/no-cool; official regional run `ilamb/output_F3b_no_cool_regions`).
Public TRENDY/firepipe Overall Score: 0.676313, rank #1 in the local public benchmark run `ilamb/output_with_ED-ModelC-formal-candidate`.

## Formula

Original Model C core:

```
base_fire(cell, month) =
    [ onset(Dbar) * suppress(Dbar)
    * precip_floor(P_ann) * precip_dampen(P_month)
    * gpp_hump(GPP_month)
    * air_temp_ign(T_air)
    ]^fire_exp
```

Final pruned candidate:

```
deficit_ratio = Dbar / (P_ann + ratio_p0)

wet_suppress  = 1 - wet_amp  * sigmoid(P_ann,        wet_k,   wet_c)
arid_suppress = 1 - arid_amp * sigmoid(deficit_ratio, arid_k,  arid_c)

fire_rate_yr = base_fire * wet_suppress * arid_suppress

burntArea_month = (1 - exp(-min(fire_rate_yr, FIRE_MAX_RATE))) / 12
```

The searched cool suppressor was ablated because removing it changed official global Overall only from 0.676544 to 0.676543 and did not materially change the regional pattern.

## Mechanistic interpretation

Model C already captures ignition onset, hyperarid suppression, precipitation fuel supply, current-rain quenching, productivity hump, and temperature ignition. Its largest regional failures were not seasonal phase but overprediction in low-fire regions and wet/cool/arid regimes.

The final candidate adds two missing global limiters:

1. Wet/canopy-moisture inhibition
   - At high annual precipitation, rainfall no longer only indicates fuel supply; it also indicates persistently moist fuels, closed canopies, and poor curing.
   - Structural analogy: a chemical reactor with substrate supply and product inhibition. Some water grows fuel; too much water inhibits combustion.

2. Hyperarid fuel-discontinuity inhibition by Dbar / (P_ann + ratio_p0)
   - Dryness alone is not sufficient for fire when rainfall/fuel continuity is too low. The dryness-to-rainfall ratio distinguishes burnable seasonal drylands from deserts or highly discontinuous fuels.
   - Structural analogy: percolation/epidemic thresholds. Spread needs a connected susceptible/fuel network, not only an ignition source.

Both terms are global smooth functions of allowed inputs. There is no region routing, latitude/longitude feature, cell lookup, or residual correction.

## Final suppressor parameters

```
wet_amp   = 0.8844066447148519
wet_k     = 0.03746225268483959
wet_c     = 1733.7962048788854
ratio_p0  = 76.48116496519896
arid_amp  = 0.7463784815617368
arid_k    = 1.8318106083501675
arid_c    = 4.018565692385908
cool_amp  = 0.0  # ablated/pruned
```

Original Model C core parameters are preserved in `models/C/params.BASELINE-before-research.json` and loaded by `scripts/reproduce_modelC.py` when `models/C/params.json` stores the pruned candidate schema.
