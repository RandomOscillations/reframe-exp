# Regional Analysis

Official regional ILAMB analysis only. Accepted regional conclusions below are from `scripts/run_official_regions.sh` output directories.

## Baseline regional scores

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

Weak baseline regions by Overall: EURO, CEAM, TENA, MIDE, SEAS, EQAS, SHSA. Spatial Distribution is especially weak in EURO, MIDE, CEAM, TENA, and EQAS.

## Candidate regional Overall deltas versus baseline

| Region | Baseline | OPT-WET-v1 delta | LAG-FUEL-v1 delta |
|---|---:|---:|---:|
| global | 0.671529 | +0.000153 | +0.000330 |
| bona | 0.789806 | +0.000040 | +0.000015 |
| tena | 0.381473 | +0.003903 | -0.001323 |
| ceam | 0.376153 | +0.013998 | +0.000093 |
| nhsa | 0.605824 | +0.009945 | +0.000140 |
| shsa | 0.507249 | +0.016485 | -0.000005 |
| euro | 0.361128 | +0.001563 | -0.001974 |
| mide | 0.382769 | +0.000386 | -0.006462 |
| nhaf | 0.645855 | -0.001075 | -0.000901 |
| shaf | 0.646693 | -0.002837 | -0.000879 |
| boas | 0.728733 | +0.000156 | -0.000439 |
| ceas | 0.670499 | +0.000450 | -0.000946 |
| seas | 0.487193 | +0.014521 | -0.004259 |
| eqas | 0.507395 | +0.052015 | +0.000036 |
| aust | 0.670219 | -0.001146 | +0.006033 |

## Interpretation by candidate

### OPT-WET-v1
Mechanistic signal: strong annual precipitation wetness ceiling improves humid/tropical weak regions: EQAS, SHSA, SEAS, CEAM, NHSA, and TENA. This supports the hypothesis that some remaining Model C failures are moisture/humidity/canopy-wetness failures not captured by current-month precipitation dampening alone.

Failure mode: the same global wetness ceiling suppresses high-fire savanna/Australia regimes. SHAF, NHAF, and AUST decline; global Spatial Distribution declines from 0.772351 to 0.768628. This suggests that annual precipitation alone cannot separate wet tropical suppression from productive seasonal savanna flammability without additional type/structure/human inputs or forbidden routing.

### LAG-FUEL-v1
Mechanistic signal: 12-month antecedent GPP improves global Seasonal Cycle and Australia. That is consistent with cured fuel carry-over improving some phase behavior.

Failure mode: the scalar gain hides regional damage in MIDE, SEAS, EURO, TENA, CEAS, NHAF, SHAF, and BOAS. Several of these are already weak regions. Spatial Distribution also declines. The lagged fuel term appears to move timing/seasonality in the right global direction while redistributing regional errors rather than resolving them.

## Regional acceptance judgement

Neither serious candidate is acceptable under the stated criterion that global Overall improvement is insufficient if important weak regions are damaged. OPT-WET-v1 is useful diagnostic evidence but damages savanna/Australia and spatial behavior. LAG-FUEL-v1 is the highest scalar candidate but damages too many weak/important regions. Original Model C remains best accepted.


## 2026-05-13 19:10 EDT — Round 2 outer-loop continuation notice

The previous `final_report.md` is now treated as an interim Round 1 report, not a final stopping artifact. Created `mechanism_queue.md` with explicit failure analysis and queued next mechanisms. Round 2 begins with Q1 dry-season-relieved wetness suppression, motivated by OPT-WET-v1 humid-region gains but NHAF/SHAF/AUST and Spatial damage. Acceptance requires official global + regional ILAMB and preservation of global score without unacceptable regional/spatial damage.


## 2026-05-13 19:22-19:33 EDT — Round 2 Q1 DRYSEASON-WET-v1

Mechanism tested: dry-season-relieved annual wetness suppression. This was inferred from OPT-WET-v1: annual wetness helped humid/perhumid weak regions but over-suppressed seasonal savanna/Australia. The Q1 formula keeps annual wetness suppression but relieves it smoothly when Dbar and/or current low precipitation indicate dry-season accessibility.

