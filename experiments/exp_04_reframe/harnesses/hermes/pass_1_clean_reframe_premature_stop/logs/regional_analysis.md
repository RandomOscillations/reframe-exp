# Regional Analysis

## Baseline Model C official regional ILAMB triage

Official regional run output: `ilamb/output_modelC_regions/scalar_database.csv`.

The regional ILAMB scalar database reports the component scores by region. Regional `Overall Score` rows are not emitted by this ILAMB configuration, so this log uses the official component rows directly and a diagnostic unweighted component mean only for triage. Acceptance decisions use official global Overall plus official regional components.

| Region | Bias | RMSE | Seasonal | Spatial | Triage component mean |
|---|---:|---:|---:|---:|---:|
| aust | 0.745626 | 0.652014 | 0.579524 | 0.721918 | 0.674771 |
| boas | 0.840753 | 0.619204 | 0.796639 | 0.767865 | 0.756115 |
| bona | 0.883981 | 0.742535 | 0.925121 | 0.654858 | 0.801624 |
| ceam | 0.286887 | 0.310422 | 0.847470 | 0.125564 | 0.392586 |
| ceas | 0.783351 | 0.560258 | 0.722163 | 0.726466 | 0.698059 |
| eqas | 0.477132 | 0.523149 | 0.836452 | 0.177092 | 0.503456 |
| euro | 0.393450 | 0.261763 | 0.808165 | 0.080499 | 0.385969 |
| global | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.7130 |
| mide | 0.436689 | 0.310067 | 0.765840 | 0.091179 | 0.400944 |
| nhaf | 0.769337 | 0.479548 | 0.901029 | 0.599810 | 0.687431 |
| nhsa | 0.501408 | 0.493150 | 0.914425 | 0.626989 | 0.633993 |
| seas | 0.496169 | 0.377266 | 0.826697 | 0.358569 | 0.514675 |
| shaf | 0.759732 | 0.502274 | 0.902122 | 0.567063 | 0.682798 |
| shsa | 0.473091 | 0.429758 | 0.820024 | 0.383616 | 0.526622 |
| tena | 0.437076 | 0.307975 | 0.694036 | 0.160304 | 0.399848 |

Initial failure pattern:
- Strong regions: boreal North America, boreal Asia, central Asia, southern/northern Africa in seasonal timing; Model C captures the dry-season phase well.
- Weakest regions by component mean and especially spatial score: Europe, Central America, Middle East, Temperate North America, Equatorial Asia, Southeast Asia, Southern Hemisphere South America.
- Many weak regions still have good seasonal score, implying timing is less broken than magnitude/spatial allocation. This points toward missing fuel-continuity / human-fragmented / humid-forest suppression / agricultural-mosaic behavior, but any remedy must be inferred from allowed physical inputs only.
- Australia has decent bias/RMSE/spatial but weak seasonal score, suggesting a different failure: monsoon/curing timing or too simple dry-season peak timing.

Next diagnostic step: quantify regional period-mean ratios and spatial correlations from the same fixed inputs/model output to decide whether candidates should mostly suppress overprediction in low-score regions, recover underprediction, or reshape spatial pattern without sacrificing African/savanna timing.


## Loop 1 regional outcomes

Official candidate regional components are in `experiments/loop1_official_regional_components.csv` and `ilamb/output_candidates_loop1/scalar_database.csv`.

Diagnostic component-mean comparison from official regional components:

| Region | C0 final | C1 wet_firebreak | C2 gpp_asym | C3 curing regional | C4 curing global | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| ceam | 0.393 | 0.567 | 0.479 | 0.688 | 0.382 | Weak-region suppression can help CEAM, but global-safe C4 does not. |
| euro | 0.386 | 0.556 | 0.549 | 0.690 | 0.414 | Europe improves under strong suppressors, consistent with overprediction/fragmentation, but these suppressors damage global spatial scores. |
| mide | 0.401 | 0.467 | 0.414 | 0.649 | 0.434 | Middle East has same pattern: improvement requires broad low-fire suppression. |
| tena | 0.400 | 0.617 | 0.471 | 0.676 | 0.402 | Temperate North America remains unresolved by global-safe mechanisms. |
| eqas | 0.503 | 0.662 | 0.651 | 0.688 | 0.466 | Equatorial Asia can improve via high-wetness/GPP suppression, but C4 loses it. |
| seas | 0.515 | 0.631 | 0.614 | 0.670 | 0.517 | Southeast Asia improves under suppressors but not under global-safe tuning. |
| shsa | 0.527 | 0.671 | 0.672 | 0.743 | 0.517 | SH South America similar; broad suppressors help but are not globally acceptable. |
| aust | 0.675 | 0.613 | 0.652 | 0.604 | 0.695 | C4 helps Australia slightly, probably via modified curing/precip timing. |
| shaf | 0.683 | 0.579 | 0.643 | 0.520 | 0.706 | C4 improves SH Africa slightly while suppressor-heavy candidates harm it. |
| bona | 0.802 | 0.636 | 0.680 | 0.645 | 0.742 | Boreal North America is a key constraint: suppressors damage it. |

Regional conclusion: the weak-region failure mode is largely an overprediction/spatial-allocation problem in low-fire, fragmented, humid, or temperate systems. The fixed inputs can indicate some of those regimes, but not enough to distinguish them from productive savanna/boreal fire systems with one simple global gate. This explains why C1-C3 improve weak regions but lose official global Spatial/Overall, while C4 protects global behavior only by nearly neutralizing the new curing mechanism.
