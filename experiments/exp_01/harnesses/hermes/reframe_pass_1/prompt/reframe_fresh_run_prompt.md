# Reframe Fresh Run Prompt

Paste this into Hermes from the fresh reframe workspace.

```text
Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, and BASELINE_REPRO.md before doing anything else. Do not stop until final_report.md is written.

Start from original Model (C). Your job is to push the model-improvement process to a defensible stopping point. The current model performs well (offline) and ranks #1 on the benchmark. However, there are caveats and improvements which can be made. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

You are free to alter the functional form along with the hyperparams (by using optuna by using 500-2000 trials at most). Once you believe there is meaningful change, you MUST run the official global and regional ILAMB and use all aspects of the scores to make your judgement.

You are welcome to view this from an angle of different fire types: such as cropland, forest fire, etc. or different region types or any other angle/hybrid you may deem worthy. But you must have one global formula, ie. you may not have seperate sub-region level formulas with some black box type routing mechanism for instance. Inferring region level physics/fire type level physics from cell level data and encoding them all in some global functional form which "acts differently" per "type" is fair game.

Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example of this would be, to solve the neonatal handover problem for newborns, doctors drew inspiration from F1 pit crews and how that analogy can transfer to the ER. The F1 pitstop is highly efficient as the pit crew had 7 seconds to refuel and change the tyres. The surgeons translated it to the ER to specify where everyone should be positioned and how to operate, bringing down errors and the duration of handover. Both problems share the same structure of team organization and efficiency. Zoom out and look for such parallels structurally for this specific problem scenario. You need to do this at each sub-level of whatever hypothesis/approach you are taking.

Run this as repeated outer and inner loops. Each outer loop should inspect global and regional failures, state the missing physical mechanism, define one unified mechanism family, use Optuna or deterministic search as the inner loop, evaluate serious candidates, then accept/reject and use the failure pattern to choose the next hypothesis. Do not treat one Optuna/search run as exhaustion of the research process.

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

When you believe all possible directions/angles are exhausted note down the set of best models you get: this could be global, regional, both, etc along with related rankings + mechanisms tried + your reasoning behind choosing them, where it is failing and why the remaining failures appear unresolved under the current constraints.

Do not stop until final_report.md is written.

Before proceeding, read necessary files and briefly reiterate your understanding. If you have no blocking questions, continue immediately into baseline verification and the first research loop without waiting for operator confirmation.
```
