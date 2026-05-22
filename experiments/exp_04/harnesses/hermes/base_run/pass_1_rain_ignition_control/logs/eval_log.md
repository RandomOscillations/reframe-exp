# Evaluation Log

## Baseline C0

Commands:
- `.venv/bin/python scripts/verify.py`
- `.venv/bin/python scripts/reproduce_modelC.py`
- `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/ilamb bash scripts/run_ilamb.sh`
- `PATH=$PWD/.venv/bin:$PATH ILAMB_ROOT=$PWD/ilamb ilamb-run --config ilamb/burntArea_official.cfg --model_root ilamb/MODELS --models ED-ModelC-final --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir ilamb/output_modelC_regions --skip_plots`

Verification:
- All input arrays, params, and GFED/GPP data present and hash-matched.
- Pre-existing generated files `ilamb/MODELS/ED-ModelC-final/burntArea.nc` and `out_terms/modelC_terms.nc` had size differences from CHECKSUMS.txt; baseline burntArea was regenerated before scoring.

Official global ILAMB (`ilamb/output_modelC/scalar_database.csv`):

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |

Regional components are in `ilamb/output_modelC_regions/scalar_database.csv`. Regional aggregate in regional_analysis.md is `(2*Bias + 2*RMSE + Seasonal + Spatial)/6` because regional scalar databases did not include an Overall Score row.

## Loop 1 C1 broad full-refit candidates

Official global ILAMB (`ilamb/output_C1_selected_global_full/scalar_database.csv`):

| Model | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---:|---:|---:|---:|---:|---|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | baseline |
| ED-C1-rain_temp_shift | 0.7303 | 0.5145 | 0.8243 | 0.7004 | 0.6568 | reject as global replacement; diagnostic regional improvement |
| ED-C1-annual_p_hump | 0.7303 | 0.5089 | 0.8361 | 0.6287 | 0.6426 | reject; spatial collapse |

C1 no-op/rejected without official rerun beyond identity:
- ED-C1-wet_gpp_supp selected wetgpp_amp=0; identical to C0.
- ED-C1-dry_season_gate selected dry_amp=0; identical to C0.
- ED-C1-base_refit selected original params; identical to C0.

## Loop 2 C2 targeted fixed-Model-C gates

Search script: `scripts/search_targeted_mechanisms.py`. Each targeted family held the Model C core fixed and tuned only the stated mechanism gate plus `rate_power` when allowed. 1000 Optuna trials per family.

Official global ILAMB:

| Model | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---:|---:|---:|---:|---:|---|
| ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.755836 | 0.675267 | best local official candidate |
| ED-C2-combined_wet_rain | 0.732270 | 0.519013 | 0.847854 | 0.747125 | 0.673055 | good but more complex and worse than rain-only |
| ED-C2-wet_gpp_amp | 0.735033 | 0.512834 | 0.848808 | 0.748156 | 0.671533 | essentially tied with C0; regional diagnostic |
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | baseline |
| ED-C2-annual_wet_amp | 0.733769 | 0.511839 | 0.846820 | 0.738642 | 0.668582 | reject as global replacement |

C2-rain_ignition_shift official regional diagnostics (`ilamb/output_C2_rainign_regions/scalar_database.csv`):
- Worst-region aggregate improvements vs C0: ceam 0.4281 vs 0.3613; euro 0.5335 vs 0.3665; tena 0.4652 vs 0.3907; mide 0.4249 vs 0.3918; seas 0.5151 vs 0.4887; shsa 0.5327 vs 0.5016; eqas 0.5598 vs 0.5024.
- Tradeoffs: nhaf 0.6748 vs 0.6664 slightly improves; shaf 0.6528 vs 0.6655 slightly worsens; global Spatial drops from 0.772351 to 0.755836.

C2-combined_wet_rain regional diagnostics:
- Similar regional gains, often slightly stronger than rain-only in ceam/mide/seas/eqas, but global Overall 0.673055 is lower and complexity is much higher.

## C2-rain ablations

Official global ILAMB (`ilamb/output_C2_ablation_global_full/scalar_database.csv`):

| Model | Bias | RMSE | Seasonal | Spatial | Overall | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.755836 | 0.675267 | accepted best |
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | baseline |
| ED-C2-ablate-rate_power_only | 0.713197 | 0.496505 | 0.846275 | 0.753624 | 0.661221 | rate power alone fails |
| ED-C2-ablate-rain_no_power | 0.726811 | 0.522298 | 0.849220 | 0.680497 | 0.660225 | rain ignition without rate power overcorrects spatial |

Ablation conclusion: the accepted improvement is not just the post-rate exponent and not just the rain-conditioned ignition replacement; the official gain requires the small rain-conditioned ignition mechanism plus retuned rate-power/intensity compression.

## Public TRENDY/firepipe comparison

Command:
`MODEL_NAME=ED-C2-rain_ignition_shift SRC=$PWD/ilamb/MODELS/ED-C2-rain_ignition_shift/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`

Output: `public_benchmark_clean/ilamb/output_with_ED-C2-rain_ignition_shift/scalar_database.csv`.

Public leaderboard rows with Overall:

| Rank | Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---:|---|---:|---:|---:|---:|---:|
| 1 | ED-ModelC-baseline | 0.734518 | 0.509637 | 0.849154 | 0.772477 | 0.675085 |
| 2 | ED-C2-rain_ignition_shift | 0.732049 | 0.519212 | 0.850027 | 0.754600 | 0.675020 |
| 3 | CLASSIC | 0.738463 | 0.506512 | 0.782179 | 0.796576 | 0.666048 |
| 4 | CLM6.0 | 0.758765 | 0.473987 | 0.758324 | 0.838156 | 0.660644 |

Public comparison caveat: JSBACH produced an IndexError in the public script, but the run completed and wrote scalar outputs for models with Overall Score. In the public benchmark root, C2-rain is effectively tied with but slightly below the included ED-ModelC-baseline by 0.000065, while remaining above other public comparators.
