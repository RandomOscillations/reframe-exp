# Final Report — Constrained Model C Fire-Model Improvement Run

## Executive decision

Recommended final model: keep original Model C (`ED-ModelC-final`, candidate C0) as the defensible final model for this workspace.

A serious near-baseline candidate, C4 (`ED-ModelC-curing_ratio-g700`), improved official global Spatial Distribution (0.782165 vs 0.772351) and Bias (0.729482 vs 0.728089), but lost RMSE, Seasonal Cycle, official Overall, and public benchmark rank relative to C0. The requested target was a meaningful, defensible step-function improvement in global fit and regional behavior, not a third-decimal scalar tradeoff. No explored mechanistic family met that bar.

The empirical stopping point is therefore: Model C remains the best supported model under the fixed input contract; the remaining regional failures appear to require information not contained in the allowed five driver fields, or a more expressive mechanism that this constrained search did not find without damaging global behavior.

## Workspace and constraints

Workspace:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_04-reframe/hermes/reframe`

Required files read before modification:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `README.md`
- `WRITEUP.md`
- `models/C/formula.md`

Allowed model inputs were respected:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files already in this workspace

No candidate formula used latitude, longitude, named-region routing, per-cell lookup tables, external data, per-region formulas, or residual correction coefficients. Region masks were used only for evaluation/search diagnostics.

## Baseline reproduction

Initial `scripts/verify.py` result:
- Present: 24, Missing: 0.
- Hash OK: 22, Mismatch: 2.
- Mismatches were generated artifacts only:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13,600,931 bytes, got 13,466,737 bytes.
  - `out_terms/modelC_terms.nc`: expected 112,006,460 bytes, got 116,077,308 bytes.
- All fixed inputs and `models/C/params.json` matched pinned hashes.

Baseline regeneration command:

```bash
.venv/bin/python scripts/reproduce_modelC.py
```

Official global ILAMB command:

```bash
PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh
```

Baseline C0 official global ILAMB:

| Metric | Score |
|---|---:|
| Bias Score | 0.728089 |
| RMSE Score | 0.505759 |
| Seasonal Cycle Score | 0.845690 |
| Spatial Distribution Score | 0.772351 |
| Overall Score | 0.671529 |

Output paths:
- NetCDF: `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- Global ILAMB: `ilamb/output_modelC`
- Regional ILAMB: `ilamb/output_modelC_regions`

## Baseline regional triage

Official regional ILAMB command used built-in GFED/TRENDY regions:

```bash
PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run \
  --config ilamb/burntArea_official.cfg \
  --model_root ilamb/MODELS \
  --models ED-ModelC-final \
  --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust \
  --build_dir ilamb/output_modelC_regions \
  --skip_plots
```

Weakest baseline regions by official component mean were:
- Europe: strong seasonal (0.808) but very weak spatial (0.080) and RMSE (0.262).
- Central America: strong seasonal (0.847) but weak bias/RMSE/spatial.
- Middle East: moderate seasonal (0.766) but very weak spatial (0.091).
- Temperate North America: weak bias/RMSE/spatial and lower seasonal.
- Equatorial Asia, Southeast Asia, SH South America: seasonal mostly good, spatial/magnitude weaker.

Interpretation: Model C already captures seasonal timing well in many regions. The main failure is spatial/magnitude allocation in low-fire, humid, temperate, fragmented, or agricultural-mosaic regimes. This suggests missing spread-continuity / fuel-structure / human-fragmentation / landcover information, but those fields are not available under the fixed input contract.

## Mechanism search implementation

