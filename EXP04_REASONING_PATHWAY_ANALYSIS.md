# Experiment 04 Reasoning Pathway Analysis

Date: 2026-05-22

Scope: Hermes Agent clean Experiment 04 runs on the ED Model C fire benchmark, comparing the matched non-reframe/control prompt against the structural-reframe prompt for one autoresearch pass.

Focus: this document evaluates reasoning traces, not final scores. Scores are used only as evidence for what the agents noticed, what they treated as failure, what they promoted or rejected, and why they stopped.

Primary evidence: unlike earlier experiments, the paired exp 04 control and reframe runs both include `decision_trace.md`. This makes exp 04 especially useful for comparing the externalized decision pathway.

## 1. Executive Conclusion

Exp 04 gives a clean but shallow paired comparison.

The reframe prompt did change the agent's reasoning style. The reframe agent explicitly framed the problem through structural analogies:

- Model C as a series circuit of necessary climatic gates;
- missing weak-region behavior as a continuity/firebreak/fuse problem;
- GPP response as a pharmacological dose-response with high-dose inhibition;
- accumulated dryness as queue/backlog state changing the effect of new rainfall.

The control agent did not reason in that language. It framed the first search wave as a physically interpretable mechanism sweep:

- precipitation-shape elasticity;
- high-temperature suppression;
- humid suppression;
- fuel-moisture balance;
- base refit.

So the answer to the central reasoning question is:

> Yes, the reframe prompt appears to have induced structurally different external reasoning. It did not merely add decorative analogical prose; the analogies directly named the mechanism families and appear in the decision trace as the reason for choosing the next hypothesis.

But the effect is limited.

Both agents stopped prematurely after one broad/shallow wave. Neither run pushed into deeper second-order mechanism composition, despite the prompt asking for repeated outer loops until the empirical ceiling was reached. Both runs concluded that original Model C remained final. Both saw the same basic failure frontier:

> Weak-region repairs are possible, but under the fixed input contract those repairs suppress or distort globally important boreal/savanna/spatial behavior.

Therefore exp 04 supports the weaker thesis:

> The structural reframe prompt changes the form of hypothesis generation and decision explanation.

It does not support the stronger thesis:

> The reframe prompt reliably makes the agent conduct deeper or more persistent autoresearch.

In fact, exp 04 is useful because it separates two dimensions:

1. **Reasoning style:** reframe clearly differs.
2. **Research persistence:** reframe did not improve; both were premature.

My best formulation:

> Exp 04 is a clean reasoning-style win but an autoresearch-depth failure. The reframe agent used structural analogies as intended, but still terminated after one loop. It transformed local mechanism labels into structural lenses, yet did not convert that framing into a deeper multi-pass exploration.

## 2. Artifact Map

There are several exp 04-related folders. The canonical paired comparison for this document is:

Control:

- Workspace: `exp-workspaces/exp_04-control/hermes/control`
- Record: `reframe-exps/experiments/exp_04_control/harnesses/hermes/control_run/pass_1_modelc_tradeoff_premature_stop`
- Archive: `_archive/2026-05-22__ed_fire_exp04_control_pass1_modelc_tradeoff_premature_stop`
- Primary trace: `reframe-exps/experiments/exp_04_control/harnesses/hermes/control_run/pass_1_modelc_tradeoff_premature_stop/logs/decision_trace.md`

Reframe:

- Workspace: `exp-workspaces/exp_04-reframe/hermes/reframe`
- Record: `reframe-exps/experiments/exp_04_reframe/harnesses/hermes/pass_1_clean_reframe_premature_stop`
- Archive: `_archive/2026-05-22__ed_fire_exp04_reframe_pass1_clean_premature_stop`
- Primary trace: `reframe-exps/experiments/exp_04_reframe/harnesses/hermes/pass_1_clean_reframe_premature_stop/logs/decision_trace.md`

There is also an earlier exp 04 base/control record:

- `reframe-exps/experiments/exp_04/harnesses/hermes/base_run/pass_1_rain_ignition_control`
- Archive: `_archive/2026-05-22__ed_fire_exp04_base_pass1_rain_ignition_control`

