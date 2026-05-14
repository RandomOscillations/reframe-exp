# ED Fire Autoresearch Program

You are running an ED fire model-improvement task.

## Objective

Start from original Model C and push the model-improvement process to a defensible stopping point.

The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

## Core Question

Can a unified mechanistic model improve:

1. public/global TRENDY burned-area benchmark ranking,
2. official global ILAMB score components,
3. official regional ILAMB scores,
4. regional/fire-regime failure modes,
5. interpretability and physical plausibility,

without using external model inputs, region routing, coordinate hacks, lookup tables, or arbitrary residual factors?

## Hard Constraints

Allowed model inputs are listed in `WORKSPACE_MANIFEST.md`.

Do not use:
- new external data as model input,
- per-cell lookup tables,
- latitude/longitude hacks,
- named-region routing,
- per-region formulas,
- arbitrary correction coefficients,
- pure hyperparameter fitting without a physical mechanism,
- any trick that improves global score while knowingly worsening regional realism.

The model should remain one unified global functional form. Smooth climate-dependent branches are allowed only if they have a physical reason and are not disguised regional routing.

## Required Autoresearch Loop

Repeat this loop until further changes are no longer productive under the current constraints:

1. State a physical hypothesis.
2. Propose a functional-form change or diagnostic.
3. Define the parameter/search space if fitting is needed.
4. Run Optuna/search or a documented deterministic parameter scan.
5. Regenerate TRENDY-format `burntArea.nc`.
6. Run official global ILAMB.
7. Run official regional ILAMB.
8. For serious candidates, run the public TRENDY/firepipe benchmark comparison.
9. Compare against baseline and current best on global, regional, and mechanistic criteria.
10. Accept, revise, ablate, or reject the candidate.
11. Log the loop before moving on.

Do not stop because one candidate improves global Overall. Keep a best-so-far model and continue until further constrained model exploration becomes unproductive.

## Evaluation Commands

Baseline verification:

```bash
.venv/bin/python scripts/verify.py
```

Regenerate model output:

```bash
.venv/bin/python scripts/reproduce_modelC.py
```

Official global ILAMB for current workspace model:

```bash
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh
```

Official regional ILAMB for current workspace model:

```bash
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
```

Public TRENDY/firepipe benchmark comparison for serious candidates:

```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```

Known benchmark caveat: the public TRENDY benchmark repo has a known JSBACH edge-case failure in ILAMB, documented by the benchmark README. That does not invalidate completed candidate/model comparisons, but it must be logged if it appears.

## Acceptance Criteria

A candidate can become best-so-far only if:

- it uses only allowed inputs,
- it is mechanistically interpretable,
- it is evaluated with official global ILAMB,
- it is evaluated with official regional ILAMB,
- it does not hide regional damage behind global gains,
- it has ablation or diagnostic support when feasible,
- it is compared against the baseline and current best.

A candidate is not acceptable solely because a proxy score improves.

## Logging Requirements

Maintain these files throughout the run:

- `research_log.md`: chronological loop-by-loop record.
- `candidate_registry.md`: every candidate, status, files changed, parameters, and verdict.
- `eval_log.md`: exact commands, output directories, score summaries, and failures.
- `regional_analysis.md`: official regional results and interpretation.
- `constraint_checks.md`: explicit compliance checks for each serious candidate.
- `stuck_state.md`: only when further constrained model exploration is exhausted.

For each loop, log:

- hypothesis,
- functional form,
- parameter/search strategy,
- files changed,
- commands run,
- global ILAMB results,
- regional ILAMB results,
- public TRENDY/firepipe result if run,
- ablation/diagnostic result,
- decision and reason.

## Stuck State

Write `stuck_state.md` only when further constrained model exploration is genuinely exhausted.

The stuck state must include:

- best-so-far model,
- baseline vs best global ILAMB table,
- baseline vs best official regional ILAMB table,
- public TRENDY/firepipe ranking table,
- mechanisms tried,
- failed and marginal directions,
- remaining regional/fire-regime failures,
- why more smooth gates or parameter tuning are unlikely to help,
- why the remaining failures appear unresolved under the current constraints.
