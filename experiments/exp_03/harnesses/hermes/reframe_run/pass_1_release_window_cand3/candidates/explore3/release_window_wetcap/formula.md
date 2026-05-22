# ED-Cand3-release_window_wetcap

Unified global candidate formula built as a second-order extension of original Model C.

Base Model C product:

```
C = onset(Dbar) * suppress(Dbar) * precip_floor(P_ann) * precip_dampen(P_month) * gpp_hump(GPP_month) * air_temp_ign(T_air)
```

Second-order release-window boost:

```
dry_now      = sigmoid(Dbar; dry_k, dry_c)
p_window     = sigmoid(P_ann; p_low_k, p_low_c) * suppress(P_ann; p_high_k, p_high_c)
gpp_window   = sigmoid(GPP; gpp_lo_k, gpp_lo_c) * suppress(GPP; gpp_hi_k, gpp_hi_c)
release      = dry_now * p_window * gpp_window
```

Soft wet/low-deficit cap:

```
wet_lowdef = sigmoid(P_ann; wet_k, wet_c) * suppress(Dbar; lowdef_k, lowdef_c)
cap        = 1 - cap_amp * wet_lowdef
```

Final annual rate before ED monthly transform:

```
rate = [ C * (1 + boost * release) * cap ]^(fire_exp_C * exp_mult)
```

Then the same ED-consistent transform is applied:

```
burntArea_month = (1 - exp(-min(rate, FIRE_MAX_RATE))) / 12
```

## Parameters

```
exp_mult = 1.087101152369019
boost = 1.2336330223250789
dry_k = 0.04241791177389437
dry_c = 213.98059190724265
p_low_k = 0.029485803776716793
p_low_c = 672.6075436104074
p_high_k = 0.02066658483851152
p_high_c = 1920.4872523398378
gpp_lo_k = 13.98478290002447
gpp_lo_c = 0.01157418986027045
gpp_hi_k = 16.997687904451354
gpp_hi_c = 0.5249589297635975
cap_amp = 0.22770466583895504
wet_k = 0.0013138097424932429
wet_c = 2189.52292752485
lowdef_k = 0.012821995482662973
lowdef_c = 226.16826845690363
```

## Mechanistic interpretation

The prior pass showed that blunt wet-forest suppression helped weak regions but damaged global spatial skill, while antecedent fuel charging alone damaged African/boreal fire belts. This formula treats burned area as a gated release process: fuels are amplified only in cells/months where current dryness, intermediate annual precipitation, and an intermediate monthly productivity window coincide. A soft wet/low-deficit cap suppresses closed wet-canopy states without imposing a broad annual-precipitation penalty. The structure is global and uses only allowed physical inputs.
