# Research Log

## 2026-05-18 prerequisite reading and baseline setup
- Read required files before modifications: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, README.md, WRITEUP.md, models/C/formula.md.
- Constraint understanding: one global mechanistic formula, fixed input contract only, no external inputs, no lat/lon hacks, no named-region routing, no per-cell lookup/residual correction, no prior experiment/archive evidence.
- Structural analogy framing to guide hypotheses: burned area behaves like a reliability/epidemic/combustion chain where ignition requires simultaneous susceptible fuel, transmission/weather contact, and non-suppressed moisture state. Like F1 pit work translated to neonatal handover, the transferable structure is not the domain content but the synchronized bottleneck: if any gate is mistimed, regional failure appears even if global aggregate is strong.

## Baseline reproduction
- `scripts/verify.py` found all pinned inputs present but two generated artifacts differed in file size before regeneration:
  - ilamb/MODELS/ED-ModelC-final/burntArea.nc expected 13,600,931 bytes, found 13,466,737 bytes.
  - out_terms/modelC_terms.nc expected 112,006,460 bytes, found 116,077,308 bytes.
  This was recorded as required by BASELINE_REPRO.md. Input arrays and params matched pinned hashes.
- Regenerated original Model C with `.venv/bin/python scripts/reproduce_modelC.py`.
  - raw rate land-mean 0.09018 yr^-1, max 0.9987, ED transformed land mean 0.00610759 vs GFED 0.00298745 (ratio 2.044).
- Official global ILAMB initially failed because `ilamb-run` was not on PATH and ILAMB_ROOT was unset; rerun with `PATH=$PWD/.venv/bin:$PATH` and `ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb` succeeded.

## Baseline scores
- Official global ILAMB output: ilamb/output_modelC/scalar_database.csv
- Model C current official global scores:
  - Bias Score 0.7281
  - RMSE Score 0.5058
  - Seasonal Cycle Score 0.8457
  - Spatial Distribution Score 0.7724
  - Overall Score 0.6715
- Official regional ILAMB run completed with GFED regions using output: ilamb/output_modelC_regions/scalar_database.csv. ILAMB does not emit a regional Overall scalar in this run; I compute a diagnostic tier-style regional overall as `(2*Bias + 2*RMSE + Seasonal + Spatial)/6` for triage only.

## Baseline regional failure triage
Worst diagnostic regional overalls are Central America, Europe, Temperate North America, Middle East, Southeast Asia, Southern Hemisphere South America, and Equatorial Asia. The dominant issue in these weak regions is very low spatial distribution score, with low bias/RMSE in several regions; seasonal phase is generally strong except Australia, Temperate North America, Central Asia.

Mechanistic implications:
- Model C is globally strong because it captures timing/seasonality and African/savanna fire belts.
- Weak regions suggest missing heterogeneity in fuel continuity / human-fragmented agricultural burning / forest-moisture suppression, but those must be represented only through allowed physical proxies (GPP, precipitation, temperature, dryness and their temporal transforms), not region names or coordinates.
- Candidate families should target transferable cell-level regimes: antecedent fuel charging, dry-down/curing dynamics, closed-canopy wet forest suppression, and asymmetric productivity response.


## Mechanism family search results

Screened with `scripts/explore_fire_candidates.py` using 500 Optuna trials per family unless noted. The fast proxy deliberately combined global fit with weak-region diagnostics, then serious/promising candidates were promoted to official ILAMB.

Fast screening summary:
- C_reopt: fast objective 0.573881; fast global 0.626112; raw land mean 0.068912.
- annual_p_hump: fast objective 0.571907; fast global 0.617062; raw land mean 0.052945.
- wetforest_curing: fast objective 0.567909; fast global 0.622108; raw land mean 0.071295.
- drydown_curing: fast objective 0.567601; fast global 0.629550; selected a near-neutral drydown effect, effectively pruning itself.
- antecedent_fuel: fast objective 0.567219; fast global 0.615867.
- fuel_moisture_balance: fast objective 0.559874; fast global 0.597305.

