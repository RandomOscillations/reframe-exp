# Experiment 03 Reasoning Pathway Analysis

Date: 2026-05-22

Scope: Hermes Agent runs for Experiment 03 on the ED Model C fire benchmark, comparing the structural-reframe prompt against the matched non-reframe/control prompt across three autoresearch passes.

Focus: This document does not evaluate whether the model scores are practically important. It evaluates how the agents reasoned: what hypotheses they formed, how they interpreted failures, how they chose the next mechanism family, and whether the reframe prompt changed the pathway to the final decision.

## 1. Executive Conclusion

The structural-reframe prompt did not create a new kind of agent, and it did not prove a step-function improvement in autonomous scientific reasoning. It did, however, measurably changed the agent's search prior.

The control agent mostly followed a local repair pathway:

> Weak regions are overpredicted. Add physically plausible suppressors. When suppressors damage global spatial skill, make them more selective. When selective suppressors still fail, try a more nuanced live-fuel/curing suppressor. Conclude that the fixed input contract does not cleanly separate the remaining fire regimes.

The reframe agent followed a structural mechanism-composition pathway:

> Fire is an interlock or handoff problem. Single gates are too blunt. Search for conditional release windows, guards, corridors, live-fuel transitions, monsoon handoffs, and mosaic-edge regimes. When no single candidate dominates, preserve a Pareto frontier as the scientific conclusion.

The important distinction is not that the reframe run "thought harder" in a generic sense. The distinction is that the reframe run transformed failures into new structural frames more aggressively and earlier. It searched more in "mechanism topology" space: release windows, corridors, edge states, handoffs, guards. The control run searched more in "local correction" space: suppressors, gated suppressors, and eventually a live-fuel suppressor.

The final comparison is nuanced:

- The reframe prompt did change the reasoning pathway.
- The added paragraph is the most plausible cause of that change, because it was the only prompt difference and the reframe logs explicitly echo its vocabulary and mode of operation.
- But from one paired experiment, we cannot prove the paragraph was the only cause of every different mechanism. Randomness, path dependence, and earlier candidate discoveries matter.
- The control agent eventually developed more sophisticated mechanism hypotheses in pass 3, especially live-fuel/curing. This means the reframe paragraph changed the search prior and the route, not the agent's fundamental capabilities.

My best formulation for the paper:

> The structural-reframe paragraph acted as a search-prior intervention. It did not produce a categorical reasoning upgrade, but it caused the agent to externalize and repeatedly use structural analogies as hypothesis generators. This shifted the trajectory from incremental suppressor refinement toward mechanism-composition search: release windows, guards, corridors, handoffs, and mosaic-edge regimes. The control run eventually reached one subtle state-based mechanism, but only after exhausting more local suppressor variants.

## 2. The Prompt Difference

The starting control prompt and starting reframe prompt are identical except for this paragraph:

```text
Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example of this would be, to solve the neonatal handover problem for newborns, doctors drew inspiration from F1 pit crews and how that analogy can transfer to the ER. The F1 pitstop is highly efficient as the pit crew had 7 seconds to refuel and change the tyres. The surgeons translated it to the ER to specify where everyone should be positioned and how to operate, bringing down errors and the duration of handover. Both problems share the same structure of team organization and efficiency. Zoom out and look for such parallels structurally for this specific problem scenario. You need to do this at each sub-level of whatever hypothesis/approach you are taking.
```

Local diff checked:

- Control prompt: `reframe-exps/experiments/exp_03_control/harnesses/hermes/base_run/pass_1_precip_curing_control/prompt/control_prompt.md`
- Reframe prompt: `reframe-exps/experiments/exp_03/harnesses/hermes/reframe_run/pass_1_release_window_cand3/prompt/reframe_prompt.md`

The diff shows that the paragraph above is exactly the only added content in the reframe prompt.

This matters because the intervention was small. It did not give the reframe agent a concrete mechanism. It did not say "try release windows", "try corridors", "try edge mosaics", "try live-fuel senescence", or "try monsoon breaks." It only instructed the agent to search for structural analogies, including cross-domain analogies, at each sub-level of the research process.

