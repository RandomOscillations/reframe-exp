# Evaluation Log

## Baseline reproduction: C0 original Model C

### Verification
Command: `.venv/bin/python scripts/verify.py`

Result: nonzero due only to generated artifact size differences before regeneration.
- OK: all CRUJRA arrays, Model C params, EDv3_S3_gpp.nc, and GFED4.1s 2001-2016 input HDF5 files.
- Size differences recorded before proceeding:
  - `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: expected 13600931, got 13628344.
  - `out_terms/modelC_terms.nc`: expected 112006460, got 116077308.

### Reproduction
Command: `.venv/bin/python scripts/reproduce_modelC.py`

Output artifact: `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
Diagnostics:
- land cells: 13826 / 64800
- raw rate land mean: 0.09018 yr-1
- max raw rate: 0.9987 yr-1
- ED-transformed land mean: 0.00610759
- GFED land mean: 0.00298745
- ratio: 2.044

### Official global ILAMB
Command: `ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH bash scripts/run_ilamb.sh`
Output: `ilamb/output_modelC/scalar_database.csv`

| Region | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| global | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 |

### Official regional ILAMB
Command: `ILAMB_ROOT=$PWD/ilamb PATH=$PWD/.venv/bin:$PATH ilamb-run --config $PWD/ilamb/burntArea_official.cfg --model_root $PWD/ilamb/MODELS --regions global bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir $PWD/ilamb/output_modelC_regions`
Output: `ilamb/output_modelC_regions/scalar_database.csv`

See `regional_analysis.md`.

## Candidate official evaluations

| Run | Artifact | Output dir | Bias | RMSE | Seasonal | Spatial | Overall | Decision |
|---|---|---|---:|---:|---:|---:|---:|---|
| C0 | `ilamb/MODELS/ED-ModelC-final/burntArea.nc` | `ilamb/output_modelC_regions` | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 | Best global/public |
| H1 retuned annual humid suppression | `ilamb/MODELS/ED-H1-annual-humid-supp/burntArea.nc` | `ilamb/output_H1_regions` | 0.7243 | 0.5173 | 0.8496 | 0.5837 | 0.6384 | Reject |
| H1m mild humid suppression | `ilamb/MODELS/ED-H1m-mild-humid/burntArea.nc` | `ilamb/output_H1m_regions` | 0.7263 | 0.5068 | 0.8460 | 0.6828 | 0.6538 | Reject |
| H2 wet-month logistic | `ilamb/MODELS/ED-H2-wetmonth/burntArea.nc` | `ilamb/output_H2_regions` | 0.7290 | 0.5168 | 0.8521 | 0.6524 | 0.6534 | Reject |
| H3 seasonal contrast | `ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc` | `ilamb/output_H3_regions` | 0.7304 | 0.5110 | 0.8480 | 0.7267 | 0.6654 | Reject as final; regional-compromise alternative |

Full regional comparison written to `artifacts/official_candidate_regional_scores.csv`.

## Public TRENDY/firepipe clean benchmark

Baseline C0 command:
`MODEL_NAME=ED-ModelC-final-repro SRC=$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`
Output: `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-repro/scalar_database.csv`

C0 public result: Overall 0.6713, tied with copied `ED-ModelC-baseline`, rank #1 above CLASSIC 0.6660 and CLM6.0 0.6606.

H3 command:
`MODEL_NAME=ED-H3-seasonal-contrast SRC=$PWD/ilamb/MODELS/ED-H3-seasonal-contrast/burntArea.nc bash scripts/run_public_trendy_firepipe_clean.sh`
Output: `public_benchmark_clean/ilamb/output_with_ED-H3-seasonal-contrast/scalar_database.csv`

H3 public result: Overall 0.6652, below Model C 0.6713 and CLASSIC 0.6660, above CLM6.0 0.6606. Rejected as final.

Note: public runs report a JSBACH IndexError for that comparator, but other comparator and candidate scalar rows are produced and usable; this is isolated to JSBACH and present during public benchmark runs.