Official global ILAMB for promoted candidates (ilamb/output_candidates_global_full/scalar_database.csv):
- ED-ModelC-final: Overall 0.671529; Bias 0.728089; RMSE 0.505759; Seasonal 0.845690; Spatial 0.772351.
- ED-Cand-Creopt: Overall 0.665583; Bias/RMSE slightly higher but Spatial fell to 0.732615.
- ED-Cand-WetForestCuring: Overall 0.661118; Spatial 0.719458.
- ED-Cand-AnnualPHump: Overall 0.653225; Spatial 0.665412.
- ED-Cand-AnteFuel: Overall 0.652335; Spatial 0.685066.

Partial wet-suppression ablation:
- Script: scripts/scan_partial_wet_suppression.py
- Grid: P_wet in [1200,1600,2000,2600,3200,4000,6000,10000], pow in [0.25,0.5,0.75,1,1.5,2,3], floor in [0.70,0.80,0.85,0.90,0.93,0.95,0.97,0.99,1.0]. Floor=1 is exact baseline ablation.
- Selected constrained candidate: P_wet=2000, pow=0.25, floor=0.70 based on fast proxy within 0.001 of baseline and better weak-region mean.
- Official global ILAMB: ED-Cand-PartialWetSupp Overall 0.669509 vs C0 0.671529. Bias/RMSE/Seasonal slightly improve, Spatial falls 0.772351 -> 0.759868.
- Official regional diagnostic deltas vs C0: SHSA +0.0169, NHSA +0.0146, EURO +0.0145, EQAS +0.0133, CEAM +0.0123, SEAS +0.0122, TENA +0.0117, MIDE +0.0079; SHAF -0.0090, NHAF -0.0071, BONA -0.0032.
- Clean public benchmark: ED-Cand-PartialWetSupp Overall 0.669258, behind ED-ModelC-baseline 0.675085 and ED-ModelC-current 0.671274 but ahead of CLASSIC 0.666048 in that run. JSBACH emitted the same IndexError caveat as previous public runs.

Stopping assessment:
The explored families produce coherent regional repairs in exactly the initially weak regions, which supports the physical diagnosis, but all repairs reduce official global Spatial Distribution enough to lose Overall. Since the incumbent is already near the public benchmark ceiling, the remaining failures appear tied to heterogeneity not identifiable under the fixed climate/GPP contract without land-use/human/vegetation-structure inputs or forbidden routing.

## 2026-05-18 continuation cycle: second-order mechanisms
- Continued after prior final_report as requested. Re-read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, research_log.md, eval_log.md, regional_analysis.md, candidate_registry.md, constraint_checks.md, and final_report.md before changing code. Also re-read README.md, WRITEUP.md, models/C/formula.md, scripts/explore_fire_candidates.py, and scripts/scan_partial_wet_suppression.py.
- Carried forward first-cycle failure learning: blunt wet suppression repaired weak regions but reduced global Spatial; antecedent fuel charging repaired some weak regions but damaged African/boreal fire belts; naked drydown was pruned.
- New structural analogy: use multi-factor interlocks, like a circuit breaker or reservoir spillway: second-order gates should trip only when multiple physical states coincide, preserving the synchronized bottleneck that gives Model C its spatial skill.
- Created scripts/explore_second_order_candidates.py to test fixed-Model-C second-order global interaction terms with 500 Optuna trials/family: wet_x_lowdef, wet_x_persist, wet_supp_fuel_release, gpp_wet_cap, hyperarid_balance, curing_window. These use only allowed inputs/transforms and GFED only for screening.