Therefore, the central causal question is:

> Did that one paragraph actually change the agent's reasoning path, or did the reframe run merely get luckier while doing the same kind of search?

The evidence supports a middle answer:

> The paragraph was taken up by the reframe agent and shaped its hypothesis language and mechanism choices. But the resulting mechanisms were still grounded in the same ED/fire physics task, the same allowed inputs, the same evaluation loop, and the same local experimental machinery. The reframe paragraph changed the search prior, not the entire research loop.

## 3. What Would Count As Evidence Of A Reasoning Pathway Difference?

Because we care about reasoning rather than outcome, the relevant evidence is not "which candidate scored best." The relevant evidence is:

1. What initial problem representation did the agent form?
2. What did the agent infer from the first failures?
3. Did it merely make the same class of mechanism milder/stronger, or did it change the mechanism class?
4. Did it use failures as dead ends, or as information for new hypotheses?
5. Did it explicitly preserve and update a research frame?
6. Did it search from surface similarity or from structural analogy?
7. Did it distinguish roles for candidates, or force every candidate into one scalar ranking?
8. Did it articulate why remaining failures are unresolved?

This document compares the runs on those axes.

## 4. Shared Starting Point

Both agents began from the same scientific setup:

- Original Model C was the incumbent.
- The objective was not merely to maximize one scalar score.
- The agent had to preserve one global, mechanistic, interpretable burned-area formula.
- It could only use fixed-contract inputs: dbar, annual/monthly precipitation, air temperature, monthly GPP, and transformations of those fields.
- It could not use external inputs, latitude/longitude hacks, named-region routing, per-cell lookup tables, residual correction maps, or per-region formulas.
- It had to run official global and regional ILAMB for serious candidates.
- It had to maintain logs and write a final report.

Both agents also diagnosed roughly the same baseline failure:

- Model C is globally strong.
- The weakest named regions are things like Europe, Central America, Temperate North America, Middle East, Southeast Asia, Southern Hemisphere South America, and Equatorial Asia.
- Many weak regions are not failing primarily by seasonality.
- The failures often involve magnitude and spatial placement.
- The weak regions are heterogeneous: cool productive low-fire mosaics, humid tropical regions, monsoon regions, arid managed/irrigated regions, etc.
- Missing variables probably include land use, human ignition/suppression, management, fragmentation, vegetation structure, peat/deforestation fire type, irrigation, and fuel continuity.

So the difference is not that the reframe agent saw a different problem. It saw substantially the same problem, then chose a different hypothesis-generation style.

## 5. Control Run Reasoning Pathway

### 5.1 Control Pass 1: Direct Suppression Of Overpredicted Regions

The control agent's first pass is best described as a direct repair strategy.

The reasoning chain was:

1. Model C performs well globally but overpredicts weak regions.
2. Weak regions are often humid, wet, productive, fragmented, or low-fire.
3. The allowed inputs cannot include direct land-use or human suppression variables.
4. Therefore, approximate missing suppression processes using smooth global functions of precipitation, monthly wetness, and curing.

This produced three core families:

#### H1: Annual humid suppression

Reasoning:

- Model C has an annual precipitation floor.
- It may lack an upper wet limb.
- Very humid systems may have high productivity but insufficient curing.
- Therefore add a high-annual-precipitation suppressor.

Mechanism:

```text
1 / (1 + (P_ann / P_humid)^q)
```

Interpretation:

This was a straightforward "too wet to burn" correction.

#### H2: Wet-month logistic suppression

Reasoning:

- Model C's monthly precipitation dampener may be too weak.
- Current wet months should suppress active fire more sharply.

Mechanism:

```text
supp(P_month; wet_k, wet_c)
```

Interpretation:

This was a current-rain/wet-month correction.

#### H3: Seasonal contrast / curing gate

Reasoning:

- Absolute monthly precipitation may not transfer across climates.
- A month should be judged relative to the local annual precipitation climatology.
- Fires occur when a month is dry relative to local climate.

Mechanism:

