Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, and BASELINE_REPRO.md before doing anything else. Do not stop until final_report.md is written.
Start from original Model (C). Your job is to push the model-improvement process to a defensible stopping point. The current model performs well (offline) and ranks #1 on the benchmark. However, there are caveats and improvements which can be made. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.
First triage where the base model is performing well and where it is not over regions by running the benchmark. Then figure out how to incrementally help improve the per region scores without cheating (see below) one by one by trying out different things while adhering to the pipeline. Do a deep dive.
You are free to alter the functional form along with the hyperparams (by using optuna by using 500-2000 trials at most). Once you believe there is meaningful change, you MUST run the official global and regional ILAMB and use all aspects of the scores to make your judgement.
You are welcome to view this from an angle of different fire types: such as cropland, forest fire, etc. or different region types or any other angle/hybrid you may deem worthy. But you must have one global formula, ie. you may not have seperate sub-region level formulas with some black box type routing mechanism for instance. Inferring region level physics/fire type level physics from cell level data and encoding them all in some global functional form which "acts differently" per "type" is fair game.
Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example of this would be, to solve the neonatal handover problem for newborns, doctors drew inspiration from F1 pit crews and how that analogy can transfer to the ER. The F1 pitstop is highly efficient as the pit crew had 7 seconds to refuel and change the tyres. The surgeons translated it to the ER to specify where everyone should be positioned and how to operate, bringing down errors and the duration of handover. Both problems share the same structure of team organization and efficiency. Zoom out and look for such parallels structurally for this specific problem scenario. You need to do this at each sub-level of whatever hypothesis/approach you are taking.
Make sure to perform ablations to properly prune complexity where necessary. Make sure to log what you try out. Do not stop because a candidate improves global Overall. Keep a best-so-far model and continue until further constrained model exploration is exhausted. Run repeated outer loops of failure triage -> mechanism hypothesis -> search/tune -> global/regional/public evaluation -> ablation -> accept/reject -> next hypothesis, with inner search loops inside each mechanism family. The target is a step-function delta over Model C in both global fit and regional behavior; minimal upgrades such as third-decimal gains or near-tie scalar movements are not meaningful stopping evidence. Keep pushing across distinct mechanistic families until the empirical ceiling appears reached under the fixed constraints.
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
- arbitrary residual correction coefficients,
Maintain these logs throughout:
- research_log.md
- candidate_registry.md
- eval_log.md
- regional_analysis.md
- constraint_checks.md
When you believe all possible directions/angles are exhausted note down the set of best models you get: this could be global, regional, both, etc along with related rankings + mechanisms tried + your reasoning behind choosing them, where it is failing and why the remaining failures appear unresolved under the current constraints.
Do not stop until final_report.md is written.
Before, proceeding read necessary files, and reiterate your understanding along with any questions you may have.
