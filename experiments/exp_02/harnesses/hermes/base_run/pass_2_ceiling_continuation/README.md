# Experiment 02 Hermes Base: Pass 2 Ceiling Continuation

This folder is the compact, repo-safe artifact package for the Hermes `/goal` continuation run from:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base
```

The heavy local artifact snapshot is stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base/pass_2_artifacts
```

The archive copy is stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-14__ed_fire_exp02_hermes_base_pass2_ceiling_hotwet_continuation
```

## Run Summary

Starting point: P2F3 best-so-far from the previous continuation state.

Accepted final balanced continuation model:

```text
ED-next-curing-hotwet-1
```

Final accepted artifact in the live/heavy snapshot:

```text
runs/candidates/p2f3_curing_hotwet_final/
```

Key official global scores:

| Model | Official Overall | Public TRENDY Overall | Decision |
| --- | ---: | ---: | --- |
| Original Model C | 0.671529 | 0.671274 | Baseline |
| P2F3 | 0.677073 | 0.676846 | Previous best / broad regional alternate |
| ED-next-curing-hotwet-1 | 0.687626 | 0.687405 | Accepted final balanced continuation |
| ED-next-curing-warmwet-nowarmgate | 0.688603 | 0.688384 | Rejected top scalar due BONA/BOAS damage |

The accepted model is not region-by-region dominant over P2F3. It is accepted as the best balanced continuation because it gives a material global/public step while mostly preserving BONA/BOAS and improving AUST, TENA, EURO, NHAF, and SHAF. P2F3 remains the broad weak-region alternate, especially for CEAM, MIDE, SEAS, EQAS, and South America.

## Contents

- `logs/`: Hermes-maintained research logs and final report.
- `candidate_metadata/`: all candidate `params.json` metadata files, flattened by candidate name.
- `model/`: original Model C params/formula plus final Hotwet-1 and previous P2F3 params.
- `scripts/`: Python/shell scripts used in the run.
- `run_logs/`: search log outputs under `runs/logs`.
- `tables/`: markdown summary tables produced by the run.
- `official_ilamb/`: compact official ILAMB `scalar_database.csv`, `scores.csv`, and `ILAMB01.log` files.
- `public_trendy/`: compact public TRENDY/firepipe outputs for accepted Hotwet-1 and rejected Nowarmgate.
- `prompt/`: Experiment 02 prompt drafts available at run time.
- `ARTIFACT_MANIFEST.sha256`: sha256 manifest for this compact package.

## Compact Artifact Policy

This repo package excludes NetCDF files, ILAMB pickle files, full input data, and virtual environments. Those are preserved in the heavy local snapshot and archive paths above.
