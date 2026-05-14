# Base Prompt Draft

Paste this into Hermes from:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base
```

```text
Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, and BASELINE_REPRO.md before doing anything else. Do not stop until final_report.md is written.

Start from original Model (C). Your job is to push the model-improvement process to a defensible stopping point. The current model performs well (offline) and ranks #1 on the benchmark. However, there are caveats and improvements which can be made. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

First triage where the base model is performing well and where it is not over regions by running the benchmark. Then figure out how to incrementally help improve the per-region scores without cheating (see below), one by one, by trying out different things while adhering to the pipeline. Do a deep dive.

You are free to alter the functional form along with the hyperparameters by using Optuna with 500-2000 trials at most for substantial searches where runtime allows. Once you believe there is meaningful change, you MUST run the official global and regional ILAMB and use all aspects of the scores to make your judgement.

You are welcome to view this from an angle of different fire types: such as cropland, forest fire, etc. or different region types or any other angle/hybrid you may deem worthy. But you must have one global formula, ie. you may not have separate sub-region level formulas with some black box type routing mechanism for instance. Inferring region level physics/fire type level physics from cell level data and encoding them all in some global functional form which "acts differently" per "type" is fair game.

Run repeated outer and inner loops. Each outer loop should inspect global and regional failures, state the missing physical mechanism, define one unified mechanism family, use Optuna or deterministic search as the inner loop, evaluate serious candidates, then accept/reject and use the failure pattern to choose the next hypothesis. Do not treat one Optuna/search run as exhaustion of the research process.

Treat this as a long-horizon, multi-hour `/goal` run. Do not stop after one or two mechanism families, and do not treat one weak Optuna/search result as exhaustion. If a direction gives marginal movement, first push the local family properly: inspect the failure pattern, try justified variants, run an adequate search, run official evals for serious variants, and perform ablations. Only then reject or demote it and move to a different plausible mechanism family. Improvements only in the third decimal place are not meaningful by themselves; they are evidence to analyze, not a stopping condition. Continue grinding until you either find a meaningful, mechanistically defensible delta or can explain why all remaining plausible directions are exhausted under the constraints.

Make sure to perform ablations to properly prune complexity where necessary. Make sure to log what you try out. Do not stop because a candidate improves global Overall. Keep a best-so-far model and continue until further constrained model exploration is exhausted.

A candidate is not acceptable unless it has:
- official global ILAMB,
- official regional ILAMB,
- public TRENDY/firepipe comparison if serious,
- mechanistic explanation,
- constraint compliance,
- ablation or diagnostic support when feasible.

Do not use:
- new external data as model input,
- latitude/longitude hacks,
- per-cell lookup tables,
- named-region routing,
- arbitrary residual correction coefficients.

Maintain these logs throughout:
- research_log.md
- candidate_registry.md
- eval_log.md
- regional_analysis.md
- constraint_checks.md

When you believe all possible directions/angles are exhausted note down the set of best models you get: this could be global, regional, both, etc along with related rankings, mechanisms tried, your reasoning behind choosing them, where it is failing, and why the remaining failures appear unresolved under the current constraints.

Do not stop until final_report.md is written.

Before proceeding, read necessary files, and reiterate your understanding along with any questions you may have. If you have no blocking questions, continue immediately into baseline verification and the first research loop without waiting for operator confirmation.
```
