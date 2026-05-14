# Constraint Checks

## Global checks applying to all model/code changes in this run

- Allowed predictive model inputs only: `data/crujra/dbar_monthly.npy`, `p_ann_monthly.npy`, `p_month_monthly.npy`, `t_air_monthly.npy`, monthly EDv3 GPP from `data/trendy_v14/EDv3_S3_gpp.nc`.
- GFED and ILAMB reference data were used only for scoring/evaluation/masks consistent with the baseline workflow, not as explanatory model inputs.
- No external datasets were introduced as model inputs.
- No latitude/longitude values, coordinate hacks, named-region IDs, or named-region routing were used in candidate formulas.
- No per-cell lookup tables or direct cell-identity fitting were used.
- No per-region formulas were used.
- No arbitrary residual correction coefficients were added.
- Every serious candidate remained one global formula and used smooth/interpretable physical transformations of allowed inputs.

## Baseline Model C

- Uses only allowed inputs: yes.
- No external model inputs: yes.
- No latitude/longitude hacks: yes.
- No named-region routing: yes.
- No per-cell lookup tables: yes.
- No per-region formulas: yes.
- No arbitrary residual correction coefficients: yes.
- One global interpretable formula: yes.
- Physical explanation: dryness onset/suppression, precipitation floor/dampening, productivity fuel hump, warm-temperature ignition.
- Official global ILAMB completed: yes, `ilamb/output_modelC_baseline`.
- Official regional ILAMB completed: yes, `ilamb/output_regions_baseline`.
- Public TRENDY/firepipe completed: yes, `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-baseline-current`.
- Final artifact verification: PASS after restoration.

## OPT-WET-v1

- Formula: Model C product multiplied by a smooth annual-precipitation wetness ceiling, blended by `wet_strength`.
- Uses only allowed inputs: yes, adds only a transformation of `P_ann`.
- No external model inputs: yes.
- No latitude/longitude hacks: yes.
- No named-region routing: yes.
- No per-cell lookup tables: yes.
- No per-region formulas: yes.
- No arbitrary residual correction coefficients: yes; term is a mechanistic wetness suppression, not residual correction.
- One global interpretable formula: yes.
- Physical explanation for added term: persistent perhumid wet canopy/fuel moisture can suppress combustion despite fuel abundance.
- Official global ILAMB completed: yes, `ilamb/output_modelC_opt_wet_v1`.
- Official regional ILAMB completed: yes, `ilamb/output_regions_opt_wet_v1`.
- Public TRENDY/firepipe completed: yes, `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-opt-wet-v1-current`.
- Ablation/diagnostic support: yes, 500-trial Optuna search selected wetness ceiling; enqueued wetness corner and official regional deltas diagnose humid-region gains vs savanna damage.
- Complexity pruned: yes, best candidate dropped lag, precip-memory, drydown, and hybrid terms; only one wetness term retained.
- Verdict: rejected as final due Spatial decline and NHAF/SHAF/AUST damage.

## LAG-FUEL-v1

- Formula: replace same-month GPP in the existing GPP hump with a 12-month lagged GPP mean.
- Uses only allowed inputs: yes, transformation of monthly EDv3 GPP.
- No external model inputs: yes.
- No latitude/longitude hacks: yes.
- No named-region routing: yes.
- No per-cell lookup tables: yes.
- No per-region formulas: yes.
- No arbitrary residual correction coefficients: yes; term represents antecedent/cured fuel.
- One global interpretable formula: yes.
- Physical explanation for added term: burned area can depend on prior productivity and cured fine fuel rather than instantaneous productivity only.
- Official global ILAMB completed: yes, `ilamb/output_modelC_lag_fuel_v1`.
- Official regional ILAMB completed: yes, `ilamb/output_regions_lag_fuel_v1`.
- Public TRENDY/firepipe completed: yes, `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-v1-current`.
- Ablation/diagnostic support: yes, clean single-mechanism ablation; 500-trial search enqueued and evaluated lag-fuel corner; official regional deltas identify hidden damage.
- Complexity pruned: yes, no wetness/precip-memory/drydown terms included.
- Verdict: rejected as accepted final despite highest scalar score because multiple weak/important regions degrade.

## PRECIP-MEM, DRYDOWN, and HYBRID proxy families

- Uses only allowed inputs: yes.
- No external model inputs/coordinate/region/cell hacks: yes.
- One global interpretable formula: yes in proxy implementation.
- Official global/regional/public ILAMB: not run because these forms did not survive the 500-trial proxy search as serious best candidates; precip-memory enqueued corner scored below baseline proxy; drydown/hybrid did not become best proxy.
- Complexity pruning: yes, not escalated because the search favored simpler wetness or lag-fuel families and official results for those already exposed the main trade-off surface.

## Final state

Final workspace restored to original Model C:
- `models/C/params.json` hash `3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b`
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc` hash `5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862`
- `out_terms/modelC_terms.nc` hash `306b833a4aeed362d67cd510793e75e1ca9a5e2735b2ebdd0c57175bcaae1883`


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