That earlier run is not the main paired comparison because the clean control/reframe rerun lives under `exp_04_control` and `exp_04_reframe`, and both of those contain `decision_trace.md`. I use the earlier base run only as context showing another control-like direction, not as the main comparison.

## 3. Prompt Difference

The control and reframe prompts are essentially matched.

The substantive difference is the structural reframe paragraph:

```text
Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example of this would be, to solve the neonatal handover problem for newborns, doctors drew inspiration from F1 pit crews and how that analogy can transfer to the ER. The F1 pitstop is highly efficient as the pit crew had 7 seconds to refuel and change the tyres. The surgeons translated it to the ER to specify where everyone should be positioned and how to operate, bringing down errors and the duration of handover. Both problems share the same structure of team organization and efficiency. Zoom out and look for such parallels structurally for this specific problem scenario. You need to do this at each sub-level of whatever hypothesis/approach you are taking.
```

Other differences are formatting and a small final-proceeding difference:

- control prompt ends with `Before, proceeding read necessary files...`
- reframe prompt ends with `Before proceeding... If you have no blocking questions, continue immediately into baseline verification and the first research loop.`

The "continue immediately" clause may affect whether the agent waits for confirmation, but it does not provide a specific mechanism. The specific structural reasoning intervention remains the analogy paragraph.

## 4. Shared Experimental Setup

Both runs were clean isolated original-Model-C runs.

Both used:

- original Model C as the starting point;
- one global mechanistic formula requirement;
- fixed allowed inputs only:
  - dbar;
  - annual precipitation;
  - monthly precipitation;
  - monthly air temperature;
  - monthly GPP;
  - existing reference/evaluation files;
- no external model inputs;
- no latitude/longitude hacks;
- no named-region routing;
- no per-cell lookup tables;
- no arbitrary residual correction coefficients;
- official global ILAMB;
- official regional ILAMB;
- public clean TRENDY/firepipe when serious;
- required logs including `decision_trace.md`.

Both runs reproduced original Model C first.

Both observed the same baseline pattern:

- Model C is globally strong.
- Seasonal timing is often already good.
- Weak regions are mostly weak in spatial distribution and/or magnitude.
- The recurring weak regions include:
  - Europe;
  - Central America;
  - Middle East;
  - Temperate North America;
  - Equatorial Asia;
  - Southeast Asia;
  - Southern Hemisphere South America.
- Strong regions include boreal systems and African/savanna systems.
- Any candidate must avoid damaging those strong regions.

This matters because the two agents did not start from different facts. The difference is how they transformed those facts into the first mechanism search.

## 5. Control Run Reasoning Pathway

The control run is recorded as:

`pass_1_modelc_tradeoff_premature_stop`

Its README already labels it:

> Clean run, but shallow. The agent followed isolation constraints and ran official evaluations, but stopped after one broad outer-loop search rather than continuing into a deeper multi-loop control process.

That label is accurate.

The control decision trace has five decisions:

- D0 baseline-first protocol;
- D1 mechanism family selection for first search wave;
- D2 official global/regional candidate evaluation;
- D3 ablation diagnostics;
- D4 public benchmark and stopping decision.

### 5.1 Control D0: Baseline-First Protocol

Control D0 is procedural.

Observed clue:

- Workspace instructions require baseline verification and evaluation before modifications.

Decision:

- Establish locally reproduced original Model C as baseline.

Reasoning:

- README scores are not enough.
- Local reproduction is required for defensible comparison.

This is sound but not creatively meaningful. It establishes discipline.

### 5.2 Control D1: First Search Wave Selection

This is the central reasoning step for the control run.

Control observed:

- baseline has excellent global seasonal behavior;
- weak regional component scores occur in low/fire-complex regions;
- key weak regions have poor spatial distribution and bias/RMSE.

Control hypothesis:

> Missing global mechanisms likely involve precipitation-shape/fuel-moisture balance, heat-window suppression, humid-region suppression, or refit tradeoffs rather than black-box regional correction.

Mechanism families selected:

1. `base_refit`
   - same Model C formula;
   - asks whether the failure is just parameter slack.

2. `precip_shape`
   - adds exponents to annual precipitation floor and monthly rainfall dampening;
   - asks whether precipitation response elasticity is too rigid.

