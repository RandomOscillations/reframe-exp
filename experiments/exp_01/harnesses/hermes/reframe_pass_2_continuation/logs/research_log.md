# Research Log Pass 2

## Setup and understanding

Read required pass-2 context before changes: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, final_report.md, research_log.md, candidate_registry.md, eval_log.md, regional_analysis.md, constraint_checks.md, models/C/formula.md, models/C/params.json, scripts/research_fire_candidates.py.

Understanding:
- Continue from completed pass 1 and current F3b model state; do not restart from original Model C or repeat pass-1 searches.
- Current best entering pass 2 was F3b: original Model C core multiplied by global wet/canopy-moisture and arid fuel-discontinuity suppressors.
- F3b official global ILAMB: Overall 0.676543, Bias 0.738225, RMSE 0.511898, Seasonal 0.844302, Spatial 0.776393.
- F3b public TRENDY/firepipe rank: #1, Overall 0.676313.
- Remaining failures: very low regional spatial scores in EURO/TENA/MIDE/CEAM, low AUST seasonal score, and tradeoffs in BONA/NHSA/BOAS.

No blocking questions were present, so pass-2 failure analysis and research loops proceeded immediately.

## Pass-2 failure framing

F3b corrected broad amplitude overprediction via slow-varying annual wet/arid limiters. Remaining errors are more about within-regime timing/spatial allocation:
- AUST seasonal cycle remains weak, suggesting missing dry-season curing/monsoon timing rather than mean wetness.
- EURO/TENA/MIDE/CEAM spatial remains poor even after amplitude correction, suggesting missing subgrid human/land-use/fuel-continuity factors unavailable directly, but perhaps partially inferable from seasonal climate/productivity mismatch.
- BONA/NHSA tradeoffs imply the wet suppressor is a blunt annual proxy; a seasonal wetness/curing term could sharpen suppression where rain is concurrent with burn risk while preserving regions where high annual precipitation still permits a burn season.

## Loop 1 — Seasonal curing/synchronization gate

Hypothesis: F3b uses static annual wet/arid limiters; remaining AUST seasonal and weak-region RMSE failures may reflect missing timing alignment among dry state, drying tendency, and rain-free current month. Structural analogy: traffic-light phase control / combustion-engine ignition timing; the same average fuel and moisture can burn differently depending on when permissive phases overlap.

Unified mechanism: multiply F3b by a global curing gate built from smooth functions of Dbar, month-to-month Dbar increase, and current-month precipitation anomaly relative to annual precipitation. No region labels or external inputs.

Search: `N_TRIALS=600 SEED=711 .venv/bin/python scripts/research_fire_pass2.py optimize --family p2_curing_gate --candidate P2F1_curing_gate`. Best internal simple score 0.679269 vs F3b internal 0.679069.

Official global ILAMB for P2F1: Overall 0.676618, Bias 0.738469, RMSE 0.512636, Seasonal 0.845672, Spatial 0.773679. It improved Bias/RMSE/Seasonal and global Overall slightly, but lost Spatial vs F3b.

Official regional ILAMB: most weak regions improved slightly (TENA, CEAM, SHSA, EURO, MIDE, SEAS, EQAS), BONA spatial/overall worsened further, AUST seasonal remained essentially unchanged.

Decision: keep as serious comparison candidate but not final. The mechanism is physically interpretable but accepted gate amplitude was small and spatial/AUST issues remained.

## Loop 2 — Seasonal wet/canopy inhibition

Hypothesis: F3b's annual wet suppressor is too static; wet tropical and temperate systems may need inhibition only when rainfall/moisture is concurrent or antecedent to the burn window. Structural analogy: clinical triage timing or warehouse scheduling; total resource load is not enough, the load must coincide with the process bottleneck.

Unified mechanism: replace the static annual wet suppressor with a wet-climate gate multiplied by current and one-month-antecedent precipitation anomaly. The arid F3b limiter stayed fixed.

Search: `N_TRIALS=700 SEED=733 ... --family p2_seasonal_wet --candidate P2F2_seasonal_wet`. Best internal simple score 0.679612.

Official global ILAMB: Overall 0.676714, Bias 0.737437, RMSE 0.510878, Seasonal 0.846213, Spatial 0.778162.

Decision: reject as final despite a higher global score than F3b. It improved global Spatial/Seasonal but worsened several weak wet-region regional scores relative to F3b/P2F1, especially CEAM, SHSA, SEAS, and EQAS. It appears to loosen the wet suppression too much in regions where persistent wet-canopy inhibition is exactly the needed mechanism.

## Loop 3 — Two-threshold arid fuel-continuity limiter

Hypothesis: F3b's single arid threshold is too blunt. Dryland fuel networks do not fail at one cliff; they first lose redundancy and then become desert-discontinuous. Structural analogy: communications networks or epidemic/percolation systems lose robustness before complete fragmentation.

Unified mechanism: keep the F3b wet suppressor, replace the single arid sigmoid with two global smooth deficit-ratio thresholds:
- a weak early semi-arid continuity threshold;
- a strong high-deficit desert cutoff.

Search: `N_TRIALS=600 SEED=751 ... --family p2_arid_softplus --candidate P2F3_arid_two_threshold`. Best internal simple score 0.680161.

Official global ILAMB: Overall 0.677073, Bias 0.738666, RMSE 0.512972, Seasonal 0.848079, Spatial 0.772673.

Official regional ILAMB: improves many weak dry/subtropical regions vs F3b: TENA +0.008019, EURO +0.008616, MIDE +0.010559, NHSA +0.003808, SHSA +0.002564, SEAS +0.002288. EQAS remains much better than baseline but slightly lower than F3b. BONA and AUST worsen.

Ablations:
- P2F3 no low threshold (arid_amp1=0): official global Overall 0.676981. This is only 0.000092 below full P2F3, with better global Spatial but lower weak-region dryland gains.
- P2F3 no high threshold (arid_amp2=0): official global Overall 0.676040. The high-deficit desert threshold is essential.

Decision: accept P2F3 as best pass-2 candidate. The low threshold is small but physically interpretable and gives the highest official global score plus improved TENA/EURO/MIDE. The high threshold is strongly supported by ablation.

## Loop 4 — Hybrid seasonal wet + two-threshold arid

Hypothesis: combine Loop 2's seasonal wetness and Loop 3's refined arid fragmentation to get both global spatial preservation and dryland gains.

Search: `N_TRIALS=800 SEED=773 ... --family p2_seasonal_wet_arid2 --candidate P2F4_seasonal_wet_arid2`. Best internal simple score 0.678267, below F3b and far below P2F3.

Decision: reject before official ILAMB. The larger 15-parameter hybrid did not produce a meaningful candidate and appears overflexible/unstable under the internal screen.

## Public benchmark and final verification

P2F3 was run through public TRENDY/firepipe with unique model name `ED-ModelC-pass2-P2F3` and fresh output directory `ilamb/output_pass2_P2F3_fresh` in the benchmark repo. JSBACH again showed the known IndexError caveat, but the table completed. P2F3 ranked #1 with public Overall 0.676846.

Final current reproduction check after updating `models/C/params.json` and `scripts/reproduce_modelC.py`:
- `.venv/bin/python scripts/reproduce_modelC.py`
- `OUT="$PWD/ilamb/output_pass2_final_current_global" ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh`
- Result: official global Overall 0.677073, matching P2F3.