Search command: `N_TRIALS=500 .venv/bin/python scripts/search_dryseason_wet_relief.py`
Search output: `models/C/candidate_search/dryseason_wet_search_500_trials.json`
Best proxy candidate: `wet_strength=0.9254714800690381`, `P_wet_half=2034.9510173025635`, `P_wet_pow=4.951654707160729`, `relief_strength=0.36437480803076217`, `D_relief_k=0.005304952754307497`, `D_relief_c=1120.7385664121684`, `P_relief_half=0.11526326332777814`, `P_relief_pow=3.4139761765083936`.

Official global output: `ilamb/output_modelC_dryseason_wet_v1`.
Official global scores: Bias 0.731037, RMSE 0.506947, Seasonal 0.846199, Spatial 0.770020, Overall 0.672230, Period Mean 0.564224.
Deltas vs baseline: Overall +0.000701, Bias +0.002948, RMSE +0.001188, Seasonal +0.000509, Spatial -0.002331, Period Mean -0.046940.

Official regional output: `ilamb/output_regions_dryseason_wet_v1`.
Regional gains vs baseline: EQAS +0.060745, SHSA +0.017608, SEAS +0.014257, CEAM +0.014943, NHSA +0.008846, TENA +0.003591, NHAF +0.000443, CEAS +0.000339, BONA +0.000072, BOAS +0.000065.
Regional harms vs baseline: SHAF -0.001779, AUST -0.001444, EURO +0.001228 and MIDE +0.000228 remain tiny gains but not a full spatial solution.

Public output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-dryseason-wet-v1-current`.
Public Overall: 0.671985, #1 in current public benchmark table. JSBACH had the documented IndexError; completed score table counts as evidence.

Decision: DRYSEASON-WET-v1 is the strongest candidate so far and remains best-so-far candidate, but not yet final. It confirms the Q1 physical hypothesis because dry-season relief improves global/public score and fixes NHAF relative to OPT-WET. However, remaining SHAF/AUST damage and global Spatial decline show the wetness/savanna distinction is still incomplete. Mechanism queue therefore continues to Q2 curing-gated antecedent fuel.


## 2026-05-13 19:34-19:44 EDT — Round 2 Q2 CURING-LAG-v1

Mechanism tested: curing-gated antecedent GPP fuel. This was inferred from LAG-FUEL-v1: uniform 12-month GPP lag improved global seasonality but damaged multiple weak/important regions. Q2 lets lagged fuel affect the GPP hump only when Dbar and/or low current precipitation indicate curing/dry-season accessibility.

Search command: `N_TRIALS=500 .venv/bin/python scripts/search_curing_gated_lag.py`
Search output: `models/C/candidate_search/curing_lag_search_500_trials.json`
Best proxy candidate: one-month lag with strong curing gate: `gpp_lag_window=1`, `lag_alpha=0.9947930088492137`, `D_cure_k=0.02449168226564592`, `D_cure_c=289.0374689642952`, `P_cure_half=0.4554493839153478`, `P_cure_pow=3.3233880373129874`.

Official global output: `ilamb/output_modelC_curing_lag_v1`.
Official global scores: Bias 0.727997, RMSE 0.505755, Seasonal 0.848710, Spatial 0.771904, Overall 0.672024, Period Mean 0.614471.
Deltas vs baseline: Overall +0.000495, Seasonal +0.003020, Spatial -0.000447, Bias -0.000092, RMSE -0.000004.

Official regional output: `ilamb/output_regions_curing_lag_v1`.
Compared with uniform LAG-FUEL-v1, Q2 reduces several damages: MIDE damage improves from -0.006462 to -0.001335, SEAS from -0.004259 to -0.002021, EURO from -0.001974 to -0.000819, CEAS flips to +0.001870, AUST remains positive at +0.004197. However TENA remains negative (-0.001105), EURO/MIDE/SEAS remain negative, and global Spatial still declines.

Public output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-curing-lag-v1-current`.
Public Overall: 0.671767, behind DRYSEASON-WET-v1 but ahead uniform LAG-FUEL and baseline. JSBACH had documented IndexError; completed score table counts.