## Continuation results: second-order and focused searches
- Second-order search families completed with 500 Optuna trials each: wet_x_lowdef, wet_x_persist, wet_supp_fuel_release, gpp_wet_cap, hyperarid_balance, curing_window.
- All six improved the official global diagnostic aggregation over Model C in `ilamb/output_cand2_regions/scalar_database.csv`. The best first-stage family was `ED-Cand2-curing_window`: Bias 0.731057, RMSE 0.509633, Seasonal 0.852393, Spatial 0.784664, diagnostic Overall 0.686406 vs Model C 0.680956.
- Mechanism learning: the useful signal was not first-cycle wet suppression by itself. The gain came from a second-order fuel-release/intermediate-regime boost that preserved and improved Spatial, while wet-only caps mostly repaired weak regions but had smaller global benefit.
- Ablated `ED-Cand2-curing_window` in `scripts/ablate_curing_window.py`. Official global ablations showed `no_drydown` slightly exceeded the full curing pulse: diagnostic Overall 0.686854 vs 0.686406. This prunes month-to-month drydown as an unnecessary part of the final mechanism; current dryness in a precip/GPP window is enough.
- Focused search `scripts/explore_release_window.py` tested `release_window` and `release_window_wetcap` with 500 Optuna trials each. The best final candidate is `ED-Cand3-release_window_wetcap`: official global diagnostic Overall 0.687439, Bias 0.731876, RMSE 0.509663, Seasonal 0.852544, Spatial 0.789014. Public clean Overall 0.678312, ranking #1 in the clean public run above ED-ModelC-baseline 0.675085 and ED-ModelC-current 0.671274.
- Final refinement attempt `scripts/explore_release_window_temp.py` added a temperature interlock to protect BONA. It failed screening: fast global Overall 0.630843 and Spatial 0.752146, so it was rejected without official promotion.
- Structural analogy used in the continuation: a reservoir/circuit-breaker system. First-cycle failures showed single gates were too blunt. The successful mechanism requires multiple interlocks: current dry state, intermediate annual precipitation, intermediate GPP/fuel, and a soft wet-low-deficit cap.
### 2026-05-18 21:31:57 — background wet_x_persist rerun completion
- Background process proc_604babcfe677 completed successfully: `scripts/explore_second_order_candidates.py --family wet_x_persist --trials 500 --seed 20260520 --write-nc`.
- It refreshed `models/explore2/wet_x_persist/result.json` and `burntArea.nc` with the same 500-trial/seed screening setup: fast objective 0.539973, fast global Overall 0.631493, weak_mean 0.356031, strong_min 0.550853.
- This is a screening artifact refresh only. The official ILAMB diagnostic score already recorded for `ED-Cand2-wet_x_persist` remains from `ilamb/output_cand2_regions/scalar_database.csv`: diagnostic Overall 0.682164. No change to final recommendation (`ED-Cand3-release_window_wetcap`).
### 2026-05-18 21:32:24 — background gpp_wet_cap rerun completion
- Background process proc_e357446cc625 completed successfully: `scripts/explore_second_order_candidates.py --family gpp_wet_cap --trials 500 --seed 20260520 --write-nc`.
- It refreshed `models/explore2/gpp_wet_cap/result.json` and `burntArea.nc` with the same 500-trial/seed screening setup: fast objective 0.539553, fast global Overall 0.631492, weak_mean 0.352526, strong_min 0.550942.
- This is a screening artifact refresh only. The official ILAMB diagnostic score already recorded for `ED-Cand2-gpp_wet_cap` remains from `ilamb/output_cand2_regions/scalar_database.csv`: diagnostic Overall 0.682203. No change to final recommendation (`ED-Cand3-release_window_wetcap`).
### 2026-05-18 21:32:49 — background hyperarid_balance rerun completion
- Background process proc_530703d37919 completed successfully: `scripts/explore_second_order_candidates.py --family hyperarid_balance --trials 500 --seed 20260520 --write-nc`.
- It refreshed `models/explore2/hyperarid_balance/result.json` and `burntArea.nc` with the same 500-trial/seed screening setup: fast objective 0.546580, fast global Overall 0.633797, weak_mean 0.358200, strong_min 0.560253.
- This is a screening artifact refresh only. The official ILAMB diagnostic score already recorded for `ED-Cand2-hyperarid_balance` remains from `ilamb/output_cand2_regions/scalar_database.csv`: diagnostic Overall 0.683630. No change to final recommendation (`ED-Cand3-release_window_wetcap`).
### 2026-05-18 21:33:21 — background curing_window rerun completion
- Background process proc_deff3fd1635d completed successfully: `scripts/explore_second_order_candidates.py --family curing_window --trials 500 --seed 20260520 --write-nc`.
- It refreshed `models/explore2/curing_window/result.json` and `burntArea.nc` with the same 500-trial/seed screening setup: fast objective 0.543191, fast global Overall 0.635044, weak_mean 0.342343, strong_min 0.553762.
- This is a screening artifact refresh only. The official ILAMB diagnostic score already recorded for `ED-Cand2-curing_window` remains from `ilamb/output_cand2_regions/scalar_database.csv`: diagnostic Overall 0.686406. The previously logged ablation still found `no_drydown` slightly better at 0.686854, so drydown remains pruned as unnecessary. No change to final recommendation (`ED-Cand3-release_window_wetcap`).
### 2026-05-18 21:33:54 — background wet_supp_fuel_release rerun completion
- Background process proc_6080093c6449 completed successfully: `scripts/explore_second_order_candidates.py --family wet_supp_fuel_release --trials 500 --seed 20260520 --write-nc`.
- It refreshed `models/explore2/wet_supp_fuel_release/result.json` and `burntArea.nc` with the same 500-trial/seed screening setup: fast objective 0.541849, fast global Overall 0.632063, weak_mean 0.348484, strong_min 0.555423.
- This is a screening artifact refresh only. The official ILAMB diagnostic score already recorded for `ED-Cand2-wet_supp_fuel_release` remains from `ilamb/output_cand2_regions/scalar_database.csv`: diagnostic Overall 0.683381. No change to final recommendation (`ED-Cand3-release_window_wetcap`).
## 2026-05-18 21:42:17 continuation cycle 2: third-order mechanism design
- Re-read all user-required files before modifications: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, research_log.md, eval_log.md, regional_analysis.md, candidate_registry.md, constraint_checks.md, final_report.md. Also re-read README.md, WRITEUP.md, and models/C/formula.md.
- Current best-so-far inferred from logs: `ED-Cand3-release_window_wetcap`, official diagnostic global 0.687439 and public Overall 0.678312, with regional gains in 12/14 non-global regions but BONA -0.0120 and NHSA -0.0029.
- Carried forward failure learnings: blunt wet suppression repairs weak wet/temperate regions but loses global Spatial; fuel charging alone damages African/boreal belts; naked dbar drydown is prunable; a simple temperature activation interlock failed screening.
- New structural analogies used to define testable families: relay-protection grid (release gate with cold/short-season guard), supply-chain/F1 bottleneck synchronization (fuel, warmth, no recent rain, dryness all aligned), senescence/curing as live-fuel drawdown rather than dbar derivative, and combustion corridor balance between hyperarid fuel absence and wet-canopy nonflammability.
- Created `scripts/explore_third_order_candidates.py` with four one-global-formula families: `guarded_release`, `senescence_release`, `dual_corridor_balance`, and `warm_dry_supply_chain`. Inputs remain only dbar, annual/monthly precipitation, air temperature, and monthly GPP transforms; GFED is used only for screening.
## 2026-05-19 00:03:05 continuation cycle 2 completion: third-order and Pareto mechanisms
- Completed third-cycle 500-trial searches for `guarded_release`, `senescence_release`, `dual_corridor_balance`, and `warm_dry_supply_chain` with `scripts/explore_third_order_candidates.py`.
- Promoted serious third-cycle candidates to official global/regional ILAMB: `ED-Cand4-senescence_release`, `ED-Cand4-dual_corridor_balance`, and `ED-Cand4-guarded_release` in `ilamb/output_cand4_regions`.
- Official diagnostics: senescence 0.687211, dual-corridor 0.686084, guarded 0.685694 versus Cand3 0.687439 and Model C 0.680956. None beat Cand3 globally. Dual-corridor repaired weak regions most strongly but worsened BONA/African belts; senescence nearly tied Cand3 while improving NHSA/EURO/EQAS but worsened BONA/Africa.
- Built Pareto-focused refinement script `scripts/explore_pareto_release_candidates.py` from these failures. `pareto_guarded_corridor` screened best: fast global 0.637500, Spatial 0.778832, but weak mean 0.342409.
- Official ILAMB for Pareto candidates: `ED-Cand4-pareto_guarded_corridor` global diagnostic 0.688961, `ED-Cand4-pareto_senescence_corridor` 0.687464. The guarded corridor improves global diagnostics/public ranking but is not a broad regional Pareto improvement versus Cand3.
- Public clean benchmark: `ED-Cand4-pareto_guarded_corridor` Overall 0.679479, above Cand3 0.678312. Ablation pruned hotboost; `ED-Cand4Abl-no_hotboost` public Overall 0.679480 and official diagnostic 0.688962.
- Ablations of Pareto guarded: no_guard 0.688355, no_arid 0.683534, no_wetcap 0.687848, no_hotboost 0.688962. Hotboost is neutral/pruned; arid corridor and wet cap support global skill; guard modestly supports global/weak-region balance despite improving BONA when removed.
- Current evidence-based split: `ED-Cand4Abl-no_hotboost` is the global/public score leader, while `ED-Cand3-release_window_wetcap` remains the better broad regional-behavior candidate because it improves 12/14 named non-global regions over Model C versus 9/14 for Cand4Abl and Cand4Abl worsens NHSA/SHSA/SEAS/CEAM relative to Model C or Cand3.