```text
1 / (1 + (P_month / (P_ann / 12 + eps))^q)
```

Interpretation:

This was still a suppressor, but more climatologically normalized.

### 5.2 Control Pass 1 Failure Interpretation

The control agent learned:

- These mechanisms improved some weak regions.
- But they degraded global spatial distribution too much.
- The fact that weak regions improved meant the diagnosis was not nonsense.
- The fact that global spatial skill collapsed meant the mechanisms were too broad.

The key control pass 1 inference was:

> Wetness/curing suppression is physically plausible, but smooth global suppressors suppress cell states that overlap with regimes where Model C already performs well.

This is a good scientific inference. It just remains inside the same frame: "make the suppressor less blunt."

### 5.3 Control Pass 2: Gated Suppressors And More Selective Local Proxies

Control pass 2 continued from pass 1's failure learning. It did not abandon the suppressor frame. It refined it.

The reasoning chain was:

1. Broad annual/monthly wet suppressors damage global spatial skill.
2. Therefore suppress only when multiple physical conditions imply nonflammability.
3. Use allowed-input diagnostics to detect whether weak regions can be separated from good regions.
4. Try second-order conditions.

This produced:

- dry-gated annual humid suppression,
- dry-gated wet-month suppression,
- wet productive forest / closed-canopy suppression,
- hyperarid low-fuel suppression,
- cool uncured ignition interaction,
- productivity shape retuning.

#### H4: Dry-gated wet-month suppression

This was the most important pass 2 reasoning step.

The agent reasoned:

- H2's wet-month suppression is too broad.
- But wet months should suppress fire if antecedent drying is insufficient.
- Therefore combine monthly wetness with low accumulated deficit.

Mechanism:

```text
1 - wet_alpha * lowdry(Dbar) * (1 - wet(P_month))
```

This is still suppression, but now conditional suppression.

The failure was informative:

- H4 improved all listed weak regions.
- But global spatial skill collapsed.
- Therefore even a physically gated wet suppressor could not isolate the weak regimes from globally important regimes.

The control agent's pass 2 final boundary was:

> The weak regions are not a single separable class under the five allowed inputs. Strong regional repair seems coupled to damage in boreal, African, Australian, and central Asian patterns.

### 5.4 Control Pass 3: More Distinct State-Based Suppressors

Control pass 3 is where the control reasoning became more sophisticated.

The pass 3 final report explicitly says:

> "The previous pass was not the endpoint. I continued with a third research cycle using the prior failures to design distinct second-order mechanism families beyond shallow precipitation/curing variants."

This means the control agent did update its approach. It did not blindly continue H1-H4.

The cycle 3 design implication was:

- Do not rerun broad precipitation gates.
- Search for mechanisms that condition fuel availability and burnability more selectively.

The new families were:

#### H5: Savanna-protected wet suppression

Reasoning:

- Previous wet gates may have failed because they suppress real warm/cured savanna fires.
- Add a savanna-state relief term based on high Dbar, warm air temperature, and intermediate annual GPP.

This is still a wet suppressor, but with a protection term.

Reasoning form:

> "Suppress wet/humid regions, but protect savannas."

#### H6: Live-fuel/curing interaction

This is the most important control pass 3 mechanism.

Reasoning:

- GPP is not just fuel availability.
- Annual GPP can represent fuel charge.
- Current GPP can represent live green vegetation and live fuel moisture.
- Fire should be suppressed when annual fuel charge exists but current live GPP, current wetness, and insufficient accumulated deficit imply live/wet fuels rather than cured combustible fuels.

Mechanism concept:

```text
1 - alpha * charge(GPP_ann) * live(GPP_current / GPP_ann) * lowdry(Dbar) * wet(P_month)
```

This is a meaningful conceptual shift. It reinterprets GPP as dual-role:

- annual GPP = fuel supply / charge,
- current relative GPP = live moisture / uncured fuel state.

That is richer than H1-H4. It is not just "more precipitation suppression."

However, it is still structurally a suppressor:

> suppress active burning when the fuel is live/wet/uncured.

