# ED Fire Model-Improvement Program

Read `AGENTS.md`, this file, `WORKSPACE_MANIFEST.md`, and `BASELINE_REPRO.md` before doing anything else.

Do not stop until `final_report.md` is written.

## Objective

Start from original Model C. Push the model-improvement process to a defensible stopping point.

The current model performs well offline and ranks strongly on the benchmark. The goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve:

- official global ILAMB behavior,
- official regional ILAMB behavior,
- public TRENDY/firepipe benchmark standing,
- regional/fire-regime realism,
- interpretability under the fixed input contract.

## Formula Requirement

You may alter the functional form and hyperparameters.

The final model must be one global, interpretable formula. It may include smooth ceilings, floors, saturations, humps, thresholds, piecewise functions, interactions, or gates if every term has a physical explanation and uses only allowed inputs.

## Long-Horizon Work Budget

This is intended to be a serious multi-hour run. Do not stop after the first improvement or first rejection.

Unless blocked, work through multiple substantial directions before finalizing. A defensible run should normally include:

- baseline verification,
- official baseline global ILAMB,
- official baseline regional ILAMB,
- public baseline TRENDY/firepipe benchmark if needed for ranking context,
- broad diagnostics of regional failure modes,
- several candidate mechanism families,
- at least one meaningful Optuna search or equivalent deterministic search per promising family,
- 500-2000 Optuna trials at most for substantial searches where runtime allows,
- official global and regional ILAMB for serious candidates,
- public TRENDY/firepipe for serious best-so-far candidates,
- ablations that prune complexity,
- final restoration or clear final candidate state,
- complete persistent logs,
- `final_report.md`.

If runtime forces a smaller search, log the reason and the expected risk.

## Search And Acceptance

You may use Optuna or deterministic scans. Search objectives may combine:

- global Overall,
- global component scores,
- bottom/weak-region Overall,
- regional regression penalties,
- Spatial Distribution preservation,
- Regional/Global trade-off penalties,
- complexity penalties.

The search objective is only a guide. Final acceptance must be based on official global ILAMB, official regional ILAMB, and public TRENDY/firepipe where relevant.

Do not accept a candidate just because global Overall improves. A candidate that raises global Overall while damaging important weak regions is evidence, not success.

## Required Loop

Repeat until further constrained exploration is exhausted:

1. State the physical/regime hypothesis.
2. Define the unified functional-form change.
3. Define the parameter/search space.
4. Run Optuna/search or a documented deterministic scan.
5. Regenerate TRENDY-format `burntArea.nc`.
6. Run official global ILAMB for serious candidates.
7. Run official regional ILAMB for serious candidates.
8. Run public TRENDY/firepipe for serious best-so-far candidates.
9. Compare against baseline and current best using global, regional, public, and mechanistic criteria.
10. Ablate or prune complexity where feasible.
11. Accept, revise, or reject.
12. Log before moving on.

## Hard Constraints

Do not use:

- new external data as model input,
- latitude/longitude hacks,
- per-cell lookup tables,
- named-region routing,
- per-region formulas,
- arbitrary residual correction coefficients,
- score-only hyperparameter fitting without a mechanistic story.

## Evaluation Commands

Baseline verification:

```bash
.venv/bin/python scripts/verify.py
```

Regenerate current model output:

```bash
.venv/bin/python scripts/reproduce_modelC.py
```

Official global ILAMB:

```bash
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh
```

Official regional ILAMB:

```bash
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh
```

Public TRENDY/firepipe benchmark:

```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
PATH="$PWD/.venv/bin:$PATH" \
bash scripts/run_public_trendy_firepipe.sh
```

Known public benchmark caveat: JSBACH may show an ILAMB `IndexError` during the public benchmark. If candidate comparisons complete and the score table is produced, log the caveat and continue.

## Required Logs

Maintain throughout:

- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`

Before finalizing, write:

- `final_report.md`

## Final Report Requirements

`final_report.md` must include:

- executive summary,
- baseline reproduction and benchmark context,
- best accepted model,
- highest global-score model if different,
- best regional model if different,
- baseline vs final global ILAMB table,
- baseline vs serious candidates regional ILAMB table,
- public TRENDY/firepipe ranking table,
- all mechanisms tried,
- Optuna/search setup and trial counts,
- ablation results,
- complexity pruning decisions,
- constraint compliance,
- remaining regional/fire-regime failures,
- why remaining failures appear unresolved under current constraints,
- exact output directories and files needed to reproduce evidence.

Do not stop until `final_report.md` is written.
