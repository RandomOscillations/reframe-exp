# Candidate Registry

| Candidate | Mechanism | Functional form | Search space/trials | Files changed | Global ILAMB | Regional ILAMB | Public TRENDY/firepipe | Ablations | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| Original Model C | Baseline ignition + precip controls + monthly GPP hump + warm-temperature ignition | `[onset(Dbar) * suppress(Dbar) * precip_floor(P_ann) * precip_dampen(P_month) * gpp_hump(GPP_month) * air_temp_ign(T_air)]^fire_exp` | Existing 12-param Model C; verified from pinned artifacts | none final; restored `ilamb/MODELS/ED-ModelC-final/burntArea.nc` | Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, Overall 0.671529 | See `ilamb/output_regions_baseline`; weak regions EURO 0.361128, CEAM 0.376153, TENA 0.381473, MIDE 0.382769, SEAS 0.487193, EQAS 0.507395 | `ED-ModelC-baseline-current` public Overall 0.671274, above CLASSIC 0.666048 and CLM6.0 0.660644 | Reference state for all deltas | Best accepted/final | Robust scalar rank and no new regional damage from added terms |
| OPT-WET-v1 | Perhumid annual wetness ceiling | Model C product multiplied by `((1-s) + s/(1+(P_ann/P_wet_half)^P_wet_pow))` | 500-trial Optuna extension search over wet, lagged fuel, precip memory, hybrid, drydown families; best: `s=0.9901726412`, `P_wet_half=2253.544628`, `P_wet_pow=3.977754` | added search/generator scripts and candidate JSON; candidate output written temporarily | Bias 0.730475, RMSE 0.506667, Seasonal 0.845975, Spatial 0.768628, Overall 0.671682 | Improves EQAS +0.052015, SHSA +0.016485, SEAS +0.014521, CEAM +0.013998, NHSA +0.009945; harms SHAF -0.002837, AUST -0.001146, NHAF -0.001075 | `ED-ModelC-opt-wet-v1-current` public Overall 0.671436 | Optuna also tested/enqueued WET-SUPP corner; best proxy was wet family; official comparison shows spatial/regional tradeoff | Rejected | Tiny global gain is offset by Spatial Distribution decline and savanna/Australia damage |
| LAG-FUEL-v1 | Antecedent/cured GPP fuel | Replace GPP in existing GPP hump with 12-month lagged mean: `GPP_eff=mean(GPP[t-1]...GPP[t-12])` | Enqueued/ablated in 500-trial search as simple antecedent fuel corner; separately evaluated as serious scalar candidate | `models/C/candidate_search/lag_fuel_v1.json`; candidate output written temporarily | Bias 0.728075, RMSE 0.505767, Seasonal 0.848154, Spatial 0.771532, Overall 0.671859 | Improves AUST +0.006033; harms MIDE -0.006462, SEAS -0.004259, EURO -0.001974, TENA -0.001323, CEAS -0.000946, NHAF -0.000901, SHAF -0.000879, BOAS -0.000439 | `ED-ModelC-lag-fuel-v1-current` public Overall 0.671600, #1 in current public run | Ablates fuel-lag idea without wetness/hybrid terms | Rejected; highest scalar-score model | Scalar gain is small and mainly Seasonal; regional degradation violates acceptance criterion |
| PRECIP-MEM proxy corner | Recent precipitation/fuel-moisture memory | Replace monthly precipitation dampener input with `(1-alpha)*P_month + alpha*mean(P_month[t-1]...t-window)` | Enqueued in 500-trial Optuna with `window=1`, `alpha=0.25`; broader precip-memory/hybrid space searched | no official candidate output retained | Not run officially because proxy score (0.628997) was below baseline proxy and below serious candidates | Not official | Not public | Proxy ablation only | Rejected before official | Did not survive search objective; full search preferred wet ceiling and lag-fuel corners |
| DRYDOWN / HYBRID proxy families | Dbar increase fire pulse and combined smooth global gates | Smooth drydown amplifier and combined fuel/moisture/wetness terms | Included in same 500-trial Optuna search | no official candidate output retained | Not run officially; no best proxy candidate from these families | Not official | Not public | Proxy exploration | Rejected before official | Added complexity did not produce superior proxy candidate; risks overfitting/interpolation without mechanistic payoff |


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