The control run then did local family search around H6:

- H8: live-fuel/curing with retuned base,
- H9: combined cycle-3 model,
- H6a: half-alpha ablation.

The stronger H8/H9 versions improved weak regions more but collapsed spatial skill. The half-alpha ablation preserved spatial skill better but weakened regional repair. This reinforced the same boundary:

> Stronger correction repairs weak regions but damages global spatial distribution.

### 5.5 Control Final Reasoning

The control final reasoning was:

1. Pass 1 proved naive wet/humid suppressors are too broad.
2. Pass 2 proved gated wet/humid suppressors are still too broad.
3. Pass 3 found that live-fuel/curing is the only family that gives a small improvement without catastrophic spatial collapse.
4. Stronger versions of live-fuel/curing repeat the same spatial-collapse pattern.
5. Therefore H6/H6a are not a step-function replacement.
6. The remaining failures likely need missing variables forbidden by the contract.

The control reasoning is disciplined and cumulative. It learns from failure. But its search remains mostly in a local-correction frame:

> find a smoother, more selective suppressor that repairs overprediction without damaging globally important regimes.

## 6. Reframe Run Reasoning Pathway

### 6.1 Reframe Pass 1: Structural Analogy As Initial Search Prior

The reframe run begins with the only prompt addition: draw parallels from other fields, inspect the structure of the problem, and use analogies at each sub-level.

The agent immediately takes up that instruction. Early in the reframe research log, it writes:

> "Structural analogy framing to guide hypotheses: burned area behaves like a reliability/epidemic/combustion chain where ignition requires simultaneous susceptible fuel, transmission/weather contact, and non-suppressed moisture state. Like F1 pit work translated to neonatal handover, the transferable structure is not the domain content but the synchronized bottleneck: if any gate is mistimed, regional failure appears even if global aggregate is strong."

This is the key evidence that the reframe paragraph was not ignored. The agent explicitly:

- names structural analogy,
- references the F1/neonatal transfer logic,
- abstracts the problem to synchronized bottlenecks,
- uses that abstraction to guide hypotheses.

This does not prove that every later mechanism came "just from" the paragraph, but it does prove the paragraph entered the agent's reasoning trace.

### 6.2 Reframe Pass 1 Initial Families

The first search still includes some mechanisms similar to what control later tried:

- re-optimization,
- annual precipitation hump,
- wet forest curing,
- antecedent fuel,
- drydown/curing gate,
- fuel-moisture balance,
- partial wet suppression.

So reframe did not immediately jump into alien solution space. It began with plausible fire-physics extensions too.

But even in pass 1, the framing differs:

- Control frames the issue as overprediction requiring suppression.
- Reframe frames the issue as a multi-condition fire chain requiring synchronized alignment.

This matters because after initial failures, reframe does not only make suppressors milder. It builds release windows and interlocks.

### 6.3 Reframe Pass 1 Failure Interpretation: Single Gates Are Too Blunt

After initial mechanisms failed or traded off, the reframe agent inferred:

- blunt wet suppression can repair weak regions but hurts global Spatial,
- fuel charging alone can damage strong fire belts,
- naked drydown is prunable,
- current dryness, precipitation regime, and GPP/fuel state need to be combined.

Then the agent explicitly uses a new structural analogy:

> "multi-factor interlocks, like a circuit breaker or reservoir spillway: second-order gates should trip only when multiple physical states coincide."

This is a different failure response from the control pass 1 response.

Control response:

> "The suppressor was too broad. Gate it by dryness."

Reframe response:

> "The mechanism should be a synchronized interlock. Search for conditional release and protection windows."

### 6.4 Reframe Pass 1 Second-Order Mechanisms

The reframe agent creates:

- wet_x_lowdef,
- wet_x_persist,
- wet_supp_fuel_release,
- gpp_wet_cap,
- hyperarid_balance,
- curing_window,
- release_window,
- release_window_wetcap.

The key family is the release window.

Conceptually, it is not merely "wet regions should be suppressed." It says:

> Fire should be released or boosted only when current dryness, intermediate precipitation, and intermediate GPP/fuel state align, with a soft wet/low-deficit cap.

