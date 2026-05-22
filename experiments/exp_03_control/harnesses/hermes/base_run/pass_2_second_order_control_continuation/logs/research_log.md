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


## 2026-05-21 Continuation cycle: second-order mechanisms beyond precipitation-only gates
- Read current required logs/reports and treated previous pass as one completed cycle, not as endpoint. Best-so-far remained original C0 globally/publicly, with H3 only a regional-compromise alternative.
- Deepened allowed-input diagnostics in `artifacts/region_allowed_input_diagnostics.csv`. C0 overpredicts weak regions by large factors: MIDE 18.88x, TENA 14.88x, EURO 13.61x, CEAM 10.46x, EQAS 8.95x, SEAS 7.88x, SHSA 6.68x. These weak regions span very different allowed-state regimes: MIDE/AUST are both low-GPP drylands but AUST is well calibrated; EURO/TENA are cool productive mosaics; EQAS is very wet/high-GPP/low-deficit. This diagnostic warned that a single broad suppressor would likely damage already-good regimes.
- Extended `scripts/fire_explore.py` with second-order, still-global mechanism families using only allowed inputs: dry-gated annual humid suppression, dry-gated wet-month suppression, wet-productive-forest suppression, hyperarid low-fuel suppression, and cool-uncured temperature/dryness suppression. No region names, lat/lon, external data, or lookup tables were added.
- Ran completed 500-trial Optuna searches saved under `artifacts/search2/`:
  - `dry_gated_humid_500.json`: proxy global Overall 0.6523, weak mean 0.3848. Rejected before official because proxy spatial was poor (0.4328) and mechanism essentially became a broad low-deficit humid suppressor.
  - `dry_gated_wetmonth_500.json`: proxy global Overall 0.6878, weak mean 0.3722; promoted to official H4 because it looked like the best proxy continuation candidate.
  - `wet_productive_forest_500.json`: proxy global Overall 0.5927, weak mean 0.3845. Rejected before official; high-GPP/high-P/low-deficit forest proxy hurt seasonality/spatial too much.
- Official H4 (`ED-H4-dry-gated-wetmonth`) used wet-month suppression gated by low accumulated Dbar: `1 - alpha * lowdry(Dbar) * (1 - wet(P_month))`. It improved all weak-region Overalls relative to C0 (EURO 0.5148, CEAM 0.4707, TENA 0.4998, MIDE 0.4266, SEAS 0.5527, SHSA 0.6208, EQAS 0.6622), but global Overall fell to 0.6369 because Spatial Distribution collapsed to 0.5786. Rejected. H4 confirms that even physically gated wet suppression still warps the global spatial fire pattern.
- Explored additional distinct mechanism families after H4 failure:
  - `hyperarid_fuel_grid.json`: deterministic 64-point grid over low annual precipitation x low GPP fuel discontinuity. Best proxy global Overall 0.5525, weak mean 0.3240; rejected. Low-productivity suppression cannot distinguish MIDE failures from well-performing Australian drylands under the allowed inputs.
  - `cool_uncured_supp_500.json`: 500-trial Optuna temperature-ignition/dryness interaction. Best proxy global Overall 0.5684, weak mean 0.3443; rejected. It reduced some cool/moist overprediction but was not competitive.
  - `productivity_shape_grid.json`: deterministic 360-point grid retuning GPP/productivity shape plus fire exponent/monthly precipitation half-saturation. Best proxy global Overall 0.6185, weak mean 0.3477; rejected before official because it was weaker than H4 proxy and H4 failed official badly.
- Updated comparison artifact `artifacts/official_candidate_regional_scores_v2.csv` and summary `artifacts/search2/official_candidate_regional_scores_v2_summary.txt`.
- Continuation stopping evidence: precipitation-only, precipitation-curing, dry-gated wet suppression, wet productive forest, hyperarid fuel discontinuity, cool-uncured ignition interaction, and productivity-shape variants have now all been tested. The same empirical wall remains: weak-region magnitude improves only by suppressing cell states that overlap with regions/regimes responsible for C0 global spatial skill.
