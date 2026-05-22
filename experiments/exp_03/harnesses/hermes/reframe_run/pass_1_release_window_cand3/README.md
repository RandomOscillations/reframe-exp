# Hermes Reframe Pass 1: Release Window / Cand3

## Purpose

This artifact package records the first Experiment 03 Hermes structural-reframe pass as recoverable from the earliest surviving exp03 reframe snapshot.

The pass started from original Model C and discovered the `ED-Cand3-release_window_wetcap` family. The core mechanism was a fuel-release window: fire is boosted only under current dryness, intermediate annual precipitation, intermediate GPP/fuel state, and a soft wet/low-deficit cap.

## Main Result

| Use case | Model | Official diagnostic global | Clean public TRENDY/firepipe Overall | Regional note |
|---|---:|---:|---:|---|
| Best pass-1 candidate | `ED-Cand3-release_window_wetcap` | `0.687439` | `0.678312` | Improved 12/14 named non-global regions versus original Model C, with BONA and NHSA caveats. |

## Log Provenance

No standalone Cand3-only filesystem snapshot was found. The earliest surviving exp03 reframe snapshot is the Cand4/Pareto snapshot:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-19__ed_fire_exp03_hermes_reframe_cand4_global_public_leader_completed_snapshot/full_workspace`

Therefore this folder includes:

- `logs/recovered_source_logs/`: exact cumulative logs from that earliest surviving snapshot.
- `logs/pass1_extract/`: extracted pass-1-relevant portions ending before the Cand4/Pareto continuation cycle.

This preserves the available evidence without pretending a raw Cand3-only log state survived.

## Directory Guide

- `logs/`: recovered cumulative logs and pass-1 extracts.
- `model/`: baseline Model C files and Cand3 formula/result files.
- `candidates/`: JSON/formula artifacts for early, second-order, and release-window searches; large NetCDF outputs are excluded.
- `eval_tables/official/`: official ILAMB scalar outputs for baseline, candidate, Cand2, Cand3, and related pass-1 comparisons.
- `eval_tables/public/`: clean public TRENDY/firepipe scalar outputs for Cand3 and earlier serious candidates.
- `scripts/`: scripts used for pass-1 searches and evaluations.
- `prompt/`: reframe prompt used to start the run.

## Large Artifacts

Large generated NetCDF files are not committed here. They remain available in the local full snapshot referenced above.
