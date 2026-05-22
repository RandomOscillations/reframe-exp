# Evaluation Log

## Baseline / original Model C

### Verification
Command: `.venv/bin/python scripts/verify.py`
Result: exit code 1 because generated artifacts differed from pinned sizes; all fixed inputs and params matched.

Mismatches before regeneration:
- ilamb/MODELS/ED-ModelC-final/burntArea.nc: expected 13,600,931 bytes, got 13,466,737 bytes.
- out_terms/modelC_terms.nc: expected 112,006,460 bytes, got 116,077,308 bytes.

### Regeneration
Command: `.venv/bin/python scripts/reproduce_modelC.py`
Artifact: ilamb/MODELS/ED-ModelC-final/burntArea.nc
Diagnostics:
- land cells: 13826 / 64800
- raw rate land mean: 0.09018 yr^-1
- max raw rate: 0.9987 yr^-1
- ED-transformed land mean: 0.00610759
- GFED land mean: 0.00298745
- ratio: 2.044

### Official global ILAMB
Command:
`PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb bash scripts/run_ilamb.sh`
Output: ilamb/output_modelC/scalar_database.csv

Scores, ED-ModelC-final, global:
- Bias Score: 0.7281
- RMSE Score: 0.5058
- Seasonal Cycle Score: 0.8457
- Spatial Distribution Score: 0.7724
- Overall Score: 0.6715

### Official regional ILAMB
Command:
`PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_modelC_regions --skip_plots`
Output: ilamb/output_modelC_regions/scalar_database.csv

Regional diagnostic overall computed for triage only: `(2*Bias + 2*RMSE + Seasonal + Spatial)/6`.

| Region | Bias | RMSE | Seasonal | Spatial | Diagnostic overall |
|---|---:|---:|---:|---:|---:|
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3613 |
| euro | 0.3935 | 0.2618 | 0.8082 | 0.0805 | 0.3665 |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3907 |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3918 |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4887 |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5016 |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5024 |
| nhsa | 0.5014 | 0.4931 | 0.9144 | 0.6270 | 0.5884 |
| shaf | 0.7597 | 0.5023 | 0.9021 | 0.5671 | 0.6655 |
| nhaf | 0.7693 | 0.4795 | 0.9010 | 0.5998 | 0.6664 |
| global | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6810 |
| aust | 0.7456 | 0.6520 | 0.5795 | 0.7219 | 0.6828 |
| ceas | 0.7834 | 0.5603 | 0.7222 | 0.7265 | 0.6893 |
| boas | 0.8408 | 0.6192 | 0.7966 | 0.7679 | 0.7474 |
| bona | 0.8840 | 0.7425 | 0.9251 | 0.6549 | 0.8055 |

### Clean public TRENDY/firepipe comparison for current baseline
Command: `MODEL_NAME=ED-ModelC-current SRC=$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc PATH=$PWD/.venv/bin:$PATH bash scripts/run_public_trendy_firepipe_clean.sh`
Output: public_benchmark_clean/ilamb/output_with_ED-ModelC-current/scalar_database.csv
Note: JSBACH pair emitted IndexError but run completed and other model scores were written.

Global ranking by diagnostic weighted formula from scalar components:
1. ED-ModelC-baseline 0.6850
2. ED-ModelC-current 0.6807
3. CLASSIC 0.6781
4. CLM6.0 0.6770
5. CLM-FATES 0.6682
6. ELM-FATES 0.6680


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


## Continuation official evaluations

### Second-order candidates
Search script: `scripts/explore_second_order_candidates.py`; 500 Optuna trials/family.
Official global/regional output: `ilamb/output_cand2_regions/scalar_database.csv`.
Diagnostic global aggregation `(2*Bias + 2*RMSE + Seasonal + Spatial)/6`:
- ED-ModelC-final: Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, diagnostic Overall 0.680956.
- ED-Cand2-curing_window: 0.731057, 0.509633, 0.852393, 0.784664, diagnostic Overall 0.686406.
- ED-Cand2-hyperarid_balance: 0.733480, 0.511027, 0.845278, 0.767490, diagnostic Overall 0.683630.
- ED-Cand2-wet_supp_fuel_release: 0.729842, 0.508530, 0.852045, 0.771495, diagnostic Overall 0.683381.
- ED-Cand2-wet_x_lowdef: 0.731856, 0.508472, 0.847305, 0.765821, diagnostic Overall 0.682297.
- ED-Cand2-gpp_wet_cap: 0.731029, 0.507915, 0.848006, 0.767326, diagnostic Overall 0.682203.
- ED-Cand2-wet_x_persist: 0.731445, 0.508261, 0.847629, 0.765940, diagnostic Overall 0.682164.

