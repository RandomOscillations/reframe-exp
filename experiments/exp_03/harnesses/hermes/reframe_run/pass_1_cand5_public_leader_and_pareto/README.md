# Hermes Reframe Pass 1: Cand5 Public Leader And Pareto Frontier

## Purpose

This artifact package records the completed Experiment 03 Hermes structural-reframe run. The run started from original Model C and continued through multiple autoresearch cycles until it found a new clean-public leader and a separate balanced regional/global Pareto candidate.

## Main Results

| Use case | Model | Official diagnostic global | Clean public TRENDY/firepipe Overall | Regional note |
|---|---:|---:|---:|---|
| Public/global leader | `ED-Cand5Abl-no_edge_mix` | `0.688648` | `0.679633` | Improves `11/14` regions vs Model C, `8/14` vs Cand3, `11/14` vs Cand4Abl. |
| Balanced Pareto compromise | `ED-Cand5Sweep-edgefrac_0p50` | `0.688490` | `0.679346` | Improves `12/14` regions vs Model C and `11/14` vs Cand3. |
| Broad weak-region repair | `ED-Cand5-mosaic_edge_release` | `0.687870` | `0.678548` | Improves `13/14` regions vs Model C and `10/14` vs Cand3. |

## Interpretation

The decisive counterfactual was the deterministic edge-mix sweep:

- `edge_mix = 0.0` / `ED-Cand5Abl-no_edge_mix`: highest public/global score.
- `edge_mix = 0.5` / `ED-Cand5Sweep-edgefrac_0p50`: best balanced global and regional compromise.
- `edge_mix = 1.0` / full `ED-Cand5-mosaic_edge_release`: strongest weak-region repair, with more global/public and BONA/African-belt cost.

This supports a Pareto-frontier conclusion: allowed climate/productivity fields can infer broad fire-regime structure, but the remaining BONA/strong-belt versus humid/monsoon repair tradeoff appears unresolved without forbidden or unavailable variables such as land use, fragmentation, management, ignition/suppression, peat/soil, or vegetation-structure inputs.

## Directory Guide

- `logs/`: agent-maintained research logs, final report, evaluation log, regional analysis, candidate registry, and constraint checks.
- `model/`: formula summaries for the public leader, balanced Pareto model, broad regional repair model, plus baseline Model C formula/params.
- `candidates/`: JSON search outputs for cycle-5 mechanism families, ablations, and edge sweep.
- `eval_tables/official/`: official global/regional ILAMB scalar tables for candidate families, ablations, and sweeps.
- `eval_tables/public/`: clean public TRENDY/firepipe scalar tables for key candidates.
- `scripts/`: scripts used for the cycle-5 search, ablation, sweep, ILAMB, and clean public benchmark invocation.
- `prompt/`: prompt used to start the run.
- `artifacts/`: checksums for large `burntArea.nc` artifacts stored outside git in the full workspace archive.

## Full Archive

Large generated files are not committed here. The full local workspace snapshot is:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-21__ed_fire_exp03_hermes_reframe_cand5_public_leader_and_pareto_final/full_workspace`

## Integrity

`ARTIFACT_MANIFEST.sha256` records SHA-256 checksums for the committed artifact package. `artifacts/burntArea_artifacts.sha256` records checksums for the large NetCDF candidate artifacts in the live/full archive workspace.
