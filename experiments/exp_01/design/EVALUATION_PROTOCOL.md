# Evaluation Protocol

## Purpose

The ED fire task is not just a score maximization task. The formal experiment asks whether an autoresearch agent can improve a mechanistic burned-area model while preserving physical interpretability and regional realism.

## Required Loop

Every serious autoresearch loop must follow this shape:

1. State the physical hypothesis.
2. Specify the functional-form change.
3. Define parameter/search space.
4. Run Optuna or a documented deterministic search.
5. Regenerate TRENDY-format `burntArea.nc`.
6. Run official global ILAMB.
7. Run official regional ILAMB.
8. Run public TRENDY/firepipe benchmark for serious best-so-far candidates.
9. Compare against baseline and current best.
10. Decide keep, revise, ablate, or reject.

## Evidence Tiers

Proxy diagnostics:
- useful for triage,
- not publication-grade final evidence,
- cannot justify a final claim alone.

Official global ILAMB:
- required for every serious candidate,
- records global score components.

Official regional ILAMB:
- required for every serious candidate,
- records GFED/ILAMB regional behavior.

Public TRENDY/firepipe benchmark:
- required before claiming best-so-far or stuck state,
- compares against the public model suite using the TRENDY benchmark repo.

## Objective

A candidate should improve the global score without hiding regional degradation. The agent must report:

- global Overall,
- Bias Score,
- RMSE Score,
- Seasonal Cycle Score,
- Spatial Distribution Score,
- official regional Overall/Spatial scores,
- public benchmark rank.

## Non-Gaming Rules

Disallowed:

- adding new external model inputs,
- latitude/longitude correction hacks,
- per-cell lookup tables,
- named-region routing,
- per-region formulas,
- arbitrary residual correction factors,
- accepting a global score gain that damages regional/fire-regime behavior.

Allowed:

- smooth climate-dependent mechanisms if physically justified,
- parameter search over mechanistic parameters,
- web/literature research for explanation only,
- custom diagnostics for triage only.