3. `temp_window`
   - adds high-temperature suppression;
   - asks whether very hot conditions imply fuel-limited/stress regimes.

4. `humid_suppression`
   - adds annual precipitation humid/fuel-moisture suppressor;
   - asks whether persistent humid systems are too wet despite existing dampening.

5. `fuel_moisture_balance`
   - adds dryness relief of monthly rainfall dampening;
   - asks whether the same rain amount should suppress less in accumulated dry cells.

Reasoning style:

The control run is physically plausible and mechanistic, but it is mostly a category sweep over direct process terms. It does not explicitly search for far structural analogies. It does not write "this is a circuit", "this is a fuse", "this is a dose-response", or "this is a backlog system." It says: these are likely missing global mechanisms and they use allowed inputs.

The choice is rational:

- no forbidden region/cell routing;
- no external landcover/cropland data;
- one global formula;
- cell-state-dependent behavior allowed.

But it is broad and flat. It launches five families in one wave rather than using each failure to change the next hypothesis class.

### 5.3 Control D2: Official Evaluation

Control D2 tests whether one of the broad smooth gates improves enough regional behavior to justify replacement.

Result:

- No candidate beats Model C global Overall.
- Closest global candidate is `temp_window`, but it is still far below baseline.
- Regional derived means improve for candidates like `precip_shape` and `fuel_moisture_balance`.
- The improvements come with global spatial/seasonal losses.

Decision:

- reject all new candidates as final;
- retain original Model C;
- record regional candidates as diagnostic alternatives.

This is strong scientific judgment. The agent does not accept a regional-improving but globally degraded model.

### 5.4 Control D3: Ablation Diagnostics

Control D3 asks a good question:

> Are the added terms genuinely useful, or are improvements mostly refit/regional-objective tradeoffs?

The ablation approach:

- neutralize added mechanism terms while keeping refit parameters;
- inspect proxy ablation effects.

Result:

- added terms are not consistently decisive;
- some improve proxy global spatial while degrading regional mean/min;
- precipitation exponents have tiny proxy effect;
- improvements do not look like a clean robust new mechanism.

Decision:

- demote added mechanisms to diagnostic insights.

Reasoning implication:

> The regional gains mostly reflect a tradeoff frontier exposed by refitting and regional weighting, not a clean mechanism that should replace Model C.

This is a good local-scientific conclusion.

### 5.5 Control D4: Public Benchmark And Stop

Control D4 runs public clean benchmark for the reproduced final Model C, then stops.

Decision:

- stop exploration at original Model C;
- no tested unified interpretable extension produced a step-function delta;
- remaining failures likely require unavailable or forbidden inputs.

This stopping decision is scientifically defensible given the tested candidates, but shallow relative to the prompt.

The prompt asked:

> Keep pushing across distinct mechanistic families until the empirical ceiling appears reached under the fixed constraints.

The control run tested five first-wave families, then stopped. It did not ask:

- If broad gates are too blunt, can conditional gates separate regimes?
- If regional gains appear but global spatial collapses, can a second-order limiter protect strong regions?
- If precip-shape helps some regions and fuel-moisture helps worst regions, can a structured hybrid be tested?
- If the failure is identifiability, can multiple candidate roles be preserved as Pareto alternatives?

So the control reasoning is competent but prematurely terminal.

## 6. Reframe Run Reasoning Pathway

The reframe run is recorded as:

`pass_1_clean_reframe_premature_stop`

Its README says:

> Status: not counted as a successful reframe pass. The run stayed within the clean experiment boundary, but stopped prematurely after one outer research loop. It tested simple wetness, productivity, and curing mechanism families, then wrote `final_report.md` without continuing into deeper second-order combinations.

That is also accurate.

The reframe decision trace has four decisions:

- D0 baseline first, no formula changes before reproduction;
- D1 wetness/firebreak fuse;
- D2 asymmetric GPP dose-response;
- D3 dbar-buffered monthly curing.

### 6.1 Reframe D0: Baseline With Structural Failure Interpretation

Reframe D0 begins procedurally like control:

- read setup files;
- verify;
- reproduce Model C;
- run official global/regional ILAMB.

But the implication for the next loop is materially different from control.

Reframe writes:

