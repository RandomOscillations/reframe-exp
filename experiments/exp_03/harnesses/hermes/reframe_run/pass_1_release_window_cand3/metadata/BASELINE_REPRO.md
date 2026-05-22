# Baseline Reproduction

## Baseline

The starting point is original Model C from `models/C/params.json` and `scripts/reproduce_modelC.py`.

Model C is described in `README.md`, `WRITEUP.md`, and `models/C/formula.md`. Use those files as the authoritative baseline description for this workspace.

## Required First Checks

Before changing the model:

1. Run `.venv/bin/python scripts/verify.py`.
2. Run `.venv/bin/python scripts/reproduce_modelC.py`.
3. Run `bash scripts/run_ilamb.sh`.
4. Record the exact global ILAMB scores in `eval_log.md`.
5. Create or run a reproducible regional evaluation workflow and record regional failures in `regional_analysis.md`.

If regenerated baseline hashes differ from `CHECKSUMS.txt`, record the difference before proceeding.

## Scoring Rule

Use locally reproduced ILAMB values as the run baseline and log exact output paths.

Do not use scores or artifacts from prior experiment folders as baseline evidence.
