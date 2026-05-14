# Experiment 01: ED Fire Hermes Run

This experiment tests whether structural reframing improves autoresearch on the ED fire Model C testbed. Dev's regime-aware prompt is the baseline prompt family, and the reframe condition will start from the same original Model C state.

This directory is the permanent research record. Live agent work happens outside this repo in local workspaces:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/
```

The prior pilot run and accidental operator-audit artifacts were archived at:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-13_162156__ed_fire_exp01_formal_prompt_reset_snapshot
```

## Formal Status

- Active phase: structural reframe pass 2 completed and recorded.
- Harness: Hermes Agent.
- Model: `gpt-5.5` through OpenAI Codex provider.
- Start state: original Model C, clean ED source commit `1bac731`.
- Required stop for each formal condition: constrained exploration exhaustion with complete logs/reports, not first improvement.

## Pilot Record

The completed Hermes run from 2026-05-13 is stored as lightweight evidence in:

```text
experiments/exp_01/harnesses/hermes/pilot_autoresearch_run_20260513
```

That run is prompt-calibration evidence because it received mid-run steering. It should not be used as the clean equal-start control condition.

## Recorded Runs

- `harnesses/hermes/base_run`: base-prompt run from original Model C.
- `harnesses/hermes/reframe_pass_1`: structural-reframe fresh run from original Model C, accepted `F3b`.
- `harnesses/hermes/reframe_pass_2_continuation`: structural-reframe continuation from `F3b`, accepted `P2F3`.

## Required Evidence

The formal base run must produce agent-owned evidence for:

- functional-form hypotheses,
- parameter/Optuna/search process,
- regenerated TRENDY-format `burntArea.nc`,
- official global ILAMB,
- official regional ILAMB,
- public TRENDY/firepipe benchmark comparison,
- ablations/diagnostics for serious candidates,
- constraint compliance,
- a final report with accepted/rejected best models and remaining failure modes.

Proxy diagnostics are allowed for triage but not final publication evidence.
