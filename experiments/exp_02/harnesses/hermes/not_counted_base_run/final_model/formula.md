# Final candidate C7 — humid-regime suppression + active dry-down gate

One global formula using only allowed inputs. Starting from Model C product:

```
base = onset(Dbar) * suppress(Dbar)
     * precip_floor(P_ann) * precip_dampen(P_month)
     * gpp_hump(GPP_month) * air_temp_ign(T_air)

dry_gate = dry_floor + (1-dry_floor) * sigmoid(Dbar - mean(Dbar[t-1:t-3]), dry_k, dry_c)

humid_gate = humid_floor + (1-humid_floor) / (1 + (P_ann / humid_half)^humid_pow)

fire_rate_yr = (base * dry_gate * humid_gate)^fire_exp
burntArea_month = (1 - exp(-min(fire_rate_yr, 5.0))) / 12
```

Mechanistic interpretation:

- `dry_gate` represents active curing/flammability during increasing dry-season water deficit. It is a smooth global function of dry-down rate, not a region rule.
- `humid_gate` represents persistent-wet/evergreen/humid-fuel suppression at very high annual precipitation, separating humid tropical forest regimes from fire-prone seasonal savanna using only annual precipitation.
- Both terms are multiplicative, smooth, and globally applied.

Parameters are in `params_and_metadata.json`.
