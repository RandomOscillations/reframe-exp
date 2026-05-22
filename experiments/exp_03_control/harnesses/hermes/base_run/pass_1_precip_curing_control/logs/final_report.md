# Final Report: Constrained Model C Fire-Formula Improvement Run

## Executive conclusion

I did not find a defensible replacement that beats original Model C under the required acceptance criteria.

Best final model: original Model C (C0), reproduced in this workspace.

Why: every tested mechanistic extension improved weak regional scores but degraded global Spatial Distribution enough to lose global ILAMB and public TRENDY/firepipe rank. The best compromise candidate, H3 seasonal contrast, raised several weak regions but fell from C0 global Overall 0.6715 to 0.6654 locally, and from public 0.6713 to 0.6652, below CLASSIC 0.6660. Therefore the defensible stopping point is to retain original Model C as the global/public best model and record H3 only as a regional-compromise alternative.

## Constraints and scope

Workspace boundary: `/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_03_control/hermes/base`

Read before changes:
- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `README.md`
- `WRITEUP.md`
- `models/C/formula.md`

All candidates used only fixed-contract inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files for scoring only.

No candidate used external data, latitude/longitude terms, named-region routing, per-region formulas, per-cell lookup tables, direct residual correction, or direct cell identity fitting.

## Baseline reproduction

Verification command:
`./.venv/bin/python scripts/verify.py`

Result:
- All pinned input arrays, params, ED GPP, and GFED HDF5 files matched checksums.
- Existing generated artifacts differed in file size before regeneration and were recorded:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13600931, got 13628344.
  - `out_terms/modelC_terms.nc`: expected 112006460, got 116077308.

Regeneration command:
`./.venv/bin/python scripts/reproduce_modelC.py`

Regenerated artifact:
`ilamb/MODELS/ED-ModelC-final/burntArea.nc`

Reproduction diagnostics:
- land cells: 13826 / 64800
- raw rate land mean: 0.09018 yr-1
- max raw rate: 0.9987 yr-1
- ED-transformed land mean: 0.00610759
- GFED land mean: 0.00298745
- ratio: 2.044

Official global ILAMB command:
`ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH bash scripts/run_ilamb.sh`

Official regional ILAMB command:
`ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_modelC_regions`

## Baseline C0 official scores

Global official ILAMB, output `ilamb/output_modelC/scalar_database.csv`:

| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| C0 original Model C | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 |

Regional official ILAMB, output `ilamb/output_modelC_regions/scalar_database.csv`:

| Region | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| bona | 0.8840 | 0.7425 | 0.9251 | 0.6549 | 0.7898 |
| boas | 0.8408 | 0.6192 | 0.7966 | 0.7679 | 0.7287 |
| ceas | 0.7834 | 0.5603 | 0.7222 | 0.7265 | 0.6705 |
| aust | 0.7456 | 0.6520 | 0.5795 | 0.7219 | 0.6702 |
| shaf | 0.7597 | 0.5023 | 0.9021 | 0.5671 | 0.6467 |
| nhaf | 0.7693 | 0.4795 | 0.9010 | 0.5998 | 0.6459 |
| nhsa | 0.5014 | 0.4932 | 0.9144 | 0.6270 | 0.6058 |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5074 |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5072 |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4872 |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3828 |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3815 |
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3762 |
| euro | 0.3934 | 0.2618 | 0.8082 | 0.0805 | 0.3611 |

Failure triage:
- C0 is strong globally and in boreal/Africa/Australia/Central Asia.
- Weak regions are Europe, Central America, Temperate North America, Middle East, Southeast Asia, Southern Hemisphere South America, and Equatorial Asia.
- Weak regions often retain high Seasonal scores; the issue is mostly magnitude/RMSE and spatial placement.
- Proxy diagnostics indicated overprediction in many weak regions, suggesting missing wet-fuel/curing/humid suppression or low-fuel/human/land-use constraints.

## Mechanisms tried

### H1: annual humid suppression / upper precipitation limb

Mechanistic hypothesis:
Model C has an annual precipitation floor but no upper wet limb. Persistently humid climates should suppress fire because fuels do not cure despite high productivity.

Formula factor:
`humid_supp(P_ann) = 1 / (1 + (P_ann / P_humid)^P_humid_q)`

Search:
- Optuna 500 full-field proxy trials.
- Tuned selected base params plus `P_humid` and `P_humid_q`.
- Best proxy output: `artifacts/candidate_annual_humid_supp_500.json`.
- Params: `models/H1_annual_humid_supp/params.json`.
- Artifact: `ilamb/MODELS/ED-H1-annual-humid-supp/burntArea.nc`.