### Curing-window ablations
Script: `scripts/ablate_curing_window.py`.
Official global output: `ilamb/output_curing_ablations_global/scalar_database.csv`.
- ED-Cand2Abl-no_drydown: diagnostic Overall 0.686854; Bias 0.731278, RMSE 0.509570, Seasonal 0.853537, Spatial 0.785892.
- ED-Cand2Abl-no_gpp_window: 0.686434; Bias 0.730685, RMSE 0.510280, Seasonal 0.847757, Spatial 0.788917.
- ED-Cand2Abl-full / ED-Cand2-curing_window: 0.686406.
- ED-Cand2Abl-pulse_no_exp: 0.685176.
- ED-Cand2Abl-exp_only: 0.680994, essentially Model C, showing the gain is not just exponent rescale.

### Focused release-window search
Search script: `scripts/explore_release_window.py`; 500 Optuna trials/family.
Official regional output: `ilamb/output_cand3_regions/scalar_database.csv`.
- ED-Cand3-release_window_wetcap: Bias 0.731876, RMSE 0.509663, Seasonal 0.852544, Spatial 0.789014, diagnostic Overall 0.687439.
- ED-Cand3-release_window: Bias 0.732075, RMSE 0.509868, Seasonal 0.848606, Spatial 0.787036, diagnostic Overall 0.686588.
- ED-Cand2Abl-no_drydown: diagnostic Overall 0.686854.
- ED-ModelC-final: diagnostic Overall 0.680956.

### Public clean comparisons
- ED-Cand2-curing_window public output: `public_benchmark_clean/ilamb/output_with_ED-Cand2-curing_window/scalar_database.csv`, Overall 0.677232.
- ED-Cand2Abl-no_drydown public output: `public_benchmark_clean/ilamb/output_with_ED-Cand2Abl-no_drydown/scalar_database.csv`, Overall 0.677726.
- ED-Cand3-release_window_wetcap public output: `public_benchmark_clean/ilamb/output_with_ED-Cand3-release_window_wetcap/scalar_database.csv`, Overall 0.678312. This ranked #1 in the clean public run, ahead of ED-ModelC-baseline 0.675085, ED-ModelC-current 0.671274, CLASSIC 0.666048, and CLM6.0 0.660644. JSBACH retained the known IndexError caveat.
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
## 2026-05-19 00:03:05 continuation cycle 2 evaluation record
### Third-cycle official ILAMB
Command: `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --models ED-ModelC-final ED-Cand3-release_window_wetcap ED-Cand4-senescence_release ED-Cand4-dual_corridor_balance ED-Cand4-guarded_release --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_cand4_regions --skip_plots`
Output: `ilamb/output_cand4_regions/scalar_database.csv`.
Global diagnostics: Cand3 0.687439; senescence 0.687211; dual_corridor 0.686084; guarded 0.685694; Model C 0.680956.

### Pareto official ILAMB
Command: `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --models ED-ModelC-final ED-Cand3-release_window_wetcap ED-Cand4-pareto_guarded_corridor ED-Cand4-pareto_senescence_corridor --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_pareto_regions --skip_plots`
Output: `ilamb/output_pareto_regions/scalar_database.csv`.
Global diagnostics: pareto_guarded 0.688961; pareto_senescence 0.687464; Cand3 0.687439; Model C 0.680956.

### Pareto ablation official ILAMB
Command: `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --models ED-Cand4-pareto_guarded_corridor ED-Cand4Abl-no_guard ED-Cand4Abl-no_arid ED-Cand4Abl-no_hotboost ED-Cand4Abl-no_wetcap --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_pareto_ablation_regions --skip_plots`
Output: `ilamb/output_pareto_ablation_regions/scalar_database.csv`.
Global diagnostics: full 0.688961; no_guard 0.688355; no_arid 0.683534; no_hotboost 0.688962; no_wetcap 0.687848.

