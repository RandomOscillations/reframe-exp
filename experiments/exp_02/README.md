# Experiment 02: ED Fire Prompt Update Run

This experiment is a fresh repeat of the ED fire Model C autoresearch setup with a slightly updated prompt. It starts from the same original Model C state used for Experiment 01 so the new prompt can be compared against the prior base and structural-reframe runs.

Live agent work happens outside this repo:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/reframe
```

Both live workspaces were created from ED autoresearch source commit `1bac731`, with shared `data` and `.venv` symlinks to:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source
```

## Workspace Verification

Both live workspaces pass:

```bash
.venv/bin/python scripts/verify.py
```

Verification result for both `base` and `reframe`:

```text
Present: 24
Hash OK: 24
Mismatch: 0
PASS
```

## Current Status

- Live workspaces: created and verified.
- Prompt files: draft copies created; update before launch.
- Run artifacts: Hermes base pass 1 P2F3 continuation copied into `experiments/exp_02/harnesses/hermes/base_run/pass_1_p2f3_continuation`; pass 2 ceiling continuation copied into `experiments/exp_02/harnesses/hermes/base_run/pass_2_ceiling_continuation`.
- Required stop condition: constrained exploration exhaustion with complete logs/reports, not first improvement.

## Run Records

After each run finishes, copy compact artifacts into:

```text
experiments/exp_02/harnesses/hermes/base_run
experiments/exp_02/harnesses/hermes/reframe_run
```

Use the same compact artifact policy as Experiment 01:

- include markdown logs and final reports,
- include candidate/search JSONs,
- include final model formula/params/scripts,
- include compact official global/regional ILAMB CSV/JSON/log outputs,
- include compact public TRENDY/firepipe CSV/JSON/log outputs,
- exclude NetCDFs, ILAMB pickle files, full data directories, and virtual environments.