## 2026-05-19 00:14:18 continuation cycle 3: post-Pareto failure triage and mechanism design
- Re-read all required files before modification: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, research_log.md, eval_log.md, regional_analysis.md, candidate_registry.md, constraint_checks.md, final_report.md; also README.md, WRITEUP.md, models/C/formula.md.
- Current evidence checkpoint is split: `ED-Cand4Abl-no_hotboost` leads global/public (official diagnostic 0.688962, public 0.679480), while `ED-Cand3-release_window_wetcap` remains the broad-regional compromise.
- Failure learning converted into next hypotheses: Cand4Abl loses NHSA/SHSA/SEAS/CEAM/TENA mostly through Spatial and Seasonal degradation; dual-corridor repairs weak regions but damages BONA/Africa; senescence repairs some humid/temperate regions but costs strong belts; hotboost and raw dbar drydown were pruned; blunt wet suppression loses Spatial.
- New analogies made concrete in `scripts/explore_cycle5_mechanisms.py`: monsoon supply-chain handoff (`monsoon_break_release`), fire-line/forest-edge mosaic (`mosaic_edge_release`), and power-grid protected corridor (`protected_corridor`). All remain one global formula using only allowed transformations of dbar, precipitation, temperature, and GPP; GFED remains screening/evaluation only.

