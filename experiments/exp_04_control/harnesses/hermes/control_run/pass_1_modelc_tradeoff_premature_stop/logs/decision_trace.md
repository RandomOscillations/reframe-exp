# Decision Trace

## D0 — Baseline-first protocol
- Observed failure or clue: Workspace instructions require baseline verification and evaluation before any model changes.
- Hypothesis/decision: Establish locally reproduced original Model C as the only valid baseline for this run.
- Why selected next: Required by `BASELINE_REPRO.md` and necessary for defensible comparisons.
- Alternatives considered: Using README pinned scores directly; rejected because local reproduction is required.
- Command/evaluation run:
  - `.venv/bin/python scripts/verify.py`
  - `.venv/bin/python scripts/reproduce_modelC.py`
  - `PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh`
  - Regional ILAMB over GFED regions.
- Result: Baseline global Overall 0.671529; regional component failures concentrated in CEAM/EURO/MIDE/TENA and low spatial scores in several regions.
- Decision: Accept as run baseline and proceed to failure triage/search.
- Implication for next loop: Explore mechanisms that can repair regional spatial/bias behavior without sacrificing Model C's strong global seasonal score.

## D1 — Mechanism family selection for first search wave
- Observed failure or clue: Baseline has excellent global seasonal behavior but weak regional component scores in low/fire-complex regions, especially poor regional spatial distribution and bias/RMSE in CEAM, EURO, MIDE, TENA.
- Hypothesis chosen: Missing global mechanisms likely involve precipitation-shape/fuel-moisture balance, heat-window suppression, humid-region suppression, or refit tradeoffs rather than black-box regional correction.
- Why selected next: These mechanisms are physically interpretable, use only allowed inputs, and can act differently by cell state without named-region routing.
- Alternatives considered:
  - Lat/lon or GFED-region gates: rejected as forbidden.
  - Per-region coefficients/residual correction: rejected as forbidden.
  - External land-cover/cropland/forest data: rejected as outside fixed input contract.
- Command/evaluation run: `N_TRIALS_PER_FAMILY=500 .venv/bin/python scripts/run_modelC_mechanism_experiments.py`.
- Result: Candidate proxy scores improved regional diagnostics but not clearly global fit. Best proxy candidate was `fuel_moisture_balance`.
- Decision: Promote all five families to official global/regional ILAMB because proxy/regional tradeoffs were informative and because the user requested a deep dive.
- Implication for next loop: Use official ILAMB, not proxy, for accept/reject.

## D2 — Official global/regional candidate evaluation
- Observed failure or clue: Proxy searches found regional gains but possible global spatial penalties.
- Hypothesis tested: One of the new smooth physical gates may improve enough regional behavior to justify a small global tradeoff or possibly reveal a better global optimum.
- Why selected next: Official ILAMB is required for serious candidates.
- Alternatives considered: Continuing to tune proxy only; rejected because proxy is approximate and can overfit regional objective.
- Command/evaluation run:
  - Official global: `ilamb/output_candidates_global_full`.
  - Official regional: `ilamb/output_candidates_regions`.
- Result: No candidate beat Model C global Overall. Closest was `temp_window` at 0.659200 vs 0.671529. Regional derived means improved for all candidates, especially `precip_shape` (0.615108) and `fuel_moisture_balance` worst-region repair (min 0.421151).
- Decision: Reject all new candidates as final models. Keep original Model C as best global and final model. Record regional-improvement candidates as diagnostic alternatives, not accepted replacements.
- Implication for next loop: The improvement frontier is a tradeoff: regional mean can be improved, but global spatial/seasonal behavior drops. Need ablations/diagnostics to determine whether added terms themselves or refit tradeoffs drive results.

## D3 — Ablation diagnostics
- Observed failure or clue: Added mechanisms improved regional diagnostics but harmed global Overall.
- Hypothesis tested: Added terms might be genuinely useful, or improvements might mainly be due to parameter refit/regional-objective tradeoff.
- Why selected next: Candidate acceptance requires ablation/diagnostic support where feasible.
- Alternatives considered: Full official ILAMB for every ablated variant; rejected as excessive once full candidates had already failed global acceptance. Proxy ablation is sufficient diagnostic support for rejection.
- Command/evaluation run: `.venv/bin/python scripts/run_proxy_ablations.py`.
- Result: Added terms were not uniformly beneficial. For example, fuel-moisture relief improved proxy global spatial but slightly worsened regional mean/min relative to its ablated refit; precipitation exponents had tiny proxy objective effect. This indicates no clean added mechanism produced a robust step-function improvement.
- Decision: Demote added mechanisms to diagnostic insights; do not accept.
- Implication for next loop: Additional complexity is not justified without new allowed explanatory variables.

## D4 — Public benchmark and stopping decision
- Observed failure or clue: Original Model C remains best official global candidate; serious final model requires public benchmark comparison if clean root is available.
- Hypothesis/decision: Run isolated public TRENDY/firepipe comparison for reproduced final Model C.
- Why selected next: `WORKSPACE_MANIFEST.md` states `public_benchmark_clean` is available and clean.
- Alternatives considered: Run public benchmark for all rejected candidates; rejected because official global ILAMB already ruled them out as final candidates.
- Command/evaluation run: `MODEL_NAME=ED-ModelC-final-reproduced SRC="$PWD/ilamb/MODELS/ED-ModelC-final/burntArea.nc" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe_clean.sh`.
- Result: Reproduced Model C scored 0.671274, ahead of CLASSIC 0.666048 and CLM6.0 0.660644. The clean root's pre-existing `ED-ModelC-baseline` artifact scored 0.675085. JSBACH emitted an IndexError during pair execution but scalar table was produced.
- Decision: Stop exploration at original Model C as the defensible best final model for this workspace. No tested unified interpretable extension produced a step-function delta over Model C; regional improvements are real but trade off against global benchmark quality.
- Implication: Remaining failures likely require inputs forbidden or absent under the fixed contract: land-use/land-cover/fire type, human ignition/suppression, lightning, vegetation structure, cropland/pasture management, or explicit burned-area observation assimilation (forbidden).
