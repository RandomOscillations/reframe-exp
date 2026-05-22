# Research Log

## 2026-05-21 Initial setup and baseline
- Read required workspace instructions and baseline docs: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, README.md, WRITEUP.md, models/C/formula.md.
- Constraint interpretation: one global mechanistic formula under fixed input contract; no external inputs, lat/lon hacks, named-region routing, lookup tables, residual correction, or per-region formulas.
- Ran `.venv/bin/python scripts/verify.py`. All input data and params matched pinned checksums. Existing generated artifacts differed in file size before regeneration: `ilamb/MODELS/ED-ModelC-final/burntArea.nc` expected 13600931 got 13628344; `out_terms/modelC_terms.nc` expected 112006460 got 116077308. This was recorded before proceeding.
- Ran `.venv/bin/python scripts/reproduce_modelC.py`, regenerating `ilamb/MODELS/ED-ModelC-final/burntArea.nc` from original Model C params. Diagnostics: land cells 13826 / 64800; raw land-mean rate 0.09018 yr-1; max raw rate 0.9987; ED-transformed land mean 0.00610759 vs GFED 0.00298745, ratio 2.044.
- First `bash scripts/run_ilamb.sh` failed because `ilamb-run` was not on PATH. Re-ran with `.venv/bin` on PATH; then ILAMB required `ILAMB_ROOT`. Official successful run used `ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH bash scripts/run_ilamb.sh`.
- Official global ILAMB baseline reproduced in `ilamb/output_modelC`: Bias 0.7281, RMSE 0.5058, Seasonal 0.8457, Spatial 0.7724, Overall 0.6715.
- Built and ran official regional ILAMB command with built-in GFED regions: `ilamb/output_modelC_regions`.
- Created `scripts/summarize_ilamb_scores.py` and `scripts/summarize_any_ilamb.py` to tabulate scalar_database.csv.
- Created `scripts/fire_explore.py` for constrained candidate exploration: loads only allowed inputs, mirrors Model C, supports annual humid suppression / wet-month logistic / seasonal contrast / combined global mechanisms, tunes with Optuna, writes TRENDY-format NetCDF, and computes proxy diagnostics. This is a research helper; candidate acceptance remains based on official ILAMB.

## 2026-05-21 Failure triage
- Official regional ILAMB shows strongest weak regions by Overall: Europe 0.3611, Central America 0.3762, Temperate North America 0.3815, Middle East 0.3828, Southeast Asia 0.4872, Southern Hemisphere South America 0.5072, Equatorial Asia 0.5074.
- Failure mode is not seasonality-dominated: many weak regions still have high Seasonal scores. Main failures are low Bias/RMSE and especially low Spatial Distribution in low-fire/humid/fragmented regions (e.g. Europe spatial 0.0805, Middle East 0.0912, Central America 0.1256, Temperate North America 0.1603, Equatorial Asia 0.1771).
- Proxy diagnostic using 1-degree mass-weighted means also indicates Model C often overpredicts weak regions relative to GFED, especially MIDE/TENA/EURO/CEAM/EQAS/SEAS/SHSA, while Africa and Australia are much better calibrated.

## 2026-05-21 Mechanism family 1: annual humid suppression / precipitation hump
- Hypothesis: Model C's annual precipitation term is only a floor (`P_ann/(P_ann+P_half)`) and lacks a high-rainfall/no-dry-fuel suppression. GPP hump partly suppresses wet forests, but official regional failures in EQAS/CEAM/SEAS and spatial failures in wet/fragmented regions suggest missing pyrogeographic upper precipitation limb.
- Candidate mechanism: multiply the global formula by `1 / (1 + (P_ann / P_humid)^P_humid_q)`, a smooth high-annual-precipitation suppression. This is one global mechanism using allowed precipitation only; no region routing.
- Ran Optuna search with 500 full-field proxy trials, tuning selected base parameters plus new humid suppression params. Best proxy params saved to `artifacts/candidate_annual_humid_supp_500.json`; candidate H1 written to `models/H1_annual_humid_supp/params.json` and `ilamb/MODELS/ED-H1-annual-humid-supp/burntArea.nc`.
- Official result H1: global Overall 0.6384. Regional weak areas improved strongly (EQAS 0.6801, SHSA 0.6404, EURO 0.5173), but global Spatial collapsed to 0.5837. Rejected.
- Ablation H1m held Model C base fixed and added mild suppression (`P_humid=1500`, `q=0.5`) selected from deterministic grid. Official global Overall 0.6538, still too much global/spatial loss. Rejected.

## 2026-05-21 Mechanism family 2: wet-month logistic suppression
- Hypothesis: Model C's monthly precipitation hyperbola may not shut off burning sharply enough during wet months, causing overprediction in monsoon/humid regions.
- Candidate mechanism: add `supp(P_month; wet_k, wet_c)` as a global wet-fuel/current-rain suppression.
- Deterministic grid over wet_k/wet_c on fixed base selected wet_k=0.1, wet_c=20 by proxy. Official H2 result: global Overall 0.6534, Seasonal improves slightly to 0.8521 but Spatial falls to 0.6524. Weak-region gains are real (e.g. EQAS 0.6268, EURO 0.4932), but the global spatial tradeoff is unacceptable. Rejected.

## 2026-05-21 Mechanism family 3: seasonal contrast / curing gate
- Hypothesis: absolute monthly precipitation is less portable than dryness relative to local annual precipitation; fires occur when current month is dry relative to local climate.
- Candidate mechanism: add `1/(1+(P_month/(P_ann/12+eps))^q)`, a global seasonal-curing contrast gate.
- Deterministic grid selected eps=0.5, q=0.25 by proxy. Official H3 result: global Overall 0.6654, Bias 0.7304, RMSE 0.5110, Seasonal 0.8480, Spatial 0.7267. This is the best regional-compromise candidate but still loses to C0 (0.6715), primarily by Spatial Distribution.
- Clean public benchmark for H3: Overall 0.6652, below Model C 0.6713 and CLASSIC 0.6660, above CLM6.0 0.6606. Rejected as final, but recorded as an interpretable alternative if regional weak-area uplift is preferred over global rank.

## 2026-05-21 Stopping rationale
- Explored three distinct mechanistic precipitation/curing families motivated by failure triage. All improve weak regional bias/overall, so the diagnosis is plausible.
- The same mechanisms consistently damage global Spatial Distribution, especially boreal/Africa/Australia patterns that drive the original rank-1 behavior.
- The empirical ceiling under the fixed five-input contract appears to be original Model C for global/public ranking. Remaining failures likely require omitted mechanisms unavailable in the contract: human land use/suppression/ignition, cropland/pasture fragmentation, peat/deforestation fire type, lightning/human ignitions, fuel continuity and vegetation structure.
