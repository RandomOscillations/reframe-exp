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

## Benchmark Support

This source-only workspace includes the local official ILAMB data/model directories under `ilamb/`.

This workspace also includes `public_benchmark_clean`, a local-only TRENDY/firepipe benchmark root containing official comparator models and this workspace's baseline Model C artifact.

Use `scripts/run_public_trendy_firepipe_clean.sh` for public TRENDY/firepipe comparisons. The script refuses benchmark roots outside this workspace.

No prior experiment benchmark outputs are included at setup time. Do not use benchmark outputs from prior experiment folders, archive folders, or unrelated local project folders.

## Isolation Rules

Use this workspace as the experiment boundary.

Do not use prior experiment folders, archive folders, or unrelated local benchmark outputs as evidence.

## Starting Model

The starting model is original Model C in:

- `models/C/params.json`
- `scripts/reproduce_modelC.py`
- `ilamb/MODELS/ED-ModelC-final/burntArea.nc`

Only `ED-ModelC-final` is expected under `ilamb/MODELS` at setup time.