This is a mechanism-composition move:

- allow fire in a narrow state,
- suppress or cap outside that state,
- preserve strong regions by not applying a broad global suppressor.

This became Cand3.

### 6.5 Reframe Pass 2: Failure Translated Into New Analogies

Pass 2 continues from Cand3's caveats.

The carried-forward learnings were:

- Cand3 improved broadly but had BONA/NHSA caveats.
- Blunt wet suppression hurts spatial skill.
- Fuel charging alone damages African/boreal belts.
- Raw drydown can be pruned.
- Simple temperature interlock failed.

Then the agent created third-order mechanisms from structural analogies:

#### Relay-protection grid -> guarded release

Reasoning:

- Release helps some regions but over-activates others.
- A power grid uses protection logic to prevent unwanted activation in vulnerable subcircuits.
- Translate this to a cold/short-season productive guard.

#### Live-fuel senescence -> senescence release

Reasoning:

- Drydown derivative was pruned, but curing may still matter.
- Instead of raw dbar drydown, use live-fuel senescence / productivity drawdown as a proxy for curing.

#### Combustion corridor -> dual-corridor balance

Reasoning:

- Fire requires a corridor between too little fuel and too much wetness.
- Suppress both hyperarid fuel absence and wet-canopy nonflammability.

#### Supply-chain / F1 bottleneck -> warm-dry supply chain

Reasoning:

- Fire happens when fuel, warmth, lack of rain, and dryness all align.
- Like a supply chain, a bottleneck at any station blocks throughput.

This is the sentence in the previous summary that the user is asking about:

> "Then it generated new third-order mechanisms from structural analogies."

Did that come from just the reframe prompt?

Best answer:

> The logs strongly suggest that the reframe paragraph caused or at least strongly shaped this behavior in the reframe run, because the paragraph was the only prompt difference and the agent explicitly used the paragraph's requested mode: cross-domain structural analogy at sub-levels. But we should not claim deterministic causality from one run. The mechanisms also depended on prior failures, fire-domain knowledge, and ordinary agent search. The reframe paragraph changed the hypothesis-generation prior; it did not single-handedly specify the mechanisms.

### 6.6 Reframe Pass 2 Decision

The pass 2 decision is already different from control:

- It does not just reject or accept one candidate.
- It preserves a split:
  - global/public leader,
  - broad regional candidate,
  - informative rejected mechanisms.

The agent interprets the result as a Pareto frontier rather than a simple "found / not found" endpoint.

This is a reasoning difference. The reframe agent is treating candidate families as evidence about the structure of the problem, not only as candidate solutions.

### 6.7 Reframe Pass 3: Pareto Frontier And Edge/Mosaic Structural Search

Pass 3 starts from a split:

- Cand4Abl leads global/public but harms some regions.
- Cand3 is broader regionally but lower globally/publicly.
- Dual corridors repair weak regions but hurt BONA/Africa.
- Senescence repairs some regions but loses strong-belt fidelity.
- Hotboost and raw drydown were pruned.
- Blunt wet suppression hurts global Spatial.

The next hypotheses target:

> "the specific handoff between wet-season fuel charging, dry-season rain breaks, live-fuel senescence, hyperarid limits, and wet-canopy caps."

Then it creates:

#### Monsoon break release

Structural analogy:

- supply-chain handoff / F1 pit-stop,
- wet/productive fuel charging only matters if a rain-free break and curing follow.

Reasoning:

> A monsoon system is not simply wet or dry. It has phases. Fire becomes possible when wet-season fuel charge is followed by a break that allows curing and burnability.

#### Mosaic edge release

Structural analogy:

- fire-line / forest-edge mosaic.

Reasoning:

> Wet productive cores stay capped, but humid-region dry edges become burnable when high fuel, rain hiatus, and senescence coincide.

This is one of the strongest examples of reframe-style reasoning. It is not merely applying a smoother suppressor. It is positing different subcell fire behavior inferred from allowed variables.

#### Protected corridor

Structural analogy:

