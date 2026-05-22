# ED-Cand5-mosaic_edge_release formula summary

Status: full mosaic edge regional repair candidate.

Base: original Model C product of dbar onset/suppression, annual/monthly precipitation gates, monthly GPP hump, and air-temperature ignition, transformed through ED monthly burned-area mapping.

Added unified mechanism family: cycle-5 mosaic/edge continuation. The formula remains one global expression using only allowed dbar, annual/monthly precipitation, air temperature, and GPP transforms.

Mechanism:
- dry/intermediate-precip/intermediate-GPP release window;
- optional mosaic-edge replacement using recent rain hiatus, annual fuel/productivity, and live-fuel senescence;
- hyperarid fuel-continuity suppression;
- cold/short-season productive guard;
- wet/low-deficit cap.

Key parameter subset:
```json
{
  "exp_mult": 1.1066776538078427,
  "boost": 1.7469472933161907,
  "dry_k": 0.012719238193233968,
  "dry_c": 223.42106281098148,
  "p_low_k": 0.013724273475579307,
  "p_low_c": 369.144710522072,
  "p_high_k": 0.01804861919429713,
  "p_high_c": 5019.308601688522,
  "gpp_lo_k": 19.8273003261204,
  "gpp_lo_c": 0.0026911938428577065,
  "gpp_hi_k": 11.73700615371164,
  "gpp_hi_c": 1.2579655854045815,
  "cap_amp": 0.31243498293816896,
  "wet_k": 0.005789454375200487,
  "wet_c": 1637.2733572735358,
  "lowdef_k": 0.002637151620328882,
  "lowdef_c": 257.61293240789195,
  "arid_amp": 0.1930432224255934,
  "arid_k": 0.02321508838444906,
  "arid_c": 771.2996419468487,
  "rainbreak_k": 0.012022423640439078,
  "rainbreak_c": 1.5850179760211605,
  "sen_k": 4.438269133074868,
  "sen_c": 1.202663096310708,
  "monsoon_k": 0.0006755534257233115,
  "monsoon_c": 987.85385746398,
  "cold_guard_amp": 0.19778757312496847,
  "cold_k": 0.0308005927171088,
  "cold_c": 286.8300852252048,
  "short_k": 36.70286782398559,
  "short_c": 0.1187823271676362,
  "edge_k": 0.06231029349896723,
  "edge_c": 1.8281018200266477,
  "annfuel_k": 0.9687741678039236,
  "annfuel_c": 0.24037793616301575,
  "edge_mix": 0.3319761955406695,
  "cap_relief": 0.07658327358638445
}
```

Fast screening metrics:
```json
{
  "fast_global": {
    "bias": 0.7129873113593522,
    "rmse": 0.3833755334378951,
    "seasonal": 0.859131893413297,
    "spatial": 0.768582473263056,
    "overall": 0.6367400093784745
  },
  "weak_mean": 0.376630884195982,
  "weak_min": 0.29828619248283295,
  "protect_min": 0.5551230949259573
}
```

Artifact: `ilamb/MODELS/ED-Cand5-mosaic_edge_release/burntArea.nc`.