> Look for one global, input-derived mechanism that suppresses or reshapes fire in weak humid/fragmented/agricultural/low-continuity regimes without degrading savanna Africa and boreal strengths.

Then it adds the structural analogy:

> current Model C is a simple series circuit of necessary gates; failures suggest the circuit lacks a "continuity/containment fuse" that trips in regions where climate/productivity can support fire but landscape/fuel continuity inferred from climate/productivity does not support large burned area.

This is the first clear reframe effect.

Control D0 says:

> Explore mechanisms that can repair regional spatial/bias behavior without sacrificing Model C's strong global seasonal score.

Reframe D0 says:

> Model C is a series circuit; weak-region failures suggest a missing continuity/containment fuse.

The difference is not merely wording. It changes the first candidate family:

- control begins with a five-family process sweep;
- reframe begins with a "firebreak/fuse" mechanism.

### 6.2 Reframe D1: Wetness / Firebreak Fuse

Observed failure:

- weak spatial/magnitude components in Europe, Central America, Middle East, Temperate North America, Equatorial Asia, Southeast Asia, SH South America;
- seasonal timing is often good.

Hypothesis:

> Model C lacks a global high-wetness/fuel-continuity suppressor.

Structural analogy:

> a circuit can have all upstream gates open but still be stopped by a fuse; humid/productive/fragmented regimes may need a spread-continuity fuse inferred from annual precipitation.

Mechanism:

```text
Model C * annual high-wetness suppressor
```

This is similar in surface form to control's `humid_suppression`, but the reasoning route differs:

- control: persistent humid systems may remain too wet;
- reframe: climate gates may all be open, but spread is stopped by a missing continuity fuse/firebreak.

The reframe mechanism name, `wet_firebreak`, also reflects the analogy. It is not just `humid_suppression`.

Result:

- weak-region means improve;
- official global Spatial collapses;
- Overall collapses.

Decision:

- reject because annual precipitation alone makes the fuse too blunt.

Implication:

> Need a mechanism that distinguishes humid low-fire regions from high-fire productive savannas without suppressing boreal/savanna spatial structure.

This is a good reframe-style inference. It turns failure into an identifiability problem:

> The firebreak idea is plausible, but the available proxy cannot separate target regimes cleanly.

### 6.3 Reframe D2: Asymmetric GPP Dose-Response

Observed failure:

- wet firebreak over-suppressed spatial structure;
- annual precipitation alone is too blunt;
- GPP might encode fuel amount and humid closure more directly.

Hypothesis:

> Replace Model C's GPP hump with separately tunable low-fuel onset and high-productivity closure.

Structural analogy:

> pharmacological dose-response with toxicity at high dose.

Mechanistic mapping:

- low GPP -> insufficient fuel;
- intermediate GPP -> flammable fuel;
- high GPP -> humid closure/wet productive systems that may suppress spread;
- high dose toxicity -> too much productivity/wetness changes the limiting process.

This is one of the clearest signs that the reframe prompt was taken up. The analogy is not a decorative aside. It determines the formula family:

- separate low-fuel onset;
- separate high-productivity closure;
- replace original GPP hump.

Result:

- RMSE improves;
- seasonal stays high;
- spatial distribution falls too much;
- regional weak regions improve but not cleanly.

Decision:

- reject/demote;
- GPP-only closure cannot separate weak humid regions from productive fire regimes under this input contract.

Implication:

> Try seasonal curing/precipitation timing rather than static annual/productivity suppression.

This is a sequential reasoning move. The agent does not merely run all families at once. It uses D1 failure to choose D2, then D2 failure to choose D3.

### 6.4 Reframe D3: Dbar-Buffered Monthly Curing

Observed failure:

- Australia seasonal weakness;
- weak-region magnitude failures;
- monthly precipitation dampening may be too absolute;
- the same wet month should behave differently after accumulated drying than in persistently wet state.

Hypothesis:

```text
effective_rain = P_month / (1 + Dbar / buffer)^q
```

Structural analogy:

> queue/bottleneck system where backlog changes the effect of new arrivals; accumulated deficit changes the extinguishing power of rainfall.

Mechanistic mapping:

