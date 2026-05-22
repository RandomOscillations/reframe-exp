Continue from the current workspace state. Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, research_log.md, eval_log.md, regional_analysis.md, candidate_registry.md, constraint_checks.md, and final_report.md before doing anything else.

The previous pass is not the endpoint. Treat it as one completed research cycle whose successes and failures should guide the next cycle. Infer the current best-so-far from the logs and reports, but do not anchor on it, overindex on it, or assume its mechanism family is privileged. It is only one piece of evidence.

Learn from the mechanisms already tried in the previous pass and explicitly carry those failure learnings into the next runs. Do not treat the previous candidates as isolated dead ends; use their global, regional, public, and ablation failure modes to decide what the next hypotheses should test. The previous pass mostly explored precipitation/curing suppression variants; do not treat that as exhaustion of the full local search space. Dig deeper into distinct mechanism families and second-order mechanism combinations: interactions between wet suppression, fuel charging, dryness/curing, productivity shape, hyperarid limits, and temperature ignition. The goal is not to rerun shallow variants, but to use what failed to design more informed unified-form mechanisms that may preserve global spatial behavior while repairing weak regions.

Your objective remains unchanged: find whether a unified, mechanistic, interpretable burned-area functional form can produce a step-function improvement over original Model C and the current best-so-far in both official global ILAMB and regional behavior under the fixed input contract. The explanation must be grounded in plausible fire physics, not merely metric movement.

You are free to alter the functional form along with the hyperparams by using Optuna with 500-2000 trials at most when appropriate. Once you believe there is meaningful change, you MUST run the official global and regional ILAMB and use all aspects of the scores to make your judgement.

You are welcome to view this from an angle of different fire types: such as cropland, forest fire, etc. or different region types or any other angle/hybrid you may deem worthy. But you must have one global formula, ie. you may not have separate sub-region level formulas with some black box type routing mechanism for instance. Inferring region level physics/fire type level physics from cell level data and encoding them all in some global functional form which "acts differently" per "type" is fair game.

Run repeated outer and inner loops. Each outer loop should inspect global and regional failures, state the missing physical mechanism, define one unified mechanism family or second-order combination, use Optuna or deterministic search as the inner loop, evaluate serious candidates, then accept/reject and use the failure pattern to choose the next hypothesis. Do not treat one Optuna/search run as exhaustion of the research process.

Do not overindex on one convenient, recently tested, or locally promising method. If a direction gives marginal movement, creates regional tradeoffs, or starts looking like parameter fitting rather than mechanism discovery, push the local family through justified variants and ablations before rejecting or demoting it. Do not stop at the first defensible improvement; treat every accepted candidate as provisional and keep searching for the empirical ceiling for both global fit and regional behavior, across distinct mechanistic families and ablations, until further gains appear exhausted under the fixed constraints. Third-decimal upgrades are not the objective and are not sufficient evidence to stop.

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
- per-region formulas,
- arbitrary residual correction coefficients,
- direct cell-identity fitting to GFED,
- prior experiment/archive evidence outside this workspace.

Maintain and update these files throughout:
- research_log.md
- candidate_registry.md
- eval_log.md
- regional_analysis.md
- constraint_checks.md
- final_report.md

When you believe all possible directions/angles are exhausted note down the set of best models you get: this could be global, regional, both, etc along with related rankings, mechanisms tried, your reasoning behind choosing them, where it is failing, and why the remaining failures appear unresolved under the current constraints.

Do not stop until final_report.md is rewritten with the full continuation result.

Before proceeding, briefly restate your understanding and any blocking questions. If there are no blocking questions, continue immediately into the next research cycle.
