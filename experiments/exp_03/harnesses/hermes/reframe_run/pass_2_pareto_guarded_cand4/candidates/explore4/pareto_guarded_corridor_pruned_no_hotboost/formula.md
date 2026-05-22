# Pareto guarded corridor, pruned no-hotboost candidate

Candidate: `ED-Cand4Abl-no_hotboost` / `pareto_guarded_corridor_pruned_no_hotboost`

This is a one-global-formula extension of original Model C. It multiplies the original Model C product by a bounded second-order factor, then applies the original ED saturation transform. It uses only allowed fields: dbar, p_ann, p_month-derived transforms, t_air-derived transforms, and monthly GPP-derived transforms.

## Formula sketch

Let `prod_C` be original Model C pre-exponent product and `fire_exp_C` its original exponent.

`dry = sig(dbar; dry_k, dry_c)`
`pwin = sig(p_ann; p_low_k, p_low_c) * supp(p_ann; p_high_k, p_high_c)`
`gwin = sig(gpp_monthly; gpp_lo_k, gpp_lo_c) * supp(gpp_monthly; gpp_hi_k, gpp_hi_c)`
`release = dry * pwin * gwin`

`guard = 1 - guard_amp * cold(t_ann) * short(warm_month_fraction) * productive(gpp_ann)`

`wet_low = sig(p_ann; wet_k, wet_c) * supp(dbar; lowdef_k, lowdef_c)`
`arid = supp(p_ann; arid_k, arid_c)`

`factor = (1 + boost * release * guard) * (1 - cap_amp * wet_low) * (1 - arid_amp * arid)`

`rate = (prod_C * factor) ** (fire_exp_C * exp_mult)`
`burntArea = (1 - exp(-min(rate, FIRE_MAX_RATE))) / 12`

The searched hot-temperature boost was ablated/pruned: `hotboost = 0`.

## Parameters

- `arid_amp`: 0.43586112271489125
- `arid_c`: 856.6837242561816
- `arid_k`: 0.009023621157614303
- `boost`: 1.7833722261637368
- `cap_amp`: 0.3047300064004322
- `cold_c`: 273.02072243370066
- `cold_k`: 0.1807416417037634
- `dry_c`: 35.97470986141089
- `dry_k`: 0.00413003581877206
- `exp_mult`: 1.11235684145781
- `gpp_hi_c`: 2.6047079318870288
- `gpp_hi_k`: 15.41008899203595
- `gpp_lo_c`: 0.01747443120078264
- `gpp_lo_k`: 5.860990487146787
- `guard_amp`: 0.4074969269643666
- `guard_gpp_c`: 0.02511382714311219
- `guard_gpp_k`: 0.05027109665979641
- `hot_c`: 290.83666204851136
- `hot_k`: 0.031524659892872446
- `hotboost`: 0.0
- `lowdef_c`: 944.0654220717427
- `lowdef_k`: 0.013319164115876287
- `p_high_c`: 1532.7965751974089
- `p_high_k`: 0.009331488778024033
- `p_low_c`: 259.8199961137102
- `p_low_k`: 0.012619167152049767
- `short_c`: 0.11111495197945899
- `short_k`: 13.943740102491747
- `wet_c`: 1753.3941608490388
- `wet_k`: 0.015274262703466136

## Mechanistic interpretation

- Release window: dry months in intermediate annual-precipitation and intermediate-productivity cells are allowed more fire, extending the successful Cand3 mechanism.
- Cold/short-season guard: a relay-protection term reduces the release boost in cold, short-warm-season productive climates where generic dry release can over-burn boreal systems.
- Wet/low-deficit cap: suppresses wet productive cells that have fuel but remain too moist to burn efficiently.
- Hyperarid corridor limit: suppresses very low annual precipitation cells where ignition/weather can be favorable but continuous fuel is absent.
- Hot-dry boost was not retained because ablation showed it was effectively neutral.
