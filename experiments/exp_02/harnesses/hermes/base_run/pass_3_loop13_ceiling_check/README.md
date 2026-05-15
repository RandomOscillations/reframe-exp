# Experiment 02 Hermes Base: Pass 3 Loop 13 Ceiling Check

This folder is the compact, repo-safe artifact package for the Hermes `/goal` continuation run from:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base
```

The heavy local artifact snapshot is stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base/pass_3_artifacts
```

The archive copy is stored at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-14__ed_fire_exp02_hermes_base_pass3_loop13_ceiling_check
```

## Run Summary

Starting point: `ED-next-curing-hotwet-1`, the pass 2 accepted balanced model.

Accepted final balanced model remains:

```text
ED-next-curing-hotwet-1
```

Key result: Loop 13 found additional scalar/public headroom, but not a defensible global-plus-regional replacement.

| Model | Official Overall | Public TRENDY Overall | Decision |
| --- | ---: | ---: | --- |
| ED-next-curing-hotwet-1 | 0.687626 | 0.687405 | Retained best balanced model |
| ED-loop13-combined | 0.690564 | 0.690353 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridatt | 0.690378 | 0.690170 | Rejected: BONA/BOAS collapse |
| ED-loop13-aridboreal-5 | 0.690073 | 0.689864 | Rejected: partial boreal recovery, not balanced |

The loop-13 result is useful ceiling evidence: scalar gains above Hotwet-1 are possible, but the tested mechanisms buy those gains by damaging BONA/BOAS and/or regional balance.

## Contents

- `logs/`: Hermes-maintained research logs and final report.
- `candidate_metadata/`: loop-13 candidate `params.json` metadata plus the retained Hotwet-1 reference.
- `model/`: current model formula/params snapshots.
- `scripts/`: scripts used for search, reproduction, and evaluation.
- `run_logs/`: relevant search logs.
- `tables/`: markdown summary tables for loop 13 and retained comparison context.
- `official_ilamb/`: compact official ILAMB `scalar_database.csv`, `scores.csv`, and `ILAMB01.log` files.
- `public_trendy/`: compact public TRENDY/firepipe outputs for serious loop-13 candidates and Hotwet-1.
- `prompt/`: prompt drafts available for the run.
- `ARTIFACT_MANIFEST.sha256`: sha256 manifest for this compact package.

## Compact Artifact Policy

This repo package excludes NetCDF files, ILAMB pickle files, full input data, and virtual environments. Those are preserved in the heavy local snapshot and archive paths above.