## 2026-05-19 01:26:21 continuation cycle 3 completion: monsoon/mosaic/protected mechanisms
- Completed 500-trial Optuna searches for `monsoon_break_release`, `mosaic_edge_release`, and `protected_corridor` using `scripts/explore_cycle5_mechanisms.py`.
- Promoted all three to official global/regional ILAMB in `ilamb/output_cand5_regions`. Results: monsoon 0.685937, mosaic 0.687870, protected 0.687291, versus Cand3 0.687439 and Cand4Abl 0.688962.
- Main learning: monsoon/edge terms strongly repair the Cand4Abl regional losses (NHSA/SHSA/SEAS/CEAM/TENA/EURO), but the repair trades off BONA and African belts and gives up the Cand4Abl global peak.
- Ran mosaic ablations in `ilamb/output_cand5_ablation_regions`: no_edge_mix 0.688648, no_cap_relief 0.687871, no_arid 0.686713, no_cold_guard 0.687817. Wet-cap relief is effectively neutral; removing edge mix improves global/public but sacrifices NHSA/SHSA. Hyperarid/arid term remains useful globally. Cold guard protects global score but hurts NHSA/SHSA when removed.
- Deterministic edge-mix sweep in `ilamb/output_cand5_edge_sweep_regions` showed a Pareto continuum: edgefrac_0p00 global 0.688648; edgefrac_0p50 global 0.688490 and improves 12/14 regions vs Model C and 11/14 vs Cand3; edgefrac_1p00 global 0.687870 and improves 13/14 vs Model C but only 10/14 vs Cand3.
- Clean public results: `ED-Cand5Abl-no_edge_mix` public Overall 0.679633 (new public #1), `ED-Cand5Sweep-edgefrac_0p50` 0.679346, `ED-Cand5-mosaic_edge_release` 0.678548, `ED-Cand5-monsoon_break_release` 0.676513. JSBACH retained the known IndexError caveat.
- Evidence-based split after this cycle: public/global leader is now `ED-Cand5Abl-no_edge_mix`; best balanced global+regional Pareto compromise is `ED-Cand5Sweep-edgefrac_0p50`; strongest broad regional/weak-region repair is `ED-Cand5-mosaic_edge_release`/monsoon family, but not a global/public winner.
