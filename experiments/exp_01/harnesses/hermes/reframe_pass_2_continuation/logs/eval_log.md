# Evaluation Log Pass 2

## Incumbent P2-CURRENT / F3b

From pass-1 final evidence:

| Metric | Official global score |
|---|---:|
| Bias Score | 0.738225 |
| RMSE Score | 0.511898 |
| Seasonal Cycle Score | 0.844302 |
| Spatial Distribution Score | 0.776393 |
| Overall Score | 0.676543 |

Official regional output: `ilamb/output_F3b_no_cool_regions`.
Public output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-formal-candidate`.

## Official global ILAMB summary

| Candidate | Bias | RMSE | Seasonal | Spatial | Overall | Output |
|---|---:|---:|---:|---:|---:|---|
| F3b incumbent | 0.738225 | 0.511898 | 0.844302 | 0.776393 | 0.676543 | `ilamb/output_final_current_global` / pass-1 |
| P2F1 curing gate | 0.738469 | 0.512636 | 0.845672 | 0.773679 | 0.676618 | `ilamb/output_P2F1_curing_gate_global` |
| P2F2 seasonal wet | 0.737437 | 0.510878 | 0.846213 | 0.778162 | 0.676714 | `ilamb/output_P2F2_seasonal_wet_global` |
| P2F3 two-threshold arid | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.677073 | `ilamb/output_P2F3_arid_two_threshold_global` |
| P2F3 no low threshold | 0.738300 | 0.512151 | 0.845262 | 0.777043 | 0.676981 | `ilamb/output_P2F3abl_no_low_global` |
| P2F3 no high threshold | 0.737042 | 0.510722 | 0.850117 | 0.771599 | 0.676040 | `ilamb/output_P2F3abl_no_high_global` |
| P2F3 final current reproduction | 0.738666 | 0.512972 | 0.848079 | 0.772673 | 0.677073 | `ilamb/output_pass2_final_current_global` |

## Regional ILAMB comparison: F3b vs accepted P2F3

| Region | F3b Overall | P2F3 Overall | Delta | P2F3 Bias | P2F3 RMSE | P2F3 Seasonal | P2F3 Spatial |
|---|---:|---:|---:|---:|---:|---:|---:|
| global | 0.676543 | 0.677073 | +0.000530 | 0.738666 | 0.512972 | 0.848079 | 0.772673 |
| bona | 0.777787 | 0.771207 | -0.006580 | 0.883408 | 0.741203 | 0.923351 | 0.566871 |
| tena | 0.406672 | 0.414691 | +0.008019 | 0.499475 | 0.358680 | 0.690093 | 0.166526 |
| ceam | 0.403003 | 0.403716 | +0.000713 | 0.376508 | 0.343289 | 0.840487 | 0.115005 |
| nhsa | 0.602484 | 0.606292 | +0.003808 | 0.540715 | 0.502157 | 0.915313 | 0.571118 |
| shsa | 0.543078 | 0.545642 | +0.002564 | 0.570951 | 0.484417 | 0.811870 | 0.376555 |
| euro | 0.376821 | 0.385437 | +0.008616 | 0.439637 | 0.290451 | 0.807493 | 0.099154 |
| mide | 0.408459 | 0.419018 | +0.010559 | 0.503206 | 0.359813 | 0.759446 | 0.112814 |
| nhaf | 0.652601 | 0.653435 | +0.000834 | 0.767026 | 0.480379 | 0.915245 | 0.624148 |
| shaf | 0.657096 | 0.656661 | -0.000435 | 0.758657 | 0.501939 | 0.901277 | 0.619491 |
| boas | 0.727964 | 0.728730 | +0.000766 | 0.842895 | 0.630159 | 0.798876 | 0.741563 |
| ceas | 0.678107 | 0.679173 | +0.001066 | 0.790580 | 0.585772 | 0.735254 | 0.698485 |
| seas | 0.509196 | 0.511484 | +0.002288 | 0.568322 | 0.404397 | 0.821928 | 0.358376 |
| eqas | 0.628943 | 0.629088 | +0.000145 | 0.709699 | 0.588010 | 0.846438 | 0.413281 |
| aust | 0.670563 | 0.667783 | -0.002780 | 0.752720 | 0.655949 | 0.560839 | 0.713459 |

## Public TRENDY/firepipe P2F3

Output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_pass2_P2F3_fresh`.
Caveat: JSBACH showed the known ILAMB IndexError, then post-processing completed and score table was produced.

| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-pass2-P2F3 | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 1 | ED-ModelC-formal-candidate | 0.676846 | 0.738666 | 0.512972 | 0.848079 | 0.771540 | 0.466368 |
| 3 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| 4 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| 5 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| 9 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| 10 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| 11 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |

Note: `ED-ModelC-formal-candidate` in this fresh public output has the same values as P2F3 because the public helper copied the current pass-2 candidate into that model slot in an earlier attempted run. The unique model name `ED-ModelC-pass2-P2F3` is the unambiguous pass-2 record.