- power-grid protection.

Reasoning:

> Keep useful corridor terms but protect cold productive short-season cells and monsoon phase from over-activation.

### 6.8 Reframe Pass 3 Decision

The agent then performs a deterministic edge-mix sweep:

- no edge mix,
- partial edge mix,
- full edge mix.

This is important reasoning evidence. It does not merely ask "which one scores highest?" It asks:

> Is there a continuous tradeoff between public/global behavior and regional repair?

The answer becomes the final scientific interpretation:

- no edge mix is the public/global leader,
- half edge mix is the balanced Pareto compromise,
- full mosaic edge is strongest weak-region repair,
- remaining BONA/strong-belt versus humid/monsoon repair tradeoff appears unresolved under the fixed input contract.

This is a qualitatively different final decision structure from the control:

Control final decision:

> H6/H6a are tiny improvements, not a step-function. Retain C0 as stability reference; H6a/H6 are marginal successors depending on criteria.

Reframe final decision:

> There is a Pareto frontier of mechanisms. Preserve separate candidates by use case: global/public leader, balanced compromise, broad weak-region repair. Do not pretend one candidate dominates.

## 7. Did The Third-Order Reframe Mechanisms Come From The Reframe Paragraph?

### 7.1 What We Can Say Strongly

The reframe paragraph is the only prompt delta. The reframe logs explicitly show the agent using the added instruction.

Evidence:

- The reframe prompt asks the agent to draw parallels from other fields, inspect structure, and do this at each sub-level.
- The reframe agent's first research-log entry says it is using "structural analogy framing" and explicitly references the F1/neonatal handover example.
- The reframe agent repeatedly names cross-domain analogies in later passes:
  - circuit breaker,
  - reservoir spillway,
  - relay-protection grid,
  - supply-chain / F1 bottleneck,
  - combustion corridor,
  - fire-line / forest-edge mosaic,
  - power-grid protection.
- Those analogies correspond to concrete formula families, not just decorative prose.

Therefore:

> In this run, the reframe addendum was actively taken up and materially shaped the language and organization of hypothesis generation.

### 7.2 What We Cannot Honestly Claim

We cannot claim:

- the reframe paragraph deterministically caused every later mechanism,
- the control agent could never have found those mechanisms,
- the reframe agent had a fundamentally different cognitive ability,
- the structural analogies alone generated the improvements,
- or the third-order mechanisms came "only" from the paragraph.

Reasons:

1. One paired run is not enough for causal proof.
2. LLM sampling/path dependence matters.
3. The agents had different intermediate states after pass 1.
4. Once Cand3 existed, subsequent mechanisms were conditioned by Cand3's failure modes.
5. The control pass 3 eventually generated a subtle live-fuel/curing mechanism without the reframe paragraph.
6. The base prompt already allowed "different fire types", "different region types", "hybrid angles", and "deep dive."

The correct causal strength is:

> The paragraph is the most plausible explanation for the reframe run's earlier and more explicit structural-analogy pathway, but the evidence supports search-prior shift rather than deterministic causal proof.

### 7.3 Why The Paragraph Was Enough To Matter

The paragraph does three things:

1. It instructs cross-domain retrieval.
2. It says to look for shared structure rather than surface similarity.
3. It requires the agent to do this at each sub-level of the hypothesis/approach.

That last clause is important:

> "You need to do this at each sub-level of whatever hypothesis/approach you are taking."

This likely explains why the reframe agent did not only use analogy once. It used analogy recursively:

- global problem: synchronized bottleneck,
- pass 1 failure: circuit-breaker / reservoir interlock,
- pass 2 mechanisms: relay protection, supply chain, combustion corridor, senescence,
- pass 3 mechanisms: monsoon handoff, mosaic edge, protected corridor,
- final interpretation: Pareto frontier of edge-mix mechanisms.

The paragraph did not provide answers. It provided a repeated cognitive move:

> When stuck or refining, ask what structural pattern from another domain this resembles.

That is exactly what appears in the reframe logs.

## 8. Control Versus Reframe Across Passes

