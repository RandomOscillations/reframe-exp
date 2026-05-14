# Model C++ — Pass-2 Two-Threshold Global Arid Fuel-Continuity Candidate

Final accepted pass-2 candidate: original Model C core multiplied by the pass-1 F3b wet/canopy suppressor and a refined two-threshold global arid fuel-continuity limiter.

Official global ILAMB Overall Score: 0.677073 (candidate P2F3; official regional run `ilamb/output_P2F3_arid_two_threshold_regions`).
Public TRENDY/firepipe Overall Score: 0.676846, rank #1 in the local public benchmark run `ilamb/output_pass2_P2F3_fresh`.

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

Pass-2 final candidate:

```
deficit_ratio = Dbar / (P_ann + ratio_p0)

wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)

arid_soft_1  = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)
arid_desert  = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)

fire_rate_yr = base_fire * wet_suppress * arid_soft_1 * arid_desert

burntArea_month = (1 - exp(-min(fire_rate_yr, FIRE_MAX_RATE))) / 12
```

The pass-2 search found that replacing F3b's single arid sigmoid with two smooth fuel-continuity thresholds improves official global Overall from 0.676543 to 0.677073 and improves several weak dryland regions. Ablation showed the high-deficit threshold is essential; the low-deficit threshold is small but gives the highest official global score and contributes to TENA/EURO/MIDE weak-region gains.

## Mechanistic interpretation

Pass 1 established that Model C was missing two global limiters:

1. High annual precipitation / wet-canopy inhibition.
2. Hyperarid fuel-discontinuity inhibition using a dryness-to-rainfall ratio.

Pass 2 refined the second mechanism. A single desert threshold is too blunt: semi-arid fuel networks can fragment gradually before true hyperarid desert conditions. The two-threshold limiter acts like a percolation network with an early weak loss of connected fine fuel and a later strong desert cutoff.

Structural analogy: fire spread resembles packet routing or epidemic/percolation on a network. Performance does not fail only at a single cliff; first the network loses redundancy, then it fragments. The low threshold represents early loss of redundant fuel pathways; the high threshold represents near-total discontinuity.

All terms are global smooth functions of allowed inputs. There is no region routing, latitude/longitude feature, cell lookup, external input, or residual correction.

## Final parameters

```
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
```

Original Model C core parameters are preserved in `models/C/params.BASELINE-before-research.json`. `scripts/reproduce_modelC.py` supports both the pass-1 F3b schema and this pass-2 two-arid-threshold schema.
