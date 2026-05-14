# Evaluation Log

## 2026-05-13 — baseline verification
- Command: `.venv/bin/python scripts/verify.py`
- Output: PASS; 24 present, 24 hash OK.
- Evidence: yes, baseline artifact integrity.
- Best-so-far: original Model C retained.

## 2026-05-13 — initial official ILAMB attempt with workspace-local ILAMB_ROOT
- Command: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_baseline_rerun" bash scripts/run_ilamb.sh`
- Output directory: `ilamb/output_modelC_baseline_rerun`
- Result: `MisplacedData`, empty `scalar_database.csv`; workspace-local `ilamb/` did not contain the reference `DATA/burntArea/GFED4.1S/burntArea.nc`.
- Evidence: no; diagnostic only.
- Follow-up: used `/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb` for ILAMB_ROOT.

## 2026-05-13 — original Model C official global ILAMB
- Command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_baseline" bash scripts/run_ilamb.sh`
- Output directory: `ilamb/output_modelC_baseline`
- Model name: `ED-ModelC-final`
- Scores: Bias 0.728089; RMSE 0.505759; Seasonal Cycle 0.845690; Spatial Distribution 0.772351; Overall 0.671529; Period Mean 0.611164.
- Warnings: none material.
- Evidence: yes.
- Best-so-far: accepted baseline.

## 2026-05-13 — original Model C official regional ILAMB
- Command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_baseline" bash scripts/run_official_regions.sh`
- Output directory: `ilamb/output_regions_baseline`
- Evidence: yes.
- Overall by region: global 0.671529; bona 0.789806; tena 0.381473; ceam 0.376153; nhsa 0.605824; shsa 0.507249; euro 0.361128; mide 0.382769; nhaf 0.645855; shaf 0.646693; boas 0.728733; ceas 0.670499; seas 0.487193; eqas 0.507395; aust 0.670219.

## 2026-05-13 — Optuna proxy search
- Command: `N_TRIALS=500 .venv/bin/python scripts/search_candidate_extensions.py`
- Output file: `models/C/candidate_search/optuna_extension_search_500_trials.json`
- Trial count: 500.
- Proxy baseline Overall: 0.629550.
- Best candidate: OPT-WET-v1, proxy Overall 0.630790, `wet_strength=0.9901726411855946`, `P_wet_half=2253.544627972052`, `P_wet_pow=3.9777542158515304`.
- Evidence: search/proposal only; not final without official ILAMB.

## 2026-05-13 — OPT-WET-v1 official global ILAMB
- Generate command: `.venv/bin/python scripts/generate_candidate_output.py models/C/candidate_search/optuna_extension_search_500_trials.json OPT-WET-v1`
- Evaluation command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_opt_wet_v1" bash scripts/run_ilamb.sh`
- Output directory: `ilamb/output_modelC_opt_wet_v1`
- Scores: Bias 0.730475; RMSE 0.506667; Seasonal Cycle 0.845975; Spatial Distribution 0.768628; Overall 0.671682; Period Mean 0.567266.
- Evidence: yes.
- Best-so-far: scalar global improves baseline by +0.000153 but not accepted without regional/public checks.

## 2026-05-13 — OPT-WET-v1 official regional ILAMB
- Command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_opt_wet_v1" bash scripts/run_official_regions.sh`
- Output directory: `ilamb/output_regions_opt_wet_v1`
- Overall by region: global 0.671682; bona 0.789846; tena 0.385376; ceam 0.390151; nhsa 0.615769; shsa 0.523734; euro 0.362691; mide 0.383155; nhaf 0.644780; shaf 0.643856; boas 0.728889; ceas 0.670949; seas 0.501714; eqas 0.559410; aust 0.669073.
- Evidence: yes.
- Decision impact: rejected as final due Spatial decline and NHAF/SHAF/AUST damage despite humid-region gains.

## 2026-05-13 — LAG-FUEL-v1 official global ILAMB
- Generate command: `.venv/bin/python scripts/generate_candidate_output.py models/C/candidate_search/lag_fuel_v1.json LAG-FUEL-v1`
- Evaluation command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_lag_fuel_v1" bash scripts/run_ilamb.sh`
- Output directory: `ilamb/output_modelC_lag_fuel_v1`
- Scores: Bias 0.728075; RMSE 0.505767; Seasonal Cycle 0.848154; Spatial Distribution 0.771532; Overall 0.671859; Period Mean 0.622335.
- Evidence: yes.
- Best-so-far: highest official global scalar candidate in this run; held for regional/public judgement.

## 2026-05-13 — LAG-FUEL-v1 official regional ILAMB
- Command: `ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_lag_fuel_v1" bash scripts/run_official_regions.sh`
- Output directory: `ilamb/output_regions_lag_fuel_v1`
- Overall by region: global 0.671859; bona 0.789821; tena 0.380150; ceam 0.376246; nhsa 0.605964; shsa 0.507244; euro 0.359154; mide 0.376307; nhaf 0.644954; shaf 0.645814; boas 0.728294; ceas 0.669553; seas 0.482934; eqas 0.507431; aust 0.676252.
- Evidence: yes.
- Decision impact: rejected as final because it harms multiple weak/important regions despite best global scalar score.

## 2026-05-13 — LAG-FUEL-v1 public TRENDY/firepipe
- Command: `TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" MODEL_NAME="ED-ModelC-lag-fuel-v1-current" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-v1-current" bash scripts/run_public_trendy_firepipe.sh`
- Output directory: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-v1-current`
- Score: public Overall 0.671600; rank #1 in current run.
- Warning: JSBACH `IndexError`, documented benchmark caveat; score table completed.
- Evidence: yes.

## 2026-05-13 — OPT-WET-v1 public TRENDY/firepipe
- Command: same wrapper with `MODEL_NAME="ED-ModelC-opt-wet-v1-current"`, output `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-opt-wet-v1-current`
- Score: public Overall 0.671436; rank below LAG-FUEL-v1 and above baseline/current TRENDY comparators in the run.
- Warning: JSBACH `IndexError`, documented caveat; score table completed.
- Evidence: yes.

## 2026-05-13 — baseline public TRENDY/firepipe and final restoration
- Restoration command: `.venv/bin/python scripts/reproduce_modelC.py`
- Public command: same wrapper with `MODEL_NAME="ED-ModelC-baseline-current"`, output `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-baseline-current`
- Public baseline score: Overall 0.671274.
- Warning: JSBACH `IndexError`, documented caveat; score table completed.
- Verification command: `.venv/bin/python scripts/verify.py`
- Verification result: PASS.
- Evidence: yes; final artifact state restored to original Model C.


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
