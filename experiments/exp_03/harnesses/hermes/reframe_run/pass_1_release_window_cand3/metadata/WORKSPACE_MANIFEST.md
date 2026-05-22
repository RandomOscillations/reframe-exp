# Workspace Manifest

## Provenance

This workspace was prepared from the local ED autoresearch source tree and pinned input data.

## Expected Contents

Core files and directories:

- `README.md`
- `WRITEUP.md`
- `CHECKSUMS.txt`
- `requirements.txt`
- `models/C/params.json`
- `models/C/formula.md`
- `scripts/reproduce_modelC.py`
- `scripts/dump_modelC_terms.py`
- `scripts/run_ilamb.sh`
- `scripts/verify.py`
- `data/crujra/*.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- `data/gfed/GFED4.1s_*.hdf5`
- `ilamb/DATA`
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- `out_terms/modelC_terms.nc`


Additional clean benchmark support:

- `public_benchmark_clean`
- `scripts/run_public_trendy_firepipe_clean.sh`

`public_benchmark_clean` contains only official benchmark comparator models, `EDv3`, and `ED-ModelC-baseline` copied from this workspace's original Model C artifact.

## Isolation Rules

Use this workspace as the experiment boundary.

Do not use prior experiment folders, archive folders, or unrelated local benchmark outputs as evidence.

Use `public_benchmark_clean` for public TRENDY/firepipe comparisons.

## Starting Model

The starting model is original Model C in:

- `models/C/params.json`
- `scripts/reproduce_modelC.py`
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`

Only `ED-ModelC-final` is expected under `ilamb/MODELS` at setup time.
