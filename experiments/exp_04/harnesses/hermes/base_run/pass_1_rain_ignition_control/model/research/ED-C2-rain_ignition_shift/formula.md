# ED-C2-rain_ignition_shift Formula

Best local official candidate from this workspace's constrained Model C improvement run.

## Relationship to original Model C

C2-rain keeps the original Model C core:

```
base_rate = [ onset(Dbar) * suppress(Dbar)
              * precip_floor(P_ann) * precip_dampen(P_month)
              * gpp_hump(GPP_month)
              * air_temp_ign(T_air) ] ^ fire_exp
```

It then replaces the independent air-temperature ignition term with a rain-conditioned ignition term, implemented as a multiplicative ratio against the original ignition term, and applies a final global rate-power compression before the ED annual-rate transform.

## Formula

Let

```
old_ign(T) = sigmoid(T_air; ign_k_C, ign_c_C)
new_ign(T, Pm) = sigmoid(T_air; ign_k2, ign_c_C + rain_shift * log1p(P_month))
rain_ignition_ratio = clip(new_ign / (old_ign + 1e-6), 0.02, 5.0)
raw_rate = base_rate_C * rain_ignition_ratio
compressed_rate = raw_rate ^ rate_power
burntArea_monthly = (1 - exp(-min(compressed_rate, 5.0))) / 12
```

## Parameters

From `models/research/ED-C2-rain_ignition_shift/params.json`:

```
rain_shift = 1.8584561329682763
ign_k      = 0.6241606715796371
rate_power = 0.700475533169256
```

The original Model C parameters are otherwise unchanged.

## Mechanistic interpretation

Monthly precipitation is used as a humidity/wet-fuel proxy. The ignition/spread threshold becomes higher in wet months, so warm conditions do not translate into the same ignition probability under rainfall or high moisture. The final rate-power compression is interpreted as a global intensity/patchiness correction after replacing the ignition response; ablations show it is not sufficient alone and the rain gate is not sufficient alone.

## Official evidence

Official local global ILAMB:
- C0 original Model C Overall: 0.671529
- C2-rain Overall: 0.675267

Ablations:
- rate_power only: 0.661221
- rain-conditioned ignition without rate_power: 0.660225

Public benchmark:
- C2-rain ranks #2 in `public_benchmark_clean`, effectively tied with public ED-ModelC-baseline (0.675020 vs 0.675085) and above CLASSIC/CLM6.0.
