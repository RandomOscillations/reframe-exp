# Regional Analysis

Official regional ILAMB analysis from `scripts/run_official_regions.sh`. Final claims below use official ILAMB regional outputs, not proxy diagnostics.

## Baseline official regional scores

| Region | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean |
|---|---:|---:|---:|---:|---:|---:|
| global | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.611164 |
| bona | 0.789806 | 0.883981 | 0.742535 | 0.925121 | 0.654858 | 0.043941 |
| tena | 0.381473 | 0.437076 | 0.307975 | 0.694036 | 0.160304 | 0.374298 |
| ceam | 0.376153 | 0.286887 | 0.310422 | 0.847470 | 0.125564 | 0.751810 |
| nhsa | 0.605824 | 0.501408 | 0.493150 | 0.914425 | 0.626989 | 0.841181 |
| shsa | 0.507249 | 0.473091 | 0.429758 | 0.820024 | 0.383616 | 0.944540 |
| euro | 0.361128 | 0.393450 | 0.261763 | 0.808165 | 0.080499 | 0.288168 |
| mide | 0.382769 | 0.436689 | 0.310067 | 0.765840 | 0.091179 | 0.341438 |
| nhaf | 0.645855 | 0.769337 | 0.479548 | 0.901029 | 0.599810 | 1.428940 |
| shaf | 0.646693 | 0.759732 | 0.502274 | 0.902122 | 0.567063 | 1.429480 |
| boas | 0.728733 | 0.840753 | 0.619204 | 0.796639 | 0.767865 | 0.073153 |
| ceas | 0.670499 | 0.783351 | 0.560258 | 0.722163 | 0.726466 | 0.258832 |
| seas | 0.487193 | 0.496169 | 0.377266 | 0.826697 | 0.358569 | 1.036140 |
| eqas | 0.507395 | 0.477132 | 0.523149 | 0.836452 | 0.177092 | 0.307191 |
| aust | 0.670219 | 0.745626 | 0.652014 | 0.579524 | 0.721918 | 0.511498 |

Main baseline weak regions by Overall: EURO, CEAM, TENA, MIDE, SEAS, EQAS, SHSA. Spatial scores are especially weak in CEAM, EURO, MIDE, TENA, EQAS.

## Regional Overall deltas vs baseline

| Region | WET-SUPP-v1 | LAG+WET-v1 | LAG-FUEL-v1 | PRECIP-MEM-v1 |
|---|---:|---:|---:|---:|
| global | -0.000145 | +0.000644 | +0.000745 | -0.001336 |
| bona | -0.000026 | -0.000009 | +0.000016 | -0.000449 |
| tena | +0.003254 | +0.002185 | -0.001043 | +0.011514 |
| ceam | +0.009207 | +0.009225 | +0.000030 | +0.011640 |
| nhsa | +0.008031 | +0.008154 | +0.000129 | +0.015017 |
| shsa | +0.010717 | +0.010324 | -0.000014 | +0.025846 |
| euro | +0.001478 | -0.000523 | -0.001970 | +0.012152 |
| mide | +0.000458 | -0.006575 | -0.007065 | +0.010737 |
| nhaf | -0.001487 | -0.001855 | -0.000398 | -0.017440 |
| shaf | -0.002719 | -0.003575 | -0.000875 | -0.005173 |
| boas | +0.000251 | +0.000010 | -0.000248 | +0.001144 |
| ceas | +0.000455 | -0.000376 | -0.000851 | +0.001800 |
| seas | +0.009698 | +0.005185 | -0.003994 | +0.025434 |
| eqas | +0.027613 | +0.027650 | +0.000034 | +0.011763 |
| aust | -0.000805 | +0.008112 | +0.008933 | +0.010295 |

## Interpretation

- WET-SUPP-v1 directly targets humid/perhumid overprediction and improves many tropical/humid regions, especially EQAS, SHSA, SEAS, CEAM, NHSA. However, the global Overall declines because Spatial Distribution worsens and some major fire regimes (NHAF, SHAF, AUST) decline.
- LAG-FUEL-v1 produces the best official global and public scores among candidates by improving Seasonal Cycle. The improvement is not regionally robust: MIDE, EURO, SEAS, TENA, CEAS, BOAS, SHAF, and NHAF decline. This is a classic scalar-score/regional-damage trade-off, so it fails acceptance.
- LAG+WET-v1 confirms the ablation: adding annual wet suppression to lagged fuel recovers some humid/tropical regions but does not remove damage in EURO/MIDE/African regions and lowers Spatial Distribution.
- PRECIP-MEM-v1 is the strongest regional diagnostic for many weak regions, improving TENA, CEAM, NHSA, SHSA, EURO, MIDE, SEAS, EQAS, AUST, but it substantially damages NHAF/SHAF and global Spatial Distribution. This suggests a true mechanistic tension: the same smooth moisture-memory operation that helps humid/temperate/regional timing suppresses African savanna fire too much.

## Final regional conclusion

No candidate satisfies the protocol requirement that global gains not hide regional damage. Original Model C remains the best accepted model. The candidate set indicates remaining failures are not fixed by adding another smooth wetness or lag gate alone: humid/tropical/temperate improvements consistently trade against African savanna or global spatial performance.