Decision: diagnostic, not final. Curing-gating validates the physical hypothesis that uniform lag was too blunt, but it does not dominate DRYSEASON-WET-v1 and still damages some weak regions. Mechanism queue continues to Q3 precipitation concentration/dry-season contrast, because Q1 and Q2 both suggest that the missing separator is not instantaneous dryness alone but seasonal rainfall concentration/perhumid-vs-seasonal structure.


## 2026-05-13 19:46-20:10 EDT — Round 2 Q3 PRECIP-CONC-WET-v1 and constrained combo

Q3 mechanism tested: precipitation-concentration wetness relief. Inferred from Q1/Q2 failure pattern: current-month dry relief and curing gates help, but the missing separator appears to be annual dry-season contrast. Q3 uses trailing-12 dry-month fraction from allowed monthly precipitation to relieve annual wetness suppression in seasonal savannas while retaining perhumid suppression.

Search command: `N_TRIALS=500 .venv/bin/python scripts/search_precip_concentration_wet.py`.
Search output: `models/C/candidate_search/precip_concentration_wet_search_500_trials.json`.
Best Q3 parameters: `wet_strength=0.9749769007371538`, `P_wet_half=1779.4206816068952`, `P_wet_pow=4.698056826790257`, `relief_strength=0.7909704781841365`, `dry_month_threshold=18.752075249354416`, `dryfrac_k=23.195108254021612`, `dryfrac_c=0.2251706610087917`, `D_support_k=0.0003532027606815267`, `D_support_c=169.58180624426103`, `d_support_weight=0.31657480284868766`.

Official Q3 outputs: `ilamb/output_modelC_precip_conc_wet_v1`, `ilamb/output_regions_precip_conc_wet_v1`.
Official Q3 global: Bias 0.731487, RMSE 0.507071, Seasonal 0.845979, Spatial 0.770753, Overall 0.672472, Period Mean 0.554164.
Regional deltas vs baseline: TENA +0.005959, CEAM +0.020241, NHSA +0.010228, SHSA +0.018546, EURO +0.002298, MIDE +0.000362, NHAF +0.001573, BOAS +0.000165, CEAS +0.000565, SEAS +0.010724, EQAS +0.076892; small losses SHAF -0.000543 and AUST -0.000646.
Public Q3 Overall: 0.672227, #2 behind the constrained combo in the current public table.

Constrained combo tested only because Q3 retained small AUST/SHAF losses while Q2 improved AUST and seasonality. Q3 wetness parameters were fixed and only curing-gated one-month GPP lag was tuned.
Search command: `N_TRIALS=500 .venv/bin/python scripts/search_precip_conc_wet_curing_lag.py`.
Official combo outputs: `ilamb/output_modelC_precip_conc_wet_curing_lag_v1`, `ilamb/output_regions_precip_conc_wet_curing_lag_v1`.
Official combo global: Bias 0.731335, RMSE 0.507024, Seasonal 0.847636, Spatial 0.770385, Overall 0.672681, Period Mean 0.558436.
Public combo Overall: 0.672433, highest scalar/public candidate.
Combo regional deltas: improves AUST (+0.001516) and seasonality but reintroduces MIDE damage (-0.002080) in an already weak region and lowers SEAS gain relative to Q3. It also still has small SHAF loss (-0.000674) and lower global Spatial than Q3.

Decision: accept PRECIP-CONC-WET-v1 as the best defensible final model because it has strong global/public improvement, broad weak-region gains, preserves MIDE, improves NHAF, and limits remaining damage to very small SHAF/AUST deltas. Reject the constrained combo as highest-global/highest-public scalar model because the extra curing-lag complexity buys +0.000209 global Overall over Q3 at the cost of damaging MIDE and weakening the regional balance. Mechanism queue exhausted: Q1 current dry relief, Q2 curing-gated fuel, Q3 annual precipitation concentration, and the only physically motivated constrained combination have been tested. Further targeted fixes for the tiny remaining SHAF/AUST losses or MIDE/Spatial tradeoff would require missing external predictors (land use/human suppression/fuel type/grazing/ignition) or forbidden region/type/cell routing.
