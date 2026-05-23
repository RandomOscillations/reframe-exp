# Evaluation Log

## Baseline checks

### `scripts/verify.py`
Command:
` .venv/bin/python scripts/verify.py `

Result: exit code 1 because generated NetCDF artifacts differed from pinned checksums before regeneration. All fixed input files and `models/C/params.json` were OK.

Mismatches recorded before proceeding:
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`: size expected 13600931, got 13466737.
- `out_terms/modelC_terms.nc`: size expected 112006460, got 116077308.

### Reproduce Model C
Command:
` .venv/bin/python scripts/reproduce_modelC.py `

Result: success. Regenerated `ilamb/MODELS/ED-ModelC-final/burntArea.nc`.
Diagnostics:
- land cells: 13826 / 64800
- raw rate land-mean: 0.09018 yr^-1
- max raw rate: 0.9987 yr^-1
- ED-transformed land-mean: 0.00610759
- GFED land-mean: 0.00298745
- ratio: 2.044

### Official global ILAMB baseline
Initial command `bash scripts/run_ilamb.sh` failed because `ilamb-run` was not on PATH. Successful command:
`PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh`

Output path: `ilamb/output_modelC/scalar_database.csv`

Exact global scores for `ED-ModelC-final`:
- Bias Score: 0.728089000000
- RMSE Score: 0.505759000000
- Seasonal Cycle Score: 0.845690000000
- Spatial Distribution Score: 0.772351000000
- Overall Score: 0.671529000000

### Official regional ILAMB baseline
Command:
`PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run --config "$PWD/ilamb/burntArea_official.cfg" --model_root "$PWD/ilamb/MODELS" --regions bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir "$PWD/ilamb/output_modelC_regions" --skip_plots`

Output path: `ilamb/output_modelC_regions/scalar_database.csv`

ILAMB emitted component scores for each GFED region, but did not emit a regional `Overall Score` scalar in this regional run. For triage I use the same tier-2 formula `(2*Bias + 2*RMSE + Seasonal + Spatial)/6` as a derived diagnostic; official component scores remain the primary regional evidence.

## Candidate search and official evaluation
Search command:
`N_TRIALS_PER_FAMILY=500 .venv/bin/python scripts/run_modelC_mechanism_experiments.py`

Search output:
- `experiments/modelC_mechanism_search/summary.json`
- Candidate NetCDFs under `ilamb/MODELS/ED-ModelC-*/burntArea.nc`

Official global candidate command:
`PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run --config "$PWD/ilamb/burntArea_official.cfg" --model_root "$PWD/ilamb/MODELS" --regions global --build_dir "$PWD/ilamb/output_candidates_global_full" --clean`

Official regional candidate command:
`PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" ilamb-run --config "$PWD/ilamb/burntArea_official.cfg" --model_root "$PWD/ilamb/MODELS" --regions bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust --build_dir "$PWD/ilamb/output_candidates_regions" --skip_plots --clean`

Official global results:
| Model | Bias | RMSE | Seasonal | Spatial | Overall |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 |
| ED-ModelC-temp_window | 0.725506 | 0.511461 | 0.841213 | 0.706360 | 0.659200 |
| ED-ModelC-fuel_moisture_balance | 0.731075 | 0.511184 | 0.839058 | 0.693227 | 0.657146 |
| ED-ModelC-humid_suppression | 0.718573 | 0.505759 | 0.829925 | 0.686248 | 0.649253 |
| ED-ModelC-base_refit | 0.722189 | 0.507389 | 0.834902 | 0.668848 | 0.648144 |
| ED-ModelC-precip_shape | 0.715627 | 0.509039 | 0.841352 | 0.656438 | 0.646299 |

Derived regional summary from official component scores:
| Model | Mean derived regional Overall | Min | Max |
|---|---:|---:|---:|
| ED-ModelC-precip_shape | 0.615108 | 0.357003 | 0.782779 |
| ED-ModelC-humid_suppression | 0.601833 | 0.347296 | 0.728462 |
| ED-ModelC-fuel_moisture_balance | 0.594038 | 0.421151 | 0.701360 |
| ED-ModelC-base_refit | 0.590194 | 0.403365 | 0.726535 |
| ED-ModelC-temp_window | 0.589537 | 0.364386 | 0.775945 |
| ED-ModelC-final | 0.560591 | 0.361275 | 0.805502 |

## Public TRENDY/firepipe comparison
Command:
`MODEL_NAME=ED-ModelC-final-reproduced SRC="$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe_clean.sh`

Output path: `public_benchmark_clean/ilamb/output_with_ED-ModelC-final-reproduced/scalar_database.csv`

Result: clean benchmark root ran, with a JSBACH pair IndexError reported by ILAMB but post-processing completed and scalar outputs were written for the comparator table. Reproduced Model C remains ahead of public comparator models except the pre-existing `ED-ModelC-baseline` artifact in the clean root.

Top public scores:
| Model | Overall |
|---|---:|
| ED-ModelC-baseline | 0.675085 |
| ED-ModelC-final-reproduced | 0.671274 |
| CLASSIC | 0.666048 |
| CLM6.0 | 0.660644 |
| CLM-FATES | 0.656831 |
| ELM-FATES | 0.656788 |
