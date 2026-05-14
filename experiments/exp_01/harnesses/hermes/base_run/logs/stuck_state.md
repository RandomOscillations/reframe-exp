# Stuck State

This file records the defensible stopping point for the formal ED fire model-improvement run under the constraints in `program.md` and `WORKSPACE_MANIFEST.md`.

## Best-so-far model and mechanism

Best accepted model: original Model C.

Mechanism:

```text
fire(cell, month) = [
  dryness_onset(Dbar)
  * hyperarid_dryness_suppression(Dbar)
  * annual_precip_floor(P_ann)
  * monthly_precip_dampening(P_month)
  * monthly_GPP_hump(GPP_month)
  * warm_air_temperature_ignition(T_air)
]^fire_exp
```

The final workspace was restored to the original Model C parameter/output hashes:

```text
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
```

Highest official global-score trial: LAG-FUEL-v1, Overall 0.672274, but rejected because the gain hides regional damage. Therefore it is not the best accepted model under the protocol.

## Baseline vs best official global ILAMB table

Because no candidate satisfied acceptance criteria, baseline and best accepted are the same original Model C. The table also includes the highest global rejected candidate for transparency.

| Model | Status | Bias | RMSE | Seasonal | Spatial | Overall | Period Mean |
|---|---|---:|---:|---:|---:|---:|---:|
| Original Model C | best accepted / final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | 0.611164 |
| LAG-FUEL-v1 | rejected, highest global | 0.727752 | 0.505788 | 0.850890 | 0.771151 | 0.672274 | 0.620074 |

Global-score interpretation: LAG-FUEL-v1 gains only +0.000745 Overall. The gain comes mainly from Seasonal Cycle (+0.005200) while Bias and Spatial decline. This is too small and too regionally damaging to accept.

## Baseline vs best official regional ILAMB table

Best accepted model is original Model C, so baseline and best accepted regional scores are identical. The rejected highest global trial is shown to document why it was not accepted.

| Region | Original Model C Overall | LAG-FUEL-v1 Overall | LAG-FUEL delta |
|---|---:|---:|---:|
| global | 0.671529 | 0.672274 | +0.000745 |
| bona | 0.789806 | 0.789822 | +0.000016 |
| tena | 0.381473 | 0.380430 | -0.001043 |
| ceam | 0.376153 | 0.376183 | +0.000030 |
| nhsa | 0.605824 | 0.605953 | +0.000129 |
| shsa | 0.507249 | 0.507235 | -0.000014 |
| euro | 0.361128 | 0.359158 | -0.001970 |
| mide | 0.382769 | 0.375704 | -0.007065 |
| nhaf | 0.645855 | 0.645457 | -0.000398 |
| shaf | 0.646693 | 0.645818 | -0.000875 |
| boas | 0.728733 | 0.728485 | -0.000248 |
| ceas | 0.670499 | 0.669648 | -0.000851 |
| seas | 0.487193 | 0.483199 | -0.003994 |
| eqas | 0.507395 | 0.507429 | +0.000034 |
| aust | 0.670219 | 0.679152 | +0.008933 |

Regional conclusion: LAG-FUEL-v1 improves Australia and global seasonal phase but damages multiple weak or important regions, especially MIDE, SEAS, EURO, TENA, CEAS, SHAF, NHAF. This violates the instruction not to accept global score gains that hide regional damage.

## Public TRENDY/firepipe ranking table

Uncontaminated baseline public run: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-baseline-formal`.

Serious candidate public run: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-lag-fuel-pure-v1`.

Known caveat: JSBACH hit the documented public benchmark `IndexError`. Candidate/model comparisons that completed remain usable. Additional caveat: the public benchmark wrapper symlinks `SRC` into model folders; during the LAG-FUEL public run, the previously created `ED-ModelC-baseline-formal` symlink pointed at the current workspace candidate file, so that run printed an identical baseline-formal row. Use the original baseline public output for baseline score.

| Rank | Model | Public Overall | Notes |
|---:|---|---:|---|
| 1 | ED-ModelC-lag-fuel-pure-v1 | 0.672014 | serious candidate; rejected by official regional criteria |
| 1/2 | Original Model C baseline | 0.671274 | uncontaminated baseline public run; rank #1 before rejected candidate |
| 3 | CLASSIC | 0.666048 | comparator |
| 4 | CLM6.0 | 0.660644 | comparator |
| 5 | CLM-FATES | 0.656831 | comparator |
| 6 | ELM-FATES | 0.656788 | comparator |
| 7 | JULES-ES | 0.590519 | comparator |
| 8 | ELM | 0.556381 | comparator |
| 9 | VISIT-UT | 0.554455 | comparator |
| 10 | LPJmL | 0.548547 | comparator |
| 11 | LPJ-GUESS | 0.479233 | comparator |
| 12 | EDv3 | 0.477410 | comparator |
| 13 | LPJ-EOSIM | 0.463542 | comparator |

