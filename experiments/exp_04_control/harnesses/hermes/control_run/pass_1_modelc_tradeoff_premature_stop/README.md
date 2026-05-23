# Pass 1: Model C Tradeoff, Premature Stop

## Status

Clean run, but shallow. The agent followed isolation constraints and ran official evaluations, but stopped after one broad outer-loop search rather than continuing into a deeper multi-loop control process.

## Summary

- Starting point: original Model C.
- Search: five mechanism families, 500 Optuna trials each.
- Official global ILAMB: completed for all candidates.
- Official regional ILAMB: completed for all candidates.
- Public TRENDY/firepipe: completed for reproduced Model C.
- Final accepted model: original Model C.

## Main Result

The run found regional-improvement tradeoffs but no replacement that beat Model C globally:

- Model C official global Overall: `0.671529`
- Closest modified candidate: `ED-ModelC-temp_window`, official global Overall `0.659200`
- Best regional-mean diagnostic: `ED-ModelC-precip_shape`, but official global Overall fell to `0.646299`
- Best worst-region repair: `ED-ModelC-fuel_moisture_balance`, but official global Overall fell to `0.657146`

## Interpretation

This is useful as evidence of a control-agent failure mode: the agent correctly identified a global-vs-regional tradeoff frontier, but prematurely concluded the empirical ceiling after one broad search wave and proxy ablations.

## Archive

Full run artifacts, excluding raw data and virtual environments, were preserved at:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-22__ed_fire_exp04_control_pass1_modelc_tradeoff_premature_stop`

