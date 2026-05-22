# Hermes Reframe Pass 2: Pareto Guarded Corridor / Cand4

## Purpose

This artifact package records the second Experiment 03 Hermes structural-reframe pass from the intact Cand4/Pareto snapshot.

The pass continued from `ED-Cand3-release_window_wetcap` and tested third-order mechanisms plus Pareto refinements: guarded release, senescence release, dual-corridor balance, warm/dry supply-chain alignment, Pareto guarded corridor, and Pareto senescence corridor.

## Main Results

| Use case | Model | Official diagnostic global | Clean public TRENDY/firepipe Overall | Regional note |
|---|---:|---:|---:|---|
| Global/public leader at pass 2 | `ED-Cand4Abl-no_hotboost` | `0.688962` | `0.679480` | Improved 9/14 named regions vs Model C and 5/14 vs Cand3; not a clean broad regional replacement. |
| Broad regional candidate retained | `ED-Cand3-release_window_wetcap` | `0.687439` | `0.678312` | Better broad regional behavior than Cand4Abl at this point. |

## Log Provenance

The pass-2 logs are intact and copied directly from:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-19__ed_fire_exp03_hermes_reframe_cand4_global_public_leader_completed_snapshot/full_workspace`

These logs are not reconstructed.

## Directory Guide

- `logs/`: exact agent-maintained logs at the end of pass 2.
- `model/`: baseline Model C files and Cand4 no-hotboost formula/result files.
- `candidates/`: JSON/formula artifacts for third-order and Pareto mechanism searches; large NetCDF outputs are excluded.
- `eval_tables/official/`: official ILAMB scalar outputs for Cand4, Pareto, and Pareto ablations.
- `eval_tables/public/`: clean public TRENDY/firepipe scalar outputs for Cand4 and Cand3 comparisons.
- `scripts/`: scripts used for third-order search, Pareto search, and ablation.
- `prompt/`: original reframe prompt retained for run context.

## Large Artifacts

Large generated NetCDF files are not committed here. They remain available in the local full snapshot referenced above.