Public conclusion: LAG-FUEL-v1 is public-rank #1 by scalar Overall, but this is not sufficient for acceptance because official regional ILAMB shows damage.

## Mechanisms tried

1. Original Model C baseline:
   - dryness onset and hyperarid suppression,
   - precipitation floor and monthly precipitation dampening,
   - monthly GPP fuel hump,
   - warm-temperature ignition.

2. WET-SUPP-v1 annual wetness ceiling:
   - smooth suppression at high annual precipitation,
   - intended to represent perhumid fuel-moisture/combustibility limitation,
   - deterministic grid over wetness half-saturation and exponent.

3. LAG-FUEL-v1 antecedent/cured GPP fuel:
   - rolling prior-month GPP mean blended into fuel hump,
   - intended to represent curing and antecedent biomass availability,
   - deterministic grid over window and alpha.

4. LAG+WET-v1 combined diagnostic:
   - combination of WET-SUPP-v1 and LAG-FUEL-v1,
   - tested whether perhumid suppression could mitigate lagged-fuel regional damage.

5. PRECIP-MEM-v1 antecedent precipitation moisture:
   - rolling prior-month precipitation mean in the existing rain dampener,
   - intended to represent fuel-moisture memory/accessibility,
   - deterministic grid over memory window and alpha.

## Failed and marginal directions

- Annual wetness suppression improves humid/tropical regional failures but lowers global Overall and damages NHAF/SHAF/AUST. It suggests the humid-regime mechanism is real but not enough as a unified fix.
- Antecedent GPP fuel gives the best scalar/global improvement, mostly through Seasonal Cycle, but the gain is small and damages several weak regions. It cannot be accepted under the regional criteria.
- Combining lagged fuel with wetness suppression does not remove the regional damage; it mostly trades Spatial Distribution for Seasonal Cycle and humid-region gains.
- Antecedent precipitation memory strongly improves many weak regions but substantially harms African savanna fire regimes and global Spatial Distribution.
- Proxy improvements are not reliable enough for acceptance: WET-SUPP and LAG-FUEL improved proxy Overall, but official ILAMB exposed trade-offs.

## Remaining regional/fire-regime failures

- Very low Spatial Distribution remains in CEAM, EURO, MIDE, TENA, and EQAS under baseline.
- African savanna regimes (NHAF/SHAF) are sensitive: mechanisms that help humid/temperate/tropical weak regions often suppress or distort African fire enough to reduce global/spatial performance.
- SEAS, SHSA, and EQAS respond positively to wetness/moisture modifications, but not without trade-offs elsewhere.
- Australia improves with lagged fuel and precipitation memory, but those same changes worsen MIDE/SEAS or African regions.
- Bias/period-mean tension persists: many candidates reduce overprediction in some humid regions but lower period mean or spatial variance in ways official Spatial Distribution penalizes.

## Why more smooth gates or parameter tuning are unlikely to help

The explored changes span the physically obvious smooth gates available under the fixed input contract:

- high-annual-precipitation wetness suppression,
- antecedent productivity/fuel curing,
- antecedent rainfall/fuel-moisture memory,
- interaction of wetness suppression with lagged fuel.

All use allowed inputs and unified global forms. The official regional evidence shows that these gates move the model along a trade-off surface rather than toward a uniformly better solution:

- Wetter/moisture-memory gates help humid and many weak low-score regions, but reduce African savanna and global spatial realism.
- Lagged fuel improves seasonality and Australia, but shifts regional phase/magnitude enough to damage MIDE, EURO, SEAS, and others.
- Combining smooth gates does not remove the tension; it redistributes the same damage.

Further parameter tuning around these forms is likely to interpolate among the evaluated trade-offs. The best settings already sit near weak perturbations: strong enough to change target failures but not strong enough to avoid cross-regime penalties. More aggressive settings in the deterministic scans worsened proxy scores, especially Spatial or Seasonal components. Pure retuning without a new physical mechanism is disallowed by `program.md`.

## Why remaining failures appear unresolved under current constraints

The remaining failures likely require information not available in the allowed input contract or mechanisms that cannot be represented by one smooth climate/productivity gate without regime-specific side effects. Examples of missing-but-relevant processes include human ignition/suppression, land use and fragmentation, vegetation/fuel type, grazing, lightning, cropland/pasture management, and sub-grid fuel continuity. These cannot be added as model inputs in this run.

Within the allowed inputs, the same variables (`P_ann`, `P_month`, GPP, dryness, temperature) must explain both humid tropical suppression and highly flammable savannas. Official regional ILAMB shows these regimes demand opposing adjustments. Without region routing, coordinate hacks, lookup tables, external inputs, or arbitrary residual corrections, further smooth gates are unlikely to separate those regimes without recreating the same trade-off.

Final stopping decision: constrained model exploration is exhausted for this formal base local-search phase. Original Model C remains the best accepted model; LAG-FUEL-v1 is documented as a rejected scalar-best candidate. The workspace has been restored to original Model C and verified.
