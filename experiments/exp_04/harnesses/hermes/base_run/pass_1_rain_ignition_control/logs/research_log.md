# Research Log

## Setup and baseline verification

Read required workspace documents before modifying model artifacts: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, README.md, WRITEUP.md, and models/C/formula.md.

Understanding: the run must remain inside this workspace, start from original Model C, preserve one global mechanistic formula using only allowed inputs, avoid region/cell identity routing or external data, and maintain official global/regional ILAMB plus public TRENDY/firepipe evidence for serious candidates.

Baseline checks:
- `.venv/bin/python scripts/verify.py` found all pinned inputs present. Two generated artifacts differed in size from CHECKSUMS.txt before regeneration: `ilamb/MODELS/ED-ModelC-final/burntArea.nc` expected 13600931 bytes got 13466737; `out_terms/modelC_terms.nc` expected 112006460 got 116077308. Input arrays and params matched checksums. This is recorded and regeneration was run before scoring.
- `.venv/bin/python scripts/reproduce_modelC.py` regenerated baseline Model C. Diagnostics: land cells 13826/64800; raw rate land mean 0.09018 yr^-1; max 0.9987; ED-transformed land mean 0.00610759 vs GFED 0.00298745 ratio 2.044.
- `bash scripts/run_ilamb.sh` needed PATH and ILAMB_ROOT set (`PATH=$PWD/.venv/bin:$PATH`, `ILAMB_ROOT=$PWD/ilamb`) because `ilamb-run` was not on default PATH and ILAMB requires ILAMB_ROOT.

Official baseline global ILAMB, from `ilamb/output_modelC/scalar_database.csv`:
- Bias Score: 0.7281
- RMSE Score: 0.5058
- Seasonal Cycle Score: 0.8457
- Spatial Distribution Score: 0.7724
- Overall Score: 0.6715

Official regional ILAMB component workflow:
`ilamb-run --config ilamb/burntArea_official.cfg --model_root ilamb/MODELS --models ED-ModelC-final --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir ilamb/output_modelC_regions --skip_plots`

First triage: Model C is globally strong but weak in Central America, Europe, temperate North America, Middle East, SE Asia, southern South America, and equatorial Asia. Weak regions often show low Spatial Distribution and/or low Bias/RMSE despite strong seasonal phase in many tropical regions. This suggests missing mechanisms may include overprediction in wet/high-productivity systems, insufficient aridity/wetness suppression, precipitation-temperature ignition coupling, or dry-season relative precipitation gating.

## Loop 1: broad full-refit mechanism families

Mechanism families searched with `scripts/research_model_variants.py`, 500 Optuna trials each (plus baseline enqueue), using only allowed inputs and one global formula:
- C1 wet_gpp_supp: wet/high-GPP live-fuel or closed-canopy suppression. Search selected no-op (amp=0), so broad Optuna found no support beyond baseline.
- C1 annual_p_hump: annual precipitation high-end suppression plus low-end floor refit. Search found a regional-improving candidate but with lower internal global spatial.
- C1 rain_temp_shift: monthly rain raises ignition threshold. Search found regional-improving candidate but lowered seasonal/spatial globally.
- C1 dry_season_gate: relative dry-season anomaly gate. Search selected no-op (amp=0), no support beyond baseline.
- C1 base_refit: broad 12-param refit. Search selected baseline, suggesting the supplied Model C is near a local optimum for this proxy.

Official ILAMB for serious C1 candidates:
- ED-C1-rain_temp_shift global Overall 0.6568 vs C0 0.6715. Bias 0.7303 and RMSE 0.5145 improved, but Seasonal 0.8243 and Spatial 0.7004 declined. Regional diagnostic aggregates improved many worst regions (e.g. ceam 0.4435 vs 0.3613, euro 0.5427 vs 0.3665, tena 0.5361 vs 0.3907), but mide remained weak (0.4050) and global loss is too large.
- ED-C1-annual_p_hump global Overall 0.6426. Bias 0.7303 and RMSE 0.5089 roughly improved, Seasonal 0.8361 slightly declined, Spatial collapsed to 0.6287. Regional worst regions improved strongly (ceam 0.4416, euro 0.4945, tena 0.4964), but global spatial tradeoff is unacceptable as a replacement.

Loop 1 conclusion: wetness/rain mechanisms are physically plausible and improve many regional failures, especially Europe/temperate/Central America, but broad full-refit versions move toward regional bias correction at the expense of global spatial structure and top-ranked global performance. Treat them as diagnostic/regional alternatives, not accepted replacements. Next loop tests smaller targeted gates around fixed Model C to see whether regional gains can be kept without destroying global spatial distribution.

## Loop 2: targeted fixed-core mechanism gates and ablations

Implemented `scripts/search_targeted_mechanisms.py` to keep the original Model C core fixed while tuning small global gates. This avoids the broad C1 tendency to refit the entire model into regional bias correction.

Targeted 1000-trial families:
- annual_wet_amp: high annual precipitation suppression + rate_power.
- wet_gpp_amp: wet/high-GPP live-fuel/closed-canopy suppression + rate_power.
- rain_ignition_shift: monthly precipitation raises the ignition temperature threshold + rate_power.
- combined_wet_rain: all three targeted wet/rain mechanisms together + rate_power.

Official global ILAMB ranking from C2:
1. ED-C2-rain_ignition_shift: Overall 0.675267; Bias 0.732049, RMSE 0.519212, Seasonal 0.850027, Spatial 0.755836.
2. ED-C2-combined_wet_rain: Overall 0.673055; lower than rain-only and more complex.
3. ED-C2-wet_gpp_amp: Overall 0.671533, effectively tied with C0 but not meaningful as global gain.
4. C0 original Model C: Overall 0.671529.
5. ED-C2-annual_wet_amp: Overall 0.668582.

C2-rain regional effects: improves all initially weakest regions (ceam, euro, tena, mide, seas, shsa, eqas, nhsa) while slightly worsening shaf. The largest diagnostic regional gain is Europe (+0.167), followed by temperate North America (+0.0745), Central America (+0.0668), and equatorial Asia (+0.0574). Remaining failures persist mostly in ceam/mide/euro spatial structure.

Ablations for C2-rain:
- rate_power only: Overall 0.661221.
- rain-conditioned ignition without rate_power: Overall 0.660225.
Therefore the gain is not explained by a scalar intensity compression alone or by the rain ignition gate alone; the combined mechanistic replacement and compression is needed.

Public TRENDY/firepipe comparison using `scripts/run_public_trendy_firepipe_clean.sh`: C2-rain ranked #2, essentially tied with the included ED-ModelC-baseline (0.675020 vs 0.675085) and above CLASSIC/CLM6.0. This prevents claiming a public leaderboard replacement, but it supports C2-rain as a serious mechanistic candidate with local official global and regional improvements.

Stopping rationale: after broad full refits, targeted single-mechanism gates, combined gates, no-op checks, and ablations, the only defensible new mechanism with global and regional support is rain-conditioned ignition. More complex wet/annual/GPP mechanisms either reduce global score, collapse spatial performance, or do not beat the simpler rain-only candidate. Remaining failures likely need inputs excluded by the fixed contract (land use, cropland management, human ignitions/suppression, vegetation/fuel structure), so further parameter fitting under the current inputs risks overfitting tradeoffs rather than mechanism discovery.