Official global result:
- Bias 0.7243
- RMSE 0.5173
- Seasonal 0.8496
- Spatial 0.5837
- Overall 0.6384

Regional result:
- Large weak-region gains, e.g. EQAS 0.6801 vs C0 0.5074, SHSA 0.6404 vs 0.5072, EURO 0.5173 vs 0.3611.
- But global Spatial collapsed by -0.1887.

Decision: rejected. The mechanism diagnoses a real regional issue but over-suppresses/reshapes spatial fire distribution globally.

### H1m: mild annual humid suppression ablation

Purpose:
Ablation to test whether H1 failure came from retuning/overfitting rather than the added mechanism.

Formula:
Same as H1, but original Model C base params fixed. Deterministic grid selected `P_humid=1500`, `P_humid_q=0.5`.

Params: `models/H1m_mild_humid/params.json`
Artifact: `ilamb/MODELS/ED-H1m-mild-humid/burntArea.nc`
Output: `ilamb/output_H1m_regions/scalar_database.csv`

Official global result:
- Bias 0.7263
- RMSE 0.5068
- Seasonal 0.8460
- Spatial 0.6828
- Overall 0.6538

Decision: rejected. It confirms the tradeoff is structural: mild humid suppression still improves weak regions but loses -0.0177 Overall and -0.0896 Spatial globally.

### H2: wet-month logistic suppression

Mechanistic hypothesis:
The original hyperbolic monthly precipitation dampener may not suppress active burning sharply enough in wet months.

Formula factor:
`wet_supp(P_month) = 1 / (1 + exp(wet_k * (P_month - wet_c)))`

Search:
- Deterministic grid over `wet_k` and `wet_c` on fixed Model C base.
- Best proxy selected `wet_k=0.1`, `wet_c=20`.

Params: `models/H2_wetmonth/params.json`
Artifact: `ilamb/MODELS/ED-H2-wetmonth/burntArea.nc`
Output: `ilamb/output_H2_regions/scalar_database.csv`

Official global result:
- Bias 0.7290
- RMSE 0.5168
- Seasonal 0.8521
- Spatial 0.6524
- Overall 0.6534

Decision: rejected. It improves some weak humid/temperate regions and slightly improves global Seasonal, but loses too much Spatial Distribution.

### H3: seasonal contrast / curing gate

Mechanistic hypothesis:
Absolute monthly precipitation is not portable across climates; fire responds to current-month wetness relative to local annual precipitation climatology. This captures curing/dry-season contrast without region labels.

Formula factor:
`contrast_supp = 1 / (1 + (P_month / (P_ann/12 + contrast_eps))^contrast_q)`

Search:
- Deterministic grid over `contrast_eps` and `contrast_q` on fixed Model C base.
- Best proxy selected `contrast_eps=0.5`, `contrast_q=0.25`.

Params: `models/H3_seasonal_contrast/params.json`
Artifact: `ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc`
Output: `ilamb/output_H3_regions/scalar_database.csv`

Official global result:
- Bias 0.7304
- RMSE 0.5110
- Seasonal 0.8480
- Spatial 0.7267
- Overall 0.6654

Regional behavior:
- EURO: 0.4198 vs C0 0.3611
- CEAM: 0.4104 vs C0 0.3762
- TENA: 0.4289 vs C0 0.3815
- MIDE: 0.4115 vs C0 0.3828
- SEAS: 0.5149 vs C0 0.4872
- SHSA: 0.5551 vs C0 0.5072
- EQAS: 0.5525 vs C0 0.5074

Decision: rejected as final, but it is the best regional-compromise alternative. It loses only -0.0061 global Overall but still loses -0.0457 Spatial and does not beat public benchmark rank.

## Candidate comparison summary

Official global ILAMB:

| Run | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| C0 original Model C | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 |
| H1 retuned humid suppression | 0.7243 | 0.5173 | 0.8496 | 0.5837 | 0.6384 |
| H1m mild humid suppression | 0.7263 | 0.5068 | 0.8460 | 0.6828 | 0.6538 |
| H2 wet-month logistic | 0.7290 | 0.5168 | 0.8521 | 0.6524 | 0.6534 |
| H3 seasonal contrast | 0.7304 | 0.5110 | 0.8480 | 0.7267 | 0.6654 |

Weak-region Overall comparison:

| Region | C0 | H1 | H1m | H2 | H3 |
|---|---:|---:|---:|---:|---:|
| euro | 0.3611 | 0.5173 | 0.4096 | 0.4932 | 0.4198 |
| ceam | 0.3762 | 0.5039 | 0.4269 | 0.4327 | 0.4104 |
| tena | 0.3815 | 0.4727 | 0.4258 | 0.4865 | 0.4289 |
| mide | 0.3828 | 0.4191 | 0.4101 | 0.4089 | 0.4115 |
| seas | 0.4872 | 0.5749 | 0.5377 | 0.5272 | 0.5149 |
| shsa | 0.5072 | 0.6404 | 0.5755 | 0.5844 | 0.5551 |
| eqas | 0.5074 | 0.6801 | 0.5694 | 0.6268 | 0.5525 |
| global | 0.6715 | 0.6384 | 0.6538 | 0.6534 | 0.6654 |

Full table:
`artifacts/official_candidate_regional_scores.csv`

## Public TRENDY/firepipe comparison

Clean benchmark root:
`public_benchmark_clean`

C0 command:
`MODEL_NAME=ED-ModelC-final-repro SRC=$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`

C0 output:
`public_benchmark_clean/ilamb/output_with_ED-ModelC-final-repro/scalar_database.csv`

C0 public result:
- Overall 0.6713
- Bias 0.7281
- RMSE 0.5058
- Seasonal 0.8457
- Spatial 0.7711
- Tied copied `ED-ModelC-baseline`, rank #1 above CLASSIC 0.6660 and CLM6.0 0.6606.

H3 command:
`MODEL_NAME=ED-H3-seasonal-contrast SRC=$PWD/ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`

H3 output:
`public_benchmark_clean/ilamb/output_with_ED-H3-seasonal-contrast/scalar_database.csv`

H3 public result:
- Overall 0.6652
- Bias 0.7304
- RMSE 0.5110
- Seasonal 0.8480
- Spatial 0.7255
- Below Model C 0.6713 and CLASSIC 0.6660; above CLM6.0 0.6606.

Public benchmark caveat:
The public script reported a JSBACH IndexError, but scalar rows for candidate and other comparators were produced. The JSBACH error was isolated and did not affect candidate-vs-available-comparator rows used here.

## Why remaining failures appear unresolved under current constraints

The regional experiments consistently say the same thing:
- Added wetness/curing suppression improves low-fire humid/temperate regions.
- But those same smooth global precipitation gates degrade global spatial distribution, especially where Model C already performs well.

This suggests the unresolved weak-region errors are not simply a missing one-dimensional precipitation transform. Likely missing mechanisms under the fixed contract include:
- human ignition and suppression,
- cropland/pasture fragmentation,
- fire-management differences in Europe/Temperate North America/Middle East,
- peat/deforestation fire processes in Equatorial/Southeast Asia,
- fuel continuity and vegetation structure,
- lightning/human ignition geography,
- land-use fire types.

Those are not available as model inputs. Under the allowed five inputs, precipitation-only or curing-only global gates can reduce magnitude in weak regions but cannot place fire correctly without damaging savanna/boreal/global spatial skill.

## Final recommendation

Use original Model C as the final model for this constrained run.

Do not replace it with H1/H1m/H2/H3 unless the objective explicitly changes from global/public benchmark rank to weak-region regional compromise. If such a compromise is desired, H3 is the cleanest alternative because it has the smallest global loss while improving all listed weak regions.

## Reproducibility artifact paths

Logs:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `final_report.md`

Scripts created:
- `scripts/fire_explore.py`
- `scripts/summarize_ilamb_scores.py`
- `scripts/summarize_any_ilamb.py`
- `scripts/grid_humid_ablation.py`
- `scripts/grid_other_families.py`
- `scripts/compare_candidates.py`

Candidate params:
- `models/H1_annual_humid_supp/params.json`
- `models/H1m_mild_humid/params.json`
- `models/H2_wetmonth/params.json`
- `models/H3_seasonal_contrast/params.json`

Candidate NetCDFs:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- `ilamb/MODELS/ED-H1-annual-humid-supp/burntArea.nc`
- `ilamb/MODELS/ED-H1m-mild-humid/burntArea.nc`
- `ilamb/MODELS/ED-H2-wetmonth/burntArea.nc`
- `ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc`

Official ILAMB outputs:
- `ilamb/output_modelC/scalar_database.csv`
- `ilamb/output_modelC_regions/scalar_database.csv`
- `ilamb/output_H1_regions/scalar_database.csv`
- `ilamb/output_H1m_regions/scalar_database.csv`
- `ilamb/output_H2_regions/scalar_database.csv`
- `ilamb/output_H3_regions/scalar_database.csv`

Public benchmark outputs:
- `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-repro/scalar_database.csv`
- `public_benchmark_clean/ilamb/output_with_ED-H3-seasonal-contrast/scalar_database.csv`

Derived comparison artifact:
- `artifacts/official_candidate_regional_scores.csv`
- `artifacts/candidate_annual_humid_supp_500.json`
