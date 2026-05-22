# Exp 03 Control - Base Run Pass 2

This folder preserves the second control continuation pass for the Hermes ED fire autoresearch experiment.

The run continued from the pass 1 control workspace and tested second-order mechanism families beyond the initial precipitation/curing variants:

- dry-gated annual humid suppression
- dry-gated wet-month suppression
- wet productive forest / closed-canopy suppression
- hyperarid low-fuel suppression
- cool uncured ignition interaction
- productivity-shape retuning

Final outcome: original Model C remained the retained model. The strongest continuation candidate, H4 dry-gated wet-month suppression, improved all listed weak regions but collapsed official global Spatial Distribution and Overall, so it was rejected.

Key scores:

- C0 original Model C official global Overall: 0.671529
- H3 seasonal contrast official global Overall: 0.665444
- H4 dry-gated wet-month official global Overall: 0.636910
- C0 clean public TRENDY/firepipe Overall: 0.6713
- H3 clean public TRENDY/firepipe Overall: 0.6652

Contents:

- `logs/`: final report and maintained research/evaluation logs
- `artifacts/`: regional score tables, diagnostics, Optuna logs, and continuation search outputs
- `model/`: baseline Model C formula/params and candidate params
- `scripts/`: run-created or run-modified helper scripts
- `ilamb_outputs/`: scalar ILAMB outputs for baseline and candidates
- `public_benchmark/`: scalar public benchmark outputs for serious public comparisons
- `prompt/`: continuation prompt used for this pass
- `ARTIFACT_MANIFEST.sha256`: checksums for this archived artifact bundle

Large input data, virtual environments, and generated NetCDF outputs are intentionally not committed here. A local recovery snapshot without data or `.venv` was also created at:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-22__ed_fire_exp03_control_base_pass2_second_order_continuation`
