# Evaluation Log

## C0 baseline

Verification: `.venv/bin/python scripts/verify.py` -> PASS, all 24 expected files present and SHA256 OK.

Official global ILAMB: `ilamb/output_modelC`

| Metric | Score |
|---|---:|
| Bias Score | 0.728089 |
| RMSE Score | 0.505759 |
| Seasonal Cycle Score | 0.845690 |
| Spatial Distribution Score | 0.772351 |
| Overall Score | 0.671529 |

Official regional ILAMB: `ilamb/output_regions_official`

| Region | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean original grids |
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

## F3a fixed suppressors

Optuna: 800 trials. Internal simple score 0.679074.
Candidate JSON: `research_candidates/F3a_fixed_suppressors.json`.
Official global output: `ilamb/output_F3a_global`.
Official regional output: `ilamb/output_F3a_regions`.

| Metric | Score |
|---|---:|
| Bias Score | 0.738227 |
| RMSE Score | 0.511895 |
| Seasonal Cycle Score | 0.844302 |
| Spatial Distribution Score | 0.776402 |
| Overall Score | 0.676544 |

## F3 ablations, official global ILAMB

| Candidate | Overall | Bias | RMSE | Seasonal | Spatial | Decision |
|---|---:|---:|---:|---:|---:|---|
| F3a full suppressors | 0.676544 | 0.738227 | 0.511895 | 0.844302 | 0.776402 | Accepted family |
| F3abl_no_wet | 0.6729 | 0.7301 | 0.5079 | 0.8444 | 0.7742 | Wet suppressor retained |
| F3abl_no_arid | 0.6753 | 0.7363 | 0.5097 | 0.8456 | 0.7753 | Arid suppressor retained |
| F3abl_no_cool / F3b | 0.676543 | 0.738225 | 0.511898 | 0.844302 | 0.776393 | Cool suppressor pruned |

## F3b final pruned regional ILAMB

Official regional output: `ilamb/output_F3b_no_cool_regions`

| Region | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean original grids |
|---|---:|---:|---:|---:|---:|---:|
| global | 0.676543 | 0.738225 | 0.511898 | 0.844302 | 0.776393 | 0.484218 |
| bona | 0.777787 | 0.882768 | 0.741079 | 0.923853 | 0.600156 | 0.039011 |
| tena | 0.406672 | 0.483984 | 0.345280 | 0.691560 | 0.167254 | 0.318773 |
| ceam | 0.403003 | 0.374136 | 0.341767 | 0.843531 | 0.113815 | 0.612190 |
| nhsa | 0.602484 | 0.538300 | 0.500749 | 0.915313 | 0.557308 | 0.374335 |
| shsa | 0.543078 | 0.566490 | 0.483830 | 0.816457 | 0.364784 | 0.629801 |
| euro | 0.376821 | 0.423902 | 0.280603 | 0.808049 | 0.090950 | 0.270967 |
| mide | 0.408459 | 0.486010 | 0.344764 | 0.761113 | 0.105643 | 0.248475 |
| nhaf | 0.652601 | 0.767938 | 0.479131 | 0.898681 | 0.638124 | 1.280640 |
| shaf | 0.657096 | 0.758823 | 0.502045 | 0.901254 | 0.621316 | 1.321200 |
| boas | 0.727964 | 0.841221 | 0.625711 | 0.797674 | 0.749504 | 0.067913 |
| ceas | 0.678107 | 0.789265 | 0.579452 | 0.732588 | 0.709778 | 0.198227 |
| seas | 0.509196 | 0.567961 | 0.404173 | 0.821611 | 0.348064 | 0.816824 |
| eqas | 0.628943 | 0.709654 | 0.587986 | 0.846531 | 0.412561 | 0.068361 |
| aust | 0.670563 | 0.750721 | 0.655101 | 0.574376 | 0.717515 | 0.421342 |

## Public TRENDY/firepipe final

Output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-formal-candidate`
Caveat: JSBACH showed an IndexError during model-confrontation pairs, then completed post-processing; score table was produced.

| Rank | Model | Overall | Bias | RMSE | Seasonal | Spatial | Period Mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-formal-candidate | 0.676313 | 0.738225 | 0.511898 | 0.844302 | 0.775242 | 0.484218 |
| 2 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | 0.731335 | 0.507024 | 0.847636 | 0.769145 | 0.558436 |
| 3 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | 0.731487 | 0.507071 | 0.845979 | 0.769529 | 0.554164 |
| 4 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | 0.731037 | 0.506947 | 0.846199 | 0.768796 | 0.564224 |
| 5 | ED-ModelC-curing-lag-v1-current | 0.671767 | 0.727997 | 0.505755 | 0.848710 | 0.770616 | 0.614471 |
| 8 | ED-ModelC-baseline-current | 0.671274 | 0.728089 | 0.505759 | 0.845690 | 0.771075 | 0.611164 |
| 9 | CLASSIC | 0.666048 | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.355219 |
| 10 | CLM6.0 | 0.660644 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.383281 |

## F4a full retune

Optuna: 1000 trials over 22 parameters. Best internal candidate reverted to baseline-equivalent with internal simple 0.672789. Rejected without official ILAMB because it did not produce a meaningful non-baseline candidate.
