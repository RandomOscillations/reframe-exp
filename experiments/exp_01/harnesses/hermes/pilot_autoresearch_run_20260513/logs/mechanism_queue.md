# Mechanism Queue

This file supersedes treating `final_report.md` as final. The existing `final_report.md` is now an interim Round 1 report only.

## Round 1 evidence summary

### LAG-FUEL-v1 failure implication
- What improved: official global Seasonal Cycle (+0.002464), public Overall (#1 in current public table), Australia regional Overall (+0.006033).
- What degraded: MIDE (-0.006462), SEAS (-0.004259), EURO (-0.001974), TENA (-0.001323), CEAS (-0.000946), NHAF (-0.000901), SHAF (-0.000879), BOAS (-0.000439). Spatial Distribution declined globally (-0.000819) and strongly in SEAS (-0.026889), EURO (-0.009475), SHAF (-0.005051), CEAS (-0.004776), NHAF (-0.003142).
- Physical inference: a uniform 12-month fuel-memory assumption is too blunt. Antecedent GPP can improve broad phase timing, but it adds/redistributes fuel in places where fire is limited by synchrony of curing, fuel dryness, land use, or ignition rather than total prior productivity. The missing mechanism is likely not "more lag everywhere" but lagged/cured fuel activated only when current conditions indicate a dry/cured fire season.

### OPT-WET-v1 failure implication
- What improved: humid/tropical weak regions, especially EQAS (+0.052015), SHSA (+0.016485), SEAS (+0.014521), CEAM (+0.013998), NHSA (+0.009945), TENA (+0.003903). Bias/RMSE improved in these regions; EQAS Spatial improved +0.087119.
- What degraded: global Spatial Distribution (-0.003723), SHAF (-0.002837), NHAF (-0.001075), AUST (-0.001146). SHAF Spatial declined -0.008071; AUST Spatial declined -0.005251.
- Physical inference: annual precipitation wetness is a real missing signal for humid forests/perhumid regions, but annual wetness alone wrongly suppresses productive seasonal savannas and some Australian fire regimes. The missing distinction is likely seasonality/dry-season accessibility: high annual rainfall with a strong dry season should retain high flammability, while high annual rainfall without enough dry-season relief should be suppressed.

## Current mechanism queue

### Q1. Dry-season-relieved wetness suppression (test next)
- Physical hypothesis: OPT-WET-v1 was right that perhumid wetness suppresses fire, but wrong because it did not distinguish wet evergreen/perhumid climates from seasonal savannas. Use only allowed variables to relieve annual wetness suppression when current cell-month conditions indicate a real dry season: high Dbar and/or low current-month precipitation.
- Unified formula idea:
  - `wet = 1 / (1 + (P_ann/P_wet_half)^P_wet_pow)`
  - `dry_relief = 1 - (1 - sigmoid(Dbar; D_relief_k,D_relief_c)) * (1 - low_precip_gate(P_month; P_relief_half,P_relief_pow))`
  - `wet_multiplier = 1 - wet_strength * (1 - wet) * (1 - relief_strength * dry_relief)`
  - `product := ModelC_product * wet_multiplier`
- Why physically plausible: annual wetness suppresses perhumid forests, but seasonal dry months and accumulated dryness allow savanna grass/fine fuel to burn despite high annual rainfall.
- Search/eval: Optuna 500 trials tied to this family; evaluate best serious candidate with official global and regional ILAMB. Accept only if it preserves OPT-WET humid gains while reducing NHAF/SHAF/AUST and Spatial damage, and global Overall is at least preserved.

### Q2. Curing-gated antecedent fuel (test after Q1 if needed)
- Physical hypothesis: LAG-FUEL-v1 improves global seasonality but damages many regions because antecedent productivity should affect fire only when current climate indicates curing/dry-season accessibility. Uniform 12-month lagged GPP adds fuel memory in wet/temperate/managed regimes where it is not the limiting process.
- Unified formula idea:
  - `curing_gate = sigmoid(Dbar; D_cure_k,D_cure_c) * low_precip_gate(P_month; P_cure_half,P_cure_pow)`
  - `GPP_eff = (1 - alpha*curing_gate) * GPP_month + alpha*curing_gate * lag_mean(GPP, window)`
  - use `GPP_eff` inside the existing GPP hump.
- Why physically plausible: prior productivity becomes burnable fine fuel after curing/drying; without curing, lagged GPP should not boost fire.
- Search/eval: Optuna/deterministic scan over window, alpha, D/P gates; evaluate best serious candidate with official global and regional ILAMB. Accept only if it keeps the seasonality/Australia benefit without MIDE/SEAS/EURO/TENA/CEAS/NHAF/SHAF/BOAS damage.

### Q3. Precipitation concentration / dry-season contrast (test if Q1 and Q2 fail)
- Physical hypothesis: neither annual wetness nor monthly precipitation alone captures annual rainfall concentration. Fire-prone savannas can have high P_ann but sharp dry seasons; perhumid forests have high P_ann and insufficient dry-season contrast.
- Unified formula idea: derive an allowed seasonality/concentration scalar from the monthly precipitation sequence, such as rolling dry-season fraction or annual dry-month deficit, and use it as a smooth gate on wetness suppression or fuel curing.
- Why physically plausible: distinguishes high-rainfall seasonal savannas from high-rainfall perhumid forests without using regions, lat/lon, external land cover, or lookup tables.
- Search/eval: only after Q1/Q2, because Q1 already tests a month-level dry-season relief proxy.

### Q4. No valid next mechanism condition
The queue is empty only if Q1-Q3 are tested/rejected or shown dominated by simpler tested mechanisms, and any further separation would require forbidden region/type routing, external predictors, per-cell lookup tables, coordinate hacks, or residual correction.
