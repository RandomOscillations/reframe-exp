# Base Fresh Run Prompt

Paste this into Hermes from the fresh base workspace.

```text
Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, and BASELINE_REPRO.md before doing anything else.

Before proceeding, read the necessary files and reiterate your understanding along with any questions you have.

Do not stop until final_report.md is written.

Start from original Model C. Your job is to push the model-improvement process to a defensible stopping point.

The current model performs well offline and ranks strongly on the benchmark. However, there are caveats and improvements that may be possible. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

You are free to alter the functional form and hyperparameters. Use Optuna where appropriate, with substantial searches of 500-2000 trials at most when the direction is promising and runtime allows. Once you believe there is meaningful change, you must run official global ILAMB and official regional ILAMB, and use all aspects of the scores to make your judgment.

The final model must be one global, interpretable formula. It may include smooth ceilings, floors, saturations, humps, thresholds, piecewise functions, interactions, or gates if every term has a physical explanation and uses only allowed inputs.

The optimization goal is not just global Overall. Improve global Overall while preserving or improving regional Overall spread and regional physical realism. Do not accept a candidate that improves global Overall by damaging important weak regions.

Make sure to perform ablations to prune complexity where necessary. Make sure to log what you try. Do not stop because a candidate improves global Overall. Keep a best-so-far model and continue until further constrained model exploration is exhausted.

This is intended to be a serious multi-hour run. Unless blocked, continue working through multiple substantial mechanism families before finalizing. Do not compress the run into a short first-improvement pass.

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
- per-region formulas,
- arbitrary residual correction coefficients,
- score-only hyperparameter fitting without a physical mechanism.

Maintain these logs throughout:
- research_log.md
- candidate_registry.md
- eval_log.md
- regional_analysis.md
- constraint_checks.md

When you believe all possible directions/angles are exhausted, write final_report.md. Include the set of best models you found: global best, regional best, balanced best, and final accepted model if these differ. Include related rankings, mechanisms tried, Optuna/search trial counts, ablations, reasoning behind choosing or rejecting models, where the model still fails, and why remaining failures appear unresolved under the current constraints.

Do not stop until final_report.md is written.
```
