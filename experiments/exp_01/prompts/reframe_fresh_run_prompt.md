# Reframe Fresh Run Prompt

Paste this into Hermes from the fresh reframe workspace.

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

Structural reframing intervention:

At every major loop, and again inside important subproblems, deliberately zoom out and look for structurally similar problems in other fields. Do not look for surface similarity. Look for shared structure: the same kind of bottleneck, constraint, regime change, coordination problem, threshold, flow, feedback, failure mode, or allocation problem.

Use these cross-domain parallels as inspiration for new mechanistic hypotheses, representations, diagnostics, or ablations. Translate any useful analogy back into the ED fire problem as a concrete, testable, unified-form model change using only the allowed inputs.

Example of the kind of structural transfer to consider: neonatal handover in hospitals was improved by studying Formula 1 pit crews. The domains are different, but both problems share a structure of time-critical coordination, role assignment, and error reduction under pressure. The useful transfer was not "cars are like babies"; it was the deeper organizational structure: where people stand, who does what, and how handoff steps are sequenced.

Apply this style of reasoning to the fire-model problem. For each hypothesis or sub-hypothesis, ask:
- What is the underlying structure of this failure?
- Where else does that structure appear?
- What variables, constraints, or mechanisms become visible through that parallel?
- Can the insight become an interpretable global formula, diagnostic, ablation, or search space under the allowed input contract?

Do not force analogies. If a parallel does not yield a concrete testable mechanism, log it briefly and move on. The analogy is useful only if it improves the scientific search, not as prose decoration.

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
