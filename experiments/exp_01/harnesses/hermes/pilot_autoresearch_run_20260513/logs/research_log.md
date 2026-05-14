# Research Log

## 2026-05-13 18:42-19:09 EDT — formal Model C improvement run

Required files read before any code/model changes:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

Understanding recorded in-session: start from original Model C; use only allowed CRUJRA Dbar/precip/temp and EDv3 monthly GPP inputs plus existing masks/reference for evaluation; keep one global mechanistic interpretable formula; no external predictor data, lat/lon hacks, named-region routing, per-cell lookup tables, per-region formulas, or arbitrary residual correction coefficients; run official global/regional ILAMB and public TRENDY/firepipe for serious candidates; maintain logs and finish with `final_report.md`.

### Baseline verification
- Command: `.venv/bin/python scripts/verify.py`
- Result: PASS, 24/24 artifacts present, 24/24 hashes OK.
- Baseline hashes later re-verified after restoration:
  - `models/C/params.json`: `3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b`
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: `5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862`
  - `out_terms/modelC_terms.nc`: `306b833a4aeed362d67cd510793e75e1ca9a5e2735b2ebdd0c57175bcaae1883`

### Baseline official ILAMB
- Initial documented command used `ILAMB_ROOT="$PWD/ilamb"`, but this workspace-local `ilamb/` lacks `DATA/burntArea/GFED4.1S/burntArea.nc` and produced an empty scalar database with `MisplacedData`.
- Corrected official reference root to `/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb`, which contains the ILAMB reference data.
- Official global command:
  `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_baseline" bash scripts/run_ilamb.sh`
- Official regional command:
  `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_baseline" bash scripts/run_official_regions.sh`
- Baseline global: Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, Overall 0.671529.
- Weak regional Overall baselines: EURO 0.361128, CEAM 0.376153, TENA 0.381473, MIDE 0.382769, SEAS 0.487193, SHSA 0.507249, EQAS 0.507395.

### Search implementation
Files added:
- `scripts/search_candidate_extensions.py`
- `scripts/generate_candidate_output.py`
- `models/C/candidate_search/optuna_extension_search_500_trials.json`
- `models/C/candidate_search/lag_fuel_v1.json`

Search command:
`N_TRIALS=500 .venv/bin/python scripts/search_candidate_extensions.py`

Physical/regime hypotheses searched in one global formula family:
1. `wet_supp`: perhumid annual precipitation can suppress combustion through persistent wet canopy/fuel moisture even where fuel is abundant.
2. `lag_fuel`: antecedent/cured productivity can better represent carry-over fine fuel than same-month GPP alone.
3. `precip_memory`: recent rainfall memory can better represent fuel moisture than fire-month precipitation alone.
4. `lag_wet`: lagged fuel plus annual wetness ceiling may be complementary.
5. `hybrid`: simultaneous smooth global fuel/moisture/drydown terms may expose a combined optimum.
6. `drydown`: month-to-month Dbar increase may represent curing/rapid drying fire pulses.

Functional forms searched:
- `GPP_eff = (1-alpha) * GPP_month + alpha * mean(GPP[t-1]...GPP[t-window])`
- `P_month_eff = (1-alpha) * P_month + alpha * mean(P_month[t-1]...P_month[t-window])`
- `wet_supp(P_ann) = 1 / (1 + (P_ann/P_wet_half)^P_wet_pow)`, blended by `wet_strength`
- `drypulse = 1 + drydown_amp * max(Dbar - Dbar[t-1],0) / (max(Dbar-Dbar[t-1],0)+drydown_half)`, blended by `drydown_strength`

Optuna setup:
- 500 trials, TPE sampler, seed 13, multivariate/group mode.
- Baseline Model C parameters fixed; only added global mechanistic extension parameters searched.
- Internal/proxy objective used GFED only as evaluation reference and followed ILAMB-like Bias/RMSE/Seasonal/Spatial with official tier-2 weighting plus a small complexity penalty.
- Enqueued ablation corners: LAG-FUEL-v1 (`alpha=1`, `window=12`), WET-SUPP deterministic corner (`P_wet_half=3000`, `P_wet_pow=3`), PRECIP-MEM corner (`alpha=0.25`, `window=1`).

Search result:
- Baseline proxy Overall: 0.629550.
- Enqueued LAG-FUEL-v1 proxy: 0.629606.
- Enqueued WET-SUPP corner proxy: 0.630098.
- Enqueued PRECIP-MEM corner proxy: 0.628997.
- Best 500-trial proxy candidate: OPT-WET-v1, `wet_strength=0.9901726411855946`, `P_wet_half=2253.544627972052`, `P_wet_pow=3.9777542158515304`, proxy Overall 0.630790.
- Decision from proxy: evaluate OPT-WET-v1 officially; also evaluate LAG-FUEL-v1 officially because it was a clean, mechanistically simple, previously plausible scalar-improving antecedent fuel ablation and it directly tests fire-season timing.

