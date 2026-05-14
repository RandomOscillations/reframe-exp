# Hermes Pilot Autoresearch Run 2026-05-13

This directory preserves the lightweight research record from the Hermes ED fire run completed on 2026-05-13.

Status: pilot / prompt-calibration evidence, not a clean paper comparison run.

Why it is marked pilot:

- The run began from the original Model C workspace, but it received mid-run steering after an early premature final report.
- The steering clarified the intended outer autoresearch loop and forced continued mechanism search.
- The resulting artifacts are useful for prompt design, harness validation, and paper-method notes, but should not be treated as the equal-start control condition.

Heavy runnable state is intentionally not stored here. NetCDF outputs, ILAMB HTML dashboards, pickles, venvs, and raw data remain in the local workspace:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/base
```

## Contents

- `logs/`: agent-owned markdown logs and final report.
- `candidates/`: candidate search JSONs.
- `scripts/`: candidate search/generation scripts created or used by the run.
- `metadata/`: prompt/program/context files and baseline metadata.
- `official_ilamb/`: compact official global/regional ILAMB evidence (`scores.csv`, `scalar_database.csv` only).
- `public_trendy/`: compact public TRENDY/firepipe score tables.

## Run Outcome

The final report accepted `PRECIP-CONC-WET-v1` as the best defensible model, while rejecting `PRECIP-CONC-WET-CURING-LAG-v1` despite its higher scalar score because it damaged MIDE and added complexity.

Key scores from the run:

- Baseline official global Overall: `0.671529`.
- Accepted `PRECIP-CONC-WET-v1` official global Overall: `0.672472`.
- Highest-scalar combo official global Overall: `0.672681`, rejected.
- Baseline public Overall: `0.671274`.
- Accepted `PRECIP-CONC-WET-v1` public Overall: `0.672227`.
- Highest-scalar combo public Overall: `0.672433`, rejected.

Use this run to refine the formal prompt and logging protocol. Fresh comparison runs should start from original Model C in a clean local workspace.
