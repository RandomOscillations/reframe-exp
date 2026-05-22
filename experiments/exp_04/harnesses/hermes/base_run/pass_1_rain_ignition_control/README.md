# Exp 04 Base Pass 1: Rain-Conditioned Ignition Control

This is the first non-reframed Hermes control pass for Exp 04, run from a clean isolated original Model C workspace.

## Run Summary

- Harness: Hermes Agent
- Branch: base/control
- Starting point: original Model C
- Prompt: `prompt/control_prompt.md`
- Local workspace snapshot: `_archive/2026-05-22__ed_fire_exp04_base_pass1_rain_ignition_control`
- Final candidate selected by agent: `ED-C2-rain_ignition_shift`
- Operator assessment: clean run, but premature as a full empirical-ceiling search

## Main Outcome

The agent performed two outer loops:

1. Broad full-refit mechanism families: wet/high-GPP suppression, annual precipitation hump, rain-temperature shift, dry-season gate, and base refit.
2. Targeted fixed-core gates: annual wet suppression, wet-GPP suppression, rain-conditioned ignition, and combined wet/rain gates.

The best candidate was `ED-C2-rain_ignition_shift`, a global rain-conditioned ignition threshold with a global rate-power compression. It improved local official global ILAMB and most initially weak regional diagnostics, but it did not beat the clean public ED baseline and reduced global Spatial Distribution.

## Key Scores

| Model | Official Overall | Public Overall | Decision |
|---|---:|---:|---|
| Original Model C | 0.671529 | 0.675085 | Public benchmark leader in this run |
| ED-C2-rain_ignition_shift | 0.675267 | 0.675020 | Best local official candidate; public near-tie but slightly lower |
| ED-C2-combined_wet_rain | 0.673055 | Not run | Rejected by parsimony and lower official score |
| ED-C2-wet_gpp_amp | 0.671533 | Not run | Near-tie, not meaningful |
| ED-C2-annual_wet_amp | 0.668582 | Not run | Rejected |

## Regional Result

`ED-C2-rain_ignition_shift` improved all initially weakest diagnostic regions, including `ceam`, `euro`, `tena`, `mide`, `seas`, `shsa`, and `eqas`. It slightly worsened `shaf` and reduced global Spatial Distribution from `0.772351` to `0.755836`.

## Contents

- `logs/`: final report and maintained research/evaluation logs
- `model/`: baseline Model C formula/params and candidate params/search logs/formulas
- `official_ilamb/`: scalar official ILAMB outputs for baseline, candidates, and ablations
- `public_trendy/`: scalar public TRENDY/firepipe outputs for the serious public comparison
- `scripts/`: run-created or run-used helper scripts
- `prompt/`: control prompt used for the pass
- `ARTIFACT_MANIFEST.sha256`: checksums for the committed artifact bundle

Large input data, virtual environments, and generated NetCDF files are intentionally not committed here.