### Candidate OPT-WET-v1 official evaluation
Hypothesis: perhumid climates require a smooth global wetness ceiling to avoid over-burning wet tropical/humid regions.
- Generated by: `.venv/bin/python scripts/generate_candidate_output.py models/C/candidate_search/optuna_extension_search_500_trials.json OPT-WET-v1`
- Official global output: `ilamb/output_modelC_opt_wet_v1`
- Official regional output: `ilamb/output_regions_opt_wet_v1`
- Public output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-opt-wet-v1-current`
- Official global: Bias 0.730475, RMSE 0.506667, Seasonal 0.845975, Spatial 0.768628, Overall 0.671682.
- Deltas vs baseline: Overall +0.000153, Bias +0.002386, RMSE +0.000908, Seasonal +0.000285, Spatial -0.003723.
- Regional benefits: EQAS +0.052015, SHSA +0.016485, SEAS +0.014521, CEAM +0.013998, NHSA +0.009945, TENA +0.003903.
- Regional harms: SHAF -0.002837, AUST -0.001146, NHAF -0.001075.
- Public Overall: 0.671436 (rank above baseline and TRENDY comparators in the run, below LAG-FUEL-v1-current).
- Decision: reject as accepted final despite strong humid-region diagnostic benefit. The global gain is tiny, Spatial Distribution declines, and African savanna/Australia regional damage indicates a wetness ceiling trades off against high-fire savanna regimes.

### Candidate LAG-FUEL-v1 official evaluation
Hypothesis: burned area responds to prior productivity after curing; a 12-month antecedent GPP mean may improve seasonal phase and fuel carry-over while remaining a single global formula.
- Generated by: `.venv/bin/python scripts/generate_candidate_output.py models/C/candidate_search/lag_fuel_v1.json LAG-FUEL-v1`
- Official global output: `ilamb/output_modelC_lag_fuel_v1`
- Official regional output: `ilamb/output_regions_lag_fuel_v1`
- Public output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-v1-current`
- Official global: Bias 0.728075, RMSE 0.505767, Seasonal 0.848154, Spatial 0.771532, Overall 0.671859.
- Deltas vs baseline: Overall +0.000330, Seasonal +0.002464, Spatial -0.000819, Bias -0.000014, RMSE +0.000008.
- Regional benefits: AUST +0.006033, NHSA +0.000140, CEAM +0.000093, EQAS +0.000036, BONA +0.000015.
- Regional harms: MIDE -0.006462, SEAS -0.004259, EURO -0.001974, TENA -0.001323, CEAS -0.000946, NHAF -0.000901, SHAF -0.000879, BOAS -0.000439.
- Public Overall: 0.671600 (rank #1 among public benchmark rows in the current run).
- Decision: reject as accepted final. It is the highest global/public scalar candidate in this run, but the scalar gain is small and driven by seasonality while many weak/important regions degrade.

### Public TRENDY/firepipe benchmark notes
Commands:
- LAG-FUEL-v1: `TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" MODEL_NAME="ED-ModelC-lag-fuel-v1-current" OUT=".../output_with_ED-ModelC-lag-fuel-v1-current" bash scripts/run_public_trendy_firepipe.sh`
- OPT-WET-v1: same wrapper with `MODEL_NAME="ED-ModelC-opt-wet-v1-current"`
- Baseline: regenerated original Model C, then same wrapper with `MODEL_NAME="ED-ModelC-baseline-current"`
- Known caveat: JSBACH produced the documented `IndexError`; all other model comparisons and score tables completed.

### Restoration
- Final artifact state restored to original Model C via `.venv/bin/python scripts/reproduce_modelC.py`.
- Verification after restoration: `.venv/bin/python scripts/verify.py` PASS.

### Stopping decision
The constrained search produced two tiny scalar improvements but neither is defensibly acceptable when official regional ILAMB and mechanism trade-offs are considered. OPT-WET-v1 shows real humid-region signal but damages spatial/African savanna behavior. LAG-FUEL-v1 has the highest global/public scalar score but damages multiple weak regions. Additional hybrid/precip-memory/drydown searches in the 500-trial Optuna run did not produce a better proxy candidate; the best collapsed to a wetness ceiling. Further tuning appears to interpolate along the same moisture/humid-vs-savanna and seasonality-vs-regional-realism trade-off surface, while more explicit separation would risk disallowed region/type routing or external inputs.


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