### 8.1 Pass 1 Comparison

Control pass 1:

- starts from regional overprediction,
- tries wet/humid/curing suppressors,
- interprets failures as broad suppressors hurting spatial skill,
- concludes more selective mechanisms are needed.

Reframe pass 1:

- starts from the same regional overprediction,
- explicitly frames fire as a synchronized bottleneck chain,
- tries broader fire-physics families,
- after failures, develops multi-factor interlocks,
- discovers conditional release window logic.

Difference:

> Control pass 1 asks "what suppressor can repair these regions?" Reframe pass 1 asks "what set of conditions must align for fire to be released without breaking the global pattern?"

### 8.2 Pass 2 Comparison

Control pass 2:

- keeps the suppressor frame,
- makes suppressors more selective,
- tests dry-gated wetness, wet productive forest, hyperarid, cool uncured, productivity retuning,
- concludes the weak regions are not separable by allowed inputs.

Reframe pass 2:

- starts from release-window caveats,
- turns failures into new structural analogies,
- tests guarded release, senescence release, dual corridor, supply-chain alignment, Pareto guarded corridor,
- interprets the result as a split between global/public leader and broad regional candidate.

Difference:

> Control pass 2 refines the original repair operation. Reframe pass 2 mutates the frame around the repair operation.

### 8.3 Pass 3 Comparison

Control pass 3:

- finally moves beyond precipitation/curing gates,
- tries state-based live-fuel/curing, savanna-protected wetness, Dbar tail, etc.,
- finds H6/H6a as marginal improvements,
- concludes stronger versions collapse spatial skill.

Reframe pass 3:

- continues from an explicit Pareto split,
- tests monsoon handoff, mosaic edge, protected corridor,
- performs an edge-mix sweep,
- concludes the final state is a Pareto frontier of mechanisms, not one clean winner.

Difference:

> Control pass 3 finds a small conservative local successor. Reframe pass 3 maps a tradeoff surface between mechanism roles.

## 9. Key Reasoning Differences

### 9.1 Initial Frame

Control:

> Weak regions are overpredicted; missing process likely suppresses fire.

Reframe:

> Fire is a synchronized interlock; failures may come from mistimed gates, missing release conditions, or unmodeled regime transitions.

### 9.2 How Failure Is Used

Control:

> Failure means the suppressor was too broad, so make it more selective or milder.

Reframe:

> Failure reveals which structural relation is missing, so create a new mechanism class.

### 9.3 Mechanism Grammar

Control grammar:

- suppress,
- gate suppression,
- protect good regions,
- retune shape,
- ablate strength.

Reframe grammar:

- release window,
- interlock,
- corridor,
- guard,
- handoff,
- edge/mosaic,
- phase,
- Pareto sweep.

### 9.4 Candidate Interpretation

Control:

> Accept or reject candidate relative to C0; keep H6/H6a only as marginal successors.

Reframe:

> Preserve candidate roles: public/global leader, balanced compromise, broad regional repair, rejected but informative mechanisms.

### 9.5 Final Scientific Claim

Control:

> H6/H6a are tiny improvements. The fixed contract still likely lacks variables needed for decisive repair.

Reframe:

> The mechanisms expose a Pareto frontier. The fixed contract can infer some broad fire-regime structure, but not enough to eliminate the tradeoff between strong-belt fidelity and humid/monsoon repair.

## 10. Why Control Eventually Became More Sophisticated

It is important not to overstate the reframe advantage.

By pass 3, the control agent did develop a meaningful reinterpretation:

> GPP is both fuel charge and live fuel moisture.

That is a real conceptual move. It is not just a parameter tweak.

This shows that the base prompt plus repeated passes can also produce deeper reasoning, especially when the continuation prompt says not to treat previous passes as endpoints and to test distinct families.

But the route is different:

- Control reached live-fuel/curing after exhausting wet suppressor variants.
- Reframe reached multi-factor interlocks and release windows much earlier.
- Control's final H6 mechanism still lives in the suppressor family.
- Reframe's final mechanism set includes suppressors, release terms, guards, corridors, edge mixtures, and Pareto sweeps.