- backlog -> accumulated dry deficit (`Dbar`);
- new arrivals -> monthly precipitation;
- bottleneck state -> whether rain suppresses fire strongly or weakly;
- deeply cured landscape -> rain has different effect than in a wet landscape.

This is also an explicit structural transfer. The analogy is not far-domain in the F1/neonatal sense, but it does reframe the monthly precipitation term as state-dependent system dynamics.

Two searches:

- C3 regional objective;
- C4 global objective.

Result:

- C3 improves weak regions but catastrophically collapses global Spatial;
- C4 is the best non-baseline global tradeoff:
  - Bias and Spatial improve;
  - RMSE and Seasonal decline;
  - Overall remains below C0;
  - public score remains below C0;
  - dry-buffer exponent is close to neutral, suggesting the mechanism has little robust global leverage when protected by global objective.

Decision:

- reject C3;
- demote C4;
- keep original Model C.

Implication:

> Simple global wetness/productivity/curing additions cannot resolve the fixed-input failure; remaining failures likely require missing landcover/cropland/human/fuel-structure information or a more expressive mechanism not found.

### 6.5 Reframe Stopping Decision

The final report says:

> The constrained exploration reached a defensible stopping point.

But the run itself is marked premature by the experiment README.

Why premature:

- only one substantive outer loop;
- only three mechanism families;
- no deeper second-order combinations;
- no exploration of protected hybrid variants;
- no attempt to transform the C1-C3 failures into new conditional mechanisms beyond C4;
- no Pareto role preservation beyond basic diagnostic labels.

This is important because the reframe prompt did not prevent the agent from stopping early. It improved the first-loop reasoning language and family selection, but not the persistence discipline.

## 7. Direct Pathway Comparison

### 7.1 Initial Problem Representation

Control:

> Baseline has excellent global seasonal behavior but weak spatial/bias/RMSE in low/fire-complex regions. Try interpretable allowed-input physical gates.

Reframe:

> Model C is a series circuit of climatic gates. Weak regions may need a missing continuity/containment fuse because climate/productivity can look permissive while spread continuity fails.

Interpretation:

The control representation is process-variable oriented. The reframe representation is system-structure oriented.

### 7.2 First Mechanism Selection

Control:

- runs broad first-wave sweep:
  - base refit;
  - precipitation shape;
  - temperature window;
  - humid suppression;
  - fuel moisture balance.

Reframe:

- starts with wet firebreak/fuel-continuity fuse.

Interpretation:

Control asks:

> Which allowed physical factors might improve the weak regions?

Reframe asks:

> What missing system constraint could prevent spread even when existing gates say fire is possible?

That is a real reasoning-pathway difference.

### 7.3 Use Of Failure

Control:

- evaluates all candidates;
- sees global/regional tradeoff;
- runs ablations;
- stops.

Reframe:

- D1 failure says annual precipitation is too blunt;
- D2 shifts to GPP asymmetry to seek a better proxy for fuel amount/closure;
- D2 failure says static annual/productivity suppression is insufficient;
- D3 shifts to timing/curing via dbar-buffered monthly precipitation.

Interpretation:

The reframe run shows more sequential hypothesis updating inside the one loop. The control run shows stronger broad sweep plus evaluation discipline, but less explicit failure-to-next-hypothesis transformation.

### 7.4 Breadth

Control tested five families and 2500 trials:

- broader first wave;
- includes base refit and temperature window;
- official global/regional for all;
- proxy ablations.

Reframe tested three families plus a global-objective rerun of the third, 2200 trials:

- narrower first wave;
- more structurally named;
- official global/regional for all;
- public for C4.

Interpretation:

Reframe is not simply "more exploration." In exp 04, control is actually broader in count and family variety. Reframe is more structured in how it names and sequences the search.

### 7.5 Mechanism Overlap

There is substantial overlap under different names:

| Control | Reframe | Relationship |
|---|---|---|
| `humid_suppression` | `wet_firebreak` | Similar high-wetness suppression; reframe frames it as continuity/fuse/firebreak. |
| `fuel_moisture_balance` | `curing_ratio` | Similar idea that monthly rainfall effect depends on dryness/accumulated state. |
| `precip_shape` | partly `curing_ratio` / wetness terms | Both reshape precipitation effects. |
| `temp_window` | no direct reframe equivalent | Control uniquely tried high-temperature suppression. |
| `base_refit` | no direct reframe equivalent | Control uniquely tested parameter-only slack. |
| no direct equivalent | `gpp_asym` | Reframe uniquely emphasized high-productivity closure/dose response. |

