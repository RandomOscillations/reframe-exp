# Experiment 02 Hermes Base: Pass 1 P2F3 Continuation

This folder is the compact, repo-safe artifact package for the first counted Hermes base continuation pass from:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base/pass_1_artifacts
```

The heavy local artifact snapshot remains stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base/pass_1_artifacts
```

The archive copy is stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-14__ed_fire_exp02_hermes_base_pass1_p2f3_continuation
```

## Run Summary

Starting point: original Model C plus the Experiment 02 base prompt and continuation steering.

Accepted final model:

```text
ED-p2f3-seed2 / p2f3_seed_current
```

Final accepted artifact in the heavy snapshot:

```text
runs/candidates/p2f3_seed_current/
```

Key official global scores:

| Model | Official Overall | Public TRENDY Overall | Decision |
| --- | ---: | ---: | --- |
| Original Model C | 0.671529 | 0.671274 | Baseline |
| ED-wet-temp-grid | 0.674491 | 0.674241 | Rejected: BONA/BOAS spatial collapse |
| ED-combo-warm-ann | 0.672911 | not final | Rejected: balanced but too small |
| ED-p2f3-seed2 | 0.677073 | 0.676846 | Accepted final for pass 1 |
| ED-p2f3-nolow2 | 0.676981 | not final | Serious ablation / parsimonious alternate |

P2F3 was accepted because it produced the first material global step while improving most weak regions and avoiding the severe BONA/BOAS collapse from earlier wet-temperature candidates. Remaining failures were BONA spatial tradeoff and AUST seasonality, which motivated the pass 2 ceiling continuation.

## Contents

- `logs/`: Hermes-maintained research logs and final report.
- `candidate_metadata/`: all candidate `params.json` metadata files, flattened by candidate name.
- `model/`: original/current Model C files plus final P2F3 params.
- `scripts/`: Python/shell scripts used in the run.
- `run_logs/`: search log outputs under `runs/logs`.
- `tables/`: markdown summary tables produced by the run.
- `official_ilamb/`: compact official ILAMB `scalar_database.csv`, `scores.csv`, and `ILAMB01.log` files.
- `public_trendy/`: compact public TRENDY/firepipe outputs for P2F3 and wet-temp comparison.
- `prompt/`: Experiment 02 prompt drafts available at run time.
- `ARTIFACT_MANIFEST.sha256`: sha256 manifest for this compact package.

## Compact Artifact Policy

This repo package excludes NetCDF files, ILAMB pickle files, full input data, and virtual environments. Those are preserved in the heavy local snapshot and archive paths above.