### Public clean benchmark
Commands: `MODEL_NAME=ED-Cand4-pareto_guarded_corridor SRC=$PWD/ilamb/MODELS/ED-Cand4-pareto_guarded_corridor/burntArea.nc PATH=$PWD/.venv/bin:$PATH bash scripts/run_public_trendy_firepipe_clean.sh` and `MODEL_NAME=ED-Cand4Abl-no_hotboost SRC=$PWD/ilamb/MODELS/ED-Cand4Abl-no_hotboost/burntArea.nc PATH=$PWD/.venv/bin:$PATH bash scripts/run_public_trendy_firepipe_clean.sh`.
Outputs: `public_benchmark_clean/ilamb/output_with_ED-Cand4-pareto_guarded_corridor/scalar_database.csv` and `public_benchmark_clean/ilamb/output_with_ED-Cand4Abl-no_hotboost/scalar_database.csv`.
Clean public Overall ranking: ED-Cand4Abl-no_hotboost 0.679480; ED-Cand4-pareto_guarded_corridor 0.679479; ED-Cand3-release_window_wetcap 0.678312; ED-Cand2Abl-no_drydown 0.677726; ED-Cand2-curing_window 0.677232; ED-ModelC-baseline 0.675085; ED-ModelC-current 0.671274; CLASSIC 0.666048; CLM6.0 0.660644. JSBACH retained the known IndexError caveat during public runs.


## 2026-05-19 01:26:21 continuation cycle 3 evaluation record
### Cycle-5 official ILAMB
Command: `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/public_benchmark_clean/ilamb ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --models ED-ModelC-final ED-Cand3-release_window_wetcap ED-Cand4Abl-no_hotboost ED-Cand5-monsoon_break_release ED-Cand5-mosaic_edge_release ED-Cand5-protected_corridor --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_cand5_regions --skip_plots`.
Output: `ilamb/output_cand5_regions/scalar_database.csv`.

| Model | Bias | RMSE | Seasonal | Spatial | Diagnostic |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.680956 |
| ED-Cand3-release_window_wetcap | 0.731876 | 0.509663 | 0.852544 | 0.789014 | 0.687439 |
| ED-Cand4Abl-no_hotboost | 0.735210 | 0.511005 | 0.846055 | 0.795285 | 0.688962 |
| ED-Cand5-monsoon_break_release | 0.731848 | 0.510109 | 0.847982 | 0.783724 | 0.685937 |
| ED-Cand5-mosaic_edge_release | 0.733281 | 0.512082 | 0.853194 | 0.783297 | 0.687870 |
| ED-Cand5-protected_corridor | 0.732924 | 0.511487 | 0.850344 | 0.784580 | 0.687291 |

### Mosaic ablations and edge-mix sweep
Official ablation output: `ilamb/output_cand5_ablation_regions/scalar_database.csv`.
Official sweep output: `ilamb/output_cand5_edge_sweep_regions/scalar_database.csv`.

| Model | Bias | RMSE | Seasonal | Spatial | Diagnostic |
|---|---:|---:|---:|---:|---:|
| ED-Cand5-mosaic_edge_release | 0.733281 | 0.512082 | 0.853194 | 0.783297 | 0.687870 |
| ED-Cand5Abl-no_edge_mix | 0.732520 | 0.511578 | 0.853499 | 0.790195 | 0.688648 |
| ED-Cand5Abl-no_cap_relief | 0.733284 | 0.512084 | 0.853194 | 0.783295 | 0.687871 |
| ED-Cand5Abl-no_arid | 0.731478 | 0.510680 | 0.853226 | 0.782734 | 0.686713 |
| ED-Cand5Abl-no_cold_guard | 0.731396 | 0.510507 | 0.853362 | 0.789733 | 0.687817 |
| ED-Cand5Sweep-edgefrac_0p50 | 0.733009 | 0.511882 | 0.853270 | 0.787890 | 0.688490 |

### Public clean benchmark additions
- `ED-Cand5Abl-no_edge_mix`: 0.679633, public rank #1 in its clean run.
- `ED-Cand5Sweep-edgefrac_0p50`: 0.679346.
- `ED-Cand5-mosaic_edge_release`: 0.678548.
- `ED-Cand5-monsoon_break_release`: 0.676513 (output present in later public run table after the timed command completed enough to write scalars).
Known JSBACH IndexError caveat persisted as in prior public runs.