Interpretation:

The reframe prompt did not cause a completely different universe of mechanisms. It changed how overlapping mechanism space was conceptualized and sequenced.

This matters for the thesis:

> Reframe changed the hypothesis-generation prior and explanation topology, but it did not necessarily give access to mechanisms the control could not reach.

### 7.6 Stopping Behavior

Both stopped too early.

Control stopped after:

- one broad five-family wave;
- official evaluation;
- ablations;
- public baseline benchmark.

Reframe stopped after:

- one structural loop with three families;
- official evaluation;
- public C4/C0 comparison.

Neither fully honored the instruction:

> Keep pushing across distinct mechanistic families until the empirical ceiling appears reached.

This is the biggest negative finding in exp 04.

If the goal is to prove that reframe improves autoresearch persistence, exp 04 does not help. If anything, it shows that even a reframe prompt with a decision trace can still stop prematurely.

## 8. Did The Reframe Prompt Cause Structurally Different Reasoning?

Yes, with caveats.

Evidence for "yes":

1. The reframe decision trace explicitly uses structural analogies in each major hypothesis:
   - series circuit / continuity fuse;
   - firebreak;
   - pharmacological dose-response;
   - queue/bottleneck backlog.

2. The reframe mechanism names encode the structural lenses:
   - `wet_firebreak`;
   - `gpp_asym`;
   - `curing_ratio`.

3. The reframe agent uses failure to move between structures:
   - wet firebreak too blunt;
   - try GPP dose-response;
   - static closure insufficient;
   - try timing/curing.

4. The reframe final report has an entire section:
   - `Mechanisms tried and structural analogies`.

5. The control run lacks comparable structural analogy language and instead describes direct physical mechanism categories.

Caveats:

1. Reframe analogies are not all far analogies.
   - Circuit/fuse and queue/bottleneck are structural but relatively generic.
   - Pharmacological dose-response is a stronger cross-domain analogy.
   - They are not as remote or operationally rich as F1/neonatal.

2. The mechanisms are not radically different from control.
   - Wet firebreak overlaps with humid suppression.
   - Curing ratio overlaps with fuel-moisture balance.
   - The difference is framing and sequence more than entirely new mechanism space.

3. Reframe did not improve persistence.
   - It stopped after one outer loop.
   - It did not explore deeper combinations or guarded second-order variants.

4. The run is marked premature.
   - The experiment record itself says not counted as a successful reframe pass.

Bottom line:

> Exp 04 confirms that the reframe paragraph changes the way the agent externalizes and organizes hypotheses. It does not confirm that this changed organization is sufficient to produce deeper autoresearch or better final decisions.

## 9. What The Decision Traces Reveal

The decision traces are useful because they expose reasoning behind the next-step choice.

### Control Decision Trace Pattern

Control trace shape:

```text
baseline -> broad mechanism family sweep -> official evaluation -> ablation -> stop
```

The reasoning is:

- identify weak regions;
- choose plausible physical families;
- run them;
- reject due global/regional tradeoff;
- ablate to see if added terms matter;
- stop because remaining failures need unavailable inputs.

This is disciplined, but coarse.

### Reframe Decision Trace Pattern

Reframe trace shape:

```text
baseline + structural circuit/fuse interpretation
  -> wet firebreak
  -> GPP dose-response
  -> dbar-buffered curing / queue backlog
  -> stop
```

The reasoning is:

- identify weak regions;
- convert failure into missing continuity fuse;
- first proxy too blunt;
- find alternate proxy in GPP dose-response;
- static proxy still too blunt;
- shift to state-dependent timing/curing;
- stop because simple additions do not resolve identifiability.

This is more sequential and structurally narrated, but still shallow.

### What This Means

The reframe prompt made the decision trace more interpretable as a research path. It is easier to see why one hypothesis followed another.

However, decision trace quality alone is not enough. The agent still needs an instruction or tool mechanism that prevents premature stopping after first-loop failure.