New search script:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_04-reframe/hermes/reframe/scripts/experiment_fire_search.py`

The script:
- loads only the fixed allowed inputs,
- implements global candidate formula families,
- uses Optuna for parameter search,
- writes candidate NetCDFs under `ilamb/MODELS/<candidate>/burntArea.nc`,
- writes candidate params/diagnostics under `experiments/`,
- uses region masks only for evaluation objectives, not model inputs.

Optuna searches run:
- C1 wet firebreak: 500 trials.
- C2 asymmetric GPP: 500 trials.
- C3 curing-ratio regional objective: 500 trials.
- C4 curing-ratio global objective: 700 trials.

Total Loop 1 search effort: 2,200 Optuna trials across distinct mechanistic families, with no single run exceeding the requested 500–2000 range.

## Mechanisms tried and structural analogies

### C1 — Wet firebreak / fuel-continuity fuse

Formula family: Model C multiplied by annual high-wetness suppression:
`wet = 1 / (1 + (P_ann / wet_P50)^wet_q)^wet_exp`

Mechanistic idea: annual wetness/productive closure can act like a firebreak. Structural analogy: a series circuit can have all upstream switches closed, but a fuse trips and stops current. Similarly, climate can permit ignition timing while landscape/fuel continuity prevents large burned area.

Result: regional weak areas improved, but the suppressor was too broad and damaged global spatial structure.

Official global C1:
- Bias 0.713542
- RMSE 0.515713
- Seasonal 0.830597
- Spatial 0.516938
- Overall 0.618500

Decision: rejected.

### C2 — Asymmetric GPP dose-response

Formula family: replace Model C’s GPP hump with separate low-fuel onset and high-productivity closure.

Mechanistic idea: fire spread peaks at intermediate productivity; too little GPP means insufficient fuel, too much GPP can imply humid closed-canopy or wet productive systems. Structural analogy: pharmacological dose-response: low dose has no effect, mid dose is effective, high dose becomes inhibitory/toxic.

Result: RMSE improved and seasonal remained high, but spatial collapsed relative to C0.

Official global C2:
- Bias 0.722221
- RMSE 0.516424
- Seasonal 0.843135
- Spatial 0.610321
- Overall 0.641705

Decision: rejected/demoted.

### C3 — Dbar-buffered monthly curing, regional objective

Formula family: monthly rain dampening is reduced by accumulated dry deficit:
`effective_rain = P_month / (1 + Dbar / dry_buffer)^dry_buffer_q`

Mechanistic idea: the same monthly rainfall should not extinguish/spread-limit equally in a deeply cured landscape and a wet landscape. Structural analogy: queue/bottleneck dynamics: the state of accumulated backlog changes the effect of a new inflow.

Result: strong regional improvements in weak areas, but by suppressing or distorting high-fire systems too much.

Official global C3:
- Bias 0.699994
- RMSE 0.510097
- Seasonal 0.827503
- Spatial 0.301372
- Overall 0.569813

Decision: rejected as an unacceptable regional/global tradeoff.

### C4 — Dbar-buffered monthly curing, global objective

Same formula family as C3, but optimized to protect global score.

Official global C4:
- Bias 0.729482
- RMSE 0.499233
- Seasonal 0.838594
- Spatial 0.782165
- Overall 0.669741

Compared with C0:
- Bias: +0.001393
- RMSE: -0.006526
- Seasonal: -0.007096
- Spatial: +0.009814
- Overall: -0.001788

C4’s fitted dry-buffer exponent was `dry_buffer_q = 0.0559457`, close to neutral. This is an ablation-like diagnostic: once global fit is protected, the optimizer nearly turns off the extra curing mechanism. The candidate is scientifically useful because it confirms that a slight spatial improvement is possible, but not enough to overcome seasonal/RMSE loss or regional unresolved failures.

Decision: demoted, not accepted.

## Official candidate global ILAMB table

Output: `ilamb/output_candidates_loop1_global_full/scalar_database.csv`

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| ED-ModelC-curing_ratio-g700 | 0.729482 | 0.499233 | 0.838594 | 0.782165 | 0.669741 |
| ED-ModelC-curing_ratio-r500 | 0.699994 | 0.510097 | 0.827503 | 0.301372 | 0.569813 |
| ED-ModelC-gpp_asym-r500 | 0.722221 | 0.516424 | 0.843135 | 0.610321 | 0.641705 |
| ED-ModelC-wet_firebreak-r500 | 0.713542 | 0.515713 | 0.830597 | 0.516938 | 0.618500 |

## Official regional candidate findings

Output:
- `ilamb/output_candidates_loop1/scalar_database.csv`
- extracted diagnostic table: `experiments/loop1_official_regional_components.csv`

Key pattern:
- C1-C3 improve many weak regions, especially CEAM, Europe, Middle East, TENA, EQAS, SEAS, and SHSA.
- But those improvements come from broad suppression that damages globally important high-fire or spatial-structure regions.
- C4 preserves global structure and improves Australia and SH Africa slightly, but it no longer improves the main weak-region set meaningfully.

This is the central scientific result of the run: the allowed inputs contain enough signal to identify “places that need suppression,” but not enough to suppress only the right systems while preserving boreal/savanna fire behavior.

## Clean public TRENDY/firepipe comparison

Public script:
`scripts/run_public_trendy_firepipe_clean.sh`

C0 regenerated baseline output:
`public_benchmark_clean/ilamb/output_with_ED-ModelC-final-c0`

C4 serious candidate output:
`public_benchmark_clean/ilamb/output_with_ED-ModelC-curing_ratio-g700`

Top public rows from the C4 run:

| Rank | Model | Overall |
|---:|---|---:|
| 1 | ED-ModelC-baseline | 0.675085 |
| 2 | ED-ModelC-final-c0 | 0.671274 |
| 3 | ED-ModelC-curing_ratio-g700 | 0.669487 |
| 4 | CLASSIC | 0.666048 |
| 5 | CLM6.0 | 0.660644 |
| 6 | CLM-FATES | 0.656831 |
| 7 | ELM-FATES | 0.656788 |
| 8 | JULES-ES | 0.590519 |

C4 remains above public comparator models but below the clean-workspace Model C artifacts. Therefore it is not a replacement.

Note: public benchmark logs include the known JSBACH `IndexError` described by the benchmark README. The scorecard still completed for the relevant models.

## Best models by use case

### Best overall supported model

C0 / `ED-ModelC-final`.

Reasons:
- Highest official global Overall among candidates generated in this run.
- Best public rank among regenerated candidate artifacts.
- Strongest seasonal cycle.
- Does not introduce additional weakly supported complexity.

### Best spatial-leaning diagnostic candidate

C4 / `ED-ModelC-curing_ratio-g700`.

Reasons:
- Official global Spatial improves from 0.772351 to 0.782165.
- Bias improves slightly.
- Useful as a diagnostic of precipitation/dryness curing interactions.

Why not accepted:
- Overall falls from 0.671529 to 0.669741.
- Seasonal and RMSE decline.
- Public benchmark falls behind C0.
- Extra mechanism almost neutralizes itself (`dry_buffer_q` near zero).

### Best weak-region diagnostic candidate

C3 / `ED-ModelC-curing_ratio-r500`.

Reasons:
- Largest weak-region component-mean improvements.

Why not accepted:
- Official global Spatial collapses to 0.301372.
- Overall collapses to 0.569813.
- It is a tradeoff model, not a unified improvement.

## Ablation and complexity pruning

Evidence used to prune complexity:

1. Regional-objective suppressors (C1-C3) improved weak regions only by damaging global spatial structure. This prunes broad annual wetness suppression, GPP-only closure, and aggressive dbar-buffered curing as acceptable final mechanisms.

2. Global-objective C4 drove `dry_buffer_q` to 0.0559457, close to neutral. This indicates the added curing mechanism has little robust global leverage when not allowed to sacrifice core Model C behavior.

3. C4’s small spatial gain did not survive the full multi-metric acceptance standard because it reduced official Overall and public rank.

4. Original Model C’s lower complexity is preferable: 12 parameters, already interpretable, and better official/public support.

## Remaining failures and why they appear unresolved

Unresolved regions:
- Europe
- Central America
- Middle East
- Temperate North America
- Equatorial/Southeast Asia
- SH South America

Likely missing drivers under the fixed contract:
- cropland and agricultural fire practices,
- human ignition/suppression and fragmentation,
- landcover and canopy/fuel structure,
- lightning or ignition source differences,
- explicit fuel load/biomass/continuity beyond monthly GPP,
- peat/tropical deforestation fire distinctions.

Why current inputs are insufficient: annual precipitation, monthly precipitation, dbar, GPP, and temperature can infer broad aridity/productivity regimes, but they cannot uniquely separate low-fire humid/fragmented/agricultural regions from productive fire-prone savannas and boreal systems. The failed candidates show this identifiability problem empirically: the same suppressors that help weak regions also remove needed high-fire spatial contrast elsewhere.

## Final artifacts

Logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `decision_trace.md`
- `final_report.md`

Scripts:
- `scripts/experiment_fire_search.py`

Baseline artifacts:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- `ilamb/output_modelC`
- `ilamb/output_modelC_regions`

Candidate artifacts:
- `ilamb/MODELS/ED-ModelC-wet_firebreak-r500/burntArea.nc`
- `ilamb/MODELS/ED-ModelC-gpp_asym-r500/burntArea.nc`
- `ilamb/MODELS/ED-ModelC-curing_ratio-r500/burntArea.nc`
- `ilamb/MODELS/ED-ModelC-curing_ratio-g700/burntArea.nc`

Search outputs:
- `experiments/wet_firebreak/ED-ModelC-wet_firebreak-r500.json`
- `experiments/gpp_asym/ED-ModelC-gpp_asym-r500.json`
- `experiments/curing_ratio/ED-ModelC-curing_ratio-r500.json`
- `experiments/curing_ratio/ED-ModelC-curing_ratio-g700.json`
- `experiments/loop1_official_global.csv`
- `experiments/loop1_official_regional_components.csv`
- `experiments/public_curing_g700_ranks.csv`

Official candidate ILAMB:
- `ilamb/output_candidates_loop1_global_full`
- `ilamb/output_candidates_loop1`

Public benchmark:
- `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-c0`
- `public_benchmark_clean/ilamb/output_with_ED-ModelC-curing_ratio-g700`

## Final conclusion

The constrained exploration reached a defensible stopping point. The search found physically interpretable mechanisms that can repair some regional failures, but only by sacrificing global spatial structure, seasonal timing, or public rank. The one global-safe candidate C4 produced only a small spatial gain and a lower official/public Overall, with its new mechanism nearly neutralized by optimization.

Therefore, no candidate supersedes original Model C. The final recommended model remains C0, with documented caveats: low-fire humid/temperate/fragmented regions remain the primary failure mode, and resolving them likely requires additional physically meaningful inputs outside the current fixed contract rather than another simple global gate over the existing five fields.
