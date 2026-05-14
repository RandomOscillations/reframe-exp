# Reframe Pass 2 Continuation Prompt

Paste this into Hermes from the reframe workspace after structural reframe pass 1 has completed and accepted `F3b`.

```text
Continue from the current pass-1 structural reframe result, not from original Model C.

Your current workspace already contains the accepted F3b model:
- original Model C core,
- wet/canopy-moisture suppressor from annual precipitation,
- hyperarid fuel-discontinuity suppressor from Dbar / (P_ann + ratio_p0).

Your job is to push the model-improvement process to a defensible stopping point from this current best model. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

You are free to alter the functional form along with the hyperparameters by using Optuna where useful, with 500-2000 trials at most for substantial searches. Once you believe there is meaningful change, you MUST run official global ILAMB and official regional ILAMB, and use all aspects of the scores to make your judgment.

You are welcome to view this from an angle of different fire types, regional fire regimes, biome-like constraints, or any other angle/hybrid you deem worthy. But the final model must be one global formula. It may not use separate sub-region-level formulas with a black-box routing mechanism. Inferring region-level or fire-type-level physics from allowed cell-level data and encoding them in one global formula that acts differently per inferred state is fair game.

Continue structural reframing. At each hypothesis and subproblem, zoom out and look for structurally similar problems from other fields, then map the analogy back into allowed fire-model terms. Do not use analogies as decoration; use them to generate concrete, testable mechanism families. Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example is the neonatal handover problem, where doctors drew inspiration from F1 pit crews and translated the shared structure of team organization and efficiency into operating-room handover design. Zoom out and look for such parallels structurally for this specific problem scenario. Do this at each sub-level of whatever hypothesis or approach you are taking.

Run repeated outer and inner loops. Each outer loop should inspect global and regional failures, state the missing physical mechanism, define one unified mechanism family, use Optuna or deterministic search as the inner loop, evaluate serious candidates, then accept/reject and use the failure pattern to choose the next hypothesis. Do not treat one Optuna/search run as exhaustion of the research process.

Make sure to perform ablations to properly prune complexity where necessary. Make sure to log what you try. Do not stop because a candidate improves global Overall. Keep a best-so-far model and continue until further constrained model exploration is exhausted.

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

Maintain separate pass-2 logs throughout:
- research_log_pass2.md,
- candidate_registry_pass2.md,
- eval_log_pass2.md,
- regional_analysis_pass2.md,
- constraint_checks_pass2.md.

When you believe all possible directions/angles are exhausted, write final_report_pass2.md. Include the set of best models you found: global best, regional best, balanced best, and final accepted model if these differ. Include related rankings, mechanisms tried, Optuna/search trial counts, ablations, reasoning behind choosing or rejecting models, where the model still fails, and why remaining failures appear unresolved under the current constraints.

Do not stop until final_report_pass2.md is written.
```