Therefore:

> The reframe prompt did not unlock exclusive capabilities. It changed what the agent searched first and how it transformed failures.

## 11. Best Paper Interpretation

A strong paper claim would be too much:

> "The reframe prompt causes a step-function improvement in autoresearch reasoning."

The evidence does not support that.

A weak paper claim would miss the signal:

> "The reframe prompt just made the agent do the same thing slightly better."

The logs do not support that either.

The defensible claim is:

> "A small structural-reframing addendum changed the agent's reasoning pathway by altering its hypothesis-generation prior. Compared with the control, the reframed agent earlier and more explicitly used cross-domain structural analogies, converted failure modes into new mechanism classes, and represented the endpoint as a Pareto frontier rather than a single accept/reject result. However, the improvement was not categorical: the control run eventually developed a subtler live-fuel/curing mechanism through ordinary iterative failure analysis, and both runs converged on the same fixed-input limitation."

## 12. What This Means For The Original Paper Plan

The original paper plan asked whether prompt-based zooming-out can help agents recover from directional uncertainty.

Experiment 03 suggests:

1. Prompt-based structural reframing can change the research trajectory.
2. The change can be visible in logs, not just scores.
3. The best evidence is the sequence of mechanisms, not the final metric.
4. The reframe prompt's effect is mostly on hypothesis generation and failure interpretation.
5. The effect is not strong enough to claim a new autonomous scientific reasoning regime.
6. The control can partially catch up over multiple passes if its continuation prompt forces broader search.
7. The next experimental design should evaluate reasoning trajectories directly, not only final candidates.

For the paper, the useful result is not:

> "Reframe beat control by X."

The useful result is:

> "The reframe prompt changed how the agent searched. It induced structural analogy use and mechanism-class mutation, while the control mostly refined local suppressor families before eventually finding one state-based correction. This supports the idea that zoom-out interventions can shift autoresearch trajectories, even when the final quantitative improvements are modest."

## 13. Suggested Coding For Trajectory Analysis

If converting this into paper evidence, code each pass along these dimensions:

### Frame Type

- Suppression repair
- Conditional suppression
- Conditional release
- Guard/protection
- Corridor/balance
- Handoff/phase transition
- Edge/mosaic regime
- Pareto frontier interpretation

### Failure Interpretation

- Candidate failed because parameter values are wrong
- Candidate failed because mechanism is too broad
- Candidate failed because allowed inputs cannot separate regimes
- Candidate failed but suggests a new structural mechanism
- Candidate reveals a tradeoff surface

### Next-Hypothesis Derivation

- Direct variant of previous mechanism
- Milder/stronger ablation
- Added gate to previous mechanism
- New physical interpretation of same variable
- Cross-domain structural analogy
- Combination of prior mechanisms
- Pareto/sweep analysis

### Evidence Role

- Candidate as final solution
- Candidate as rejected dead end
- Candidate as diagnostic evidence
- Candidate as family seed
- Candidate as Pareto endpoint

Using that coding, the expected pattern is:

- Control: mostly suppression repair -> conditional suppression -> new physical interpretation of same variable.
- Reframe: structural analogy -> conditional release -> guard/corridor/handoff -> edge/mosaic -> Pareto frontier.

## 14. Bottom Line

The third-order reframe mechanisms did not come "just" from the paragraph in the sense of the paragraph specifying them. The paragraph did not contain the mechanisms.

But the mechanisms did come from the paragraph in the more important experimental sense:

- the paragraph was the only prompt delta,
- the agent explicitly adopted structural analogy as a method,
- the generated mechanism families correspond to named structural analogies,
- and the reframe pathway differs systematically from the control pathway.

So the right answer is:

> The paragraph did not hand the agent the answer. It changed the agent's hypothesis-generation policy. That policy shift is visible in the logs: the reframe agent repeatedly turned failures into new structural analogies and mechanism classes, while the control agent mostly refined suppressive local repairs until pass 3. The result is a reasoning-pathway difference, not a proven step-function reasoning upgrade.