For future experiments, the decision trace requirement should maybe include:

```text
Before stopping, list at least three second-order continuations implied by the failed candidates and explain why each was tested or why it is impossible under constraints.
```

Exp 04 reframe would likely have failed that requirement, because it did not deeply pursue second-order continuations after C1-C3.

## 10. Relation To Exp 01, Exp 02, And Exp 03

Exp 01:

- contaminated;
- reframe showed structural reasoning;
- not causally clean.

Exp 02:

- contaminated high-ceiling path;
- clean reframe did not reproduce high ceiling;
- high score likely leakage-assisted.

Exp 03:

- cleaner and more complete three-pass comparison;
- reframe followed a structural mechanism-composition pathway;
- control followed local repair then later more nuanced suppressor/state reasoning;
- best evidence that reframe changes search prior.

Exp 04:

- clean prompt comparison;
- one pass only;
- explicit decision traces;
- both premature;
- reframe shows structural reasoning style but not deeper research persistence.

So exp 04 strengthens one claim and weakens another.

Strengthened claim:

> The reframe paragraph changes the visible reasoning pathway. The agent writes and uses structural analogies in decision-making.

Weakened claim:

> Reframing alone ensures better autoresearch depth.

Exp 04 shows it does not.

## 11. Implications For The Reframe CLI

Exp 04 is relevant to the CLI design discussion.

A static reframe paragraph can induce structural analogy language. But structural language is not enough.

The reframe CLI should not only ask for analogies. It should also force:

- second-order continuation after a failed analogy;
- cheap tests before full commitment;
- explicit rejection criteria;
- portfolio maintenance;
- "before stopping" checks;
- conversion of failed lenses into new candidate families.

For example, a better reframe addendum for exp 04 would have said:

```text
If a structural lens fails because it is too blunt, do not stop. Ask what condition, guard, or second signal would make the lens selective enough. Test at least one guarded or second-order variant before declaring that mechanism family exhausted.
```

This matters because exp 04 reframe did the first part:

- found structural lenses;
- tested them;
- rejected them.

But it did not do the second part:

- transform failed lenses into deeper variants.

For a CLI, that suggests the output should not merely contain:

```text
Think structurally.
```

It should contain:

```text
When a structural analogy fails, diagnose why it failed: too broad, wrong proxy, wrong timing, wrong scale, missing guard, missing interaction, or objective mismatch. Then test one cheap corrected version before abandoning the family.
```

## 12. Paper Framing

The cleanest way to use exp 04 in the paper:

> Experiment 04 added explicit decision traces to a clean one-pass control/reframe comparison. The reframe run externalized more structural reasoning than the control run: it framed Model C as a circuit of gates, weak-region failures as missing firebreak/fuse mechanisms, productivity response as a dose-response curve, and rainfall dampening as a queue/backlog problem. These analogies directly generated the candidate families. However, both runs stopped prematurely after one broad loop, and neither found a replacement for Model C. Thus exp 04 supports the claim that reframing changes hypothesis framing and decision-trace content, but not the stronger claim that a single reframe prompt ensures deeper or more successful autoresearch.

Avoid saying:

> Exp 04 proves the reframe prompt improves model discovery.

Better:

> Exp 04 shows a clean shift in reasoning trace without a clean improvement in research depth or final outcome.

Even better:

> Reframing changed the agent's hypothesis language and mechanism-selection rationale, but additional process constraints may be needed to convert structural insight into sustained exploration.

## 13. Bottom Line

Control exp 04:

- clean;
- broad first-wave mechanism sweep;
- physically plausible local/global terms;
- good evaluation and ablation discipline;
- premature stop;
- no structural analogy uptake.

Reframe exp 04:

- clean;
- explicit structural analogies;
- more sequential failure-to-next-hypothesis reasoning;
- fewer families than control;
- premature stop;
- no accepted replacement;
- no proof of deeper autoresearch.

Final assessment:

> Exp 04 is a clean positive result for reasoning-style change and a clean negative result for one-pass reframe sufficiency. The reframe prompt made the agent think and write in structurally different terms, but did not make it persist into the deeper mechanism-composition search that the prompt requested.

