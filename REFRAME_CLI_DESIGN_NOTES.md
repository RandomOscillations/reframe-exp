# Reframe CLI Trial: Design Notes And Open Questions

Date: 2026-05-22

Context: these notes consolidate the discussion about building a CLI that reframes prompts for agents/autoresearch systems, motivated by the ED fire Model C experiments and the structural-reframe addendum.

The central question:

Can we build a project-agnostic CLI that takes an existing prompt and rewrites or appends a reframe layer that nudges an agent toward better structural reasoning, more useful cross-domain analogies, and less blind local search?

The current answer:

Yes, but the tool should not claim to magically discover perfect analogies. It should produce a tailored structural reframe scaffold that changes how the downstream agent searches. The agent still has to do the domain work after reading the project/code/logs.

## Why We Are Considering This

The original experiments were about whether adding a structural reframe prompt changes the reasoning pathway of autoresearch agents.

The extra reframe paragraph was roughly:

> Draw parallels and look at other fields for inspiration. Explore the structure of the problem and solution and see where you can draw inspiration to find the best match. An example of this would be, to solve the neonatal handover problem for newborns, doctors drew inspiration from F1 pit crews and how that analogy can transfer to the ER. The F1 pitstop is highly efficient as the pit crew had 7 seconds to refuel and change the tyres. The surgeons translated it to the ER to specify where everyone should be positioned and how to operate, bringing down errors and the duration of handover. Both problems share the same structure of team organization and efficiency. Zoom out and look for such parallels structurally for this specific problem scenario. You need to do this at each sub-level of whatever hypothesis/approach you are taking.

The key empirical observation from the experiments:

- The reframe prompt did not necessarily create a clean step-function improvement in model score.
- But it did seem to change the agent's search style.
- The agent became more likely to use structural analogies, system-level mechanism families, regime gates, limiters, timing/readiness terms, and broader failure interpretations.
- In contaminated experiments, apparent large gains could not be attributed cleanly to the reframe prompt because the reframe agent could see prior/control artifacts.
- In the cleaner experiment, the reframe prompt appeared more like a search-prior intervention than a new reasoning capability.

So the practical product thesis became:

> A reframe CLI should not "make LLMs creative." It should inject a structural search protocol into prompts so agents are less likely to continue the same local search blindly.

## The Hard Problem

The F1/neonatal example is powerful because it is a far analogy.

Surface domains:

- Formula 1 pit crews.
- Neonatal handover in emergency medicine.

Surface similarity is weak. The domains look unrelated.

Structural similarity is strong:

- time pressure;
- role choreography;
- high consequence of delay/error;
- constrained physical workspace;
- handoff minimization;
- preassigned positions;
- repeatable sequence;
- standardized communication.

The concern is that LLMs often do not find such far analogies unaided. Without web search or user-provided examples, they tend to produce obvious analogies:

- immune system -> cybersecurity;
- epidemiology -> information spread;
- firebreaks -> software containment;
- portfolio theory -> hypothesis search;
- apprenticeship -> model training.

Some of these are useful, but many are semantically adjacent or already common metaphor clusters in model pretraining. They are easier to generate because the tokens are already associated.

By contrast, when web search was allowed, the examples retrieved were more historically grounded and often stronger as far-domain transfers:

- aviation checklists -> surgical safety checklists;
- aviation crew resource management -> operating room teamwork;
- Toyota Production System -> hospital operations;
- wildland fire incident command -> hospital emergency incident command;
- high-reliability organizations -> ICU/hospital safety;
- F1 pit crew -> neonatal handover.

This implies:

> LLMs are often better at explaining and elaborating a far analogy after it is retrieved or supplied than at independently discovering it from a thin prompt.

That has direct consequences for CLI design.

## What The CLI Should Not Be

The CLI should not be an "analogy oracle."

Bad framing:

> Give the model the perfect analogy and tell it the best mechanism.

Why this is not viable:

- It requires deep project understanding.
- The prompt alone often does not contain enough information.
- It risks steering research into bad directions.
- It makes the CLI brittle and non-project-agnostic.
- It overclaims what an LLM backend can reliably do.

The CLI should also not be a static paragraph generator.

Bad framing:

> Always append the same structural reframe paragraph to every prompt.

Why this is weak:

- Users could just paste that paragraph manually.
- It does not justify a tool.
- It does not adapt to task type.
- It cannot supply tailored analogical lenses.

The CLI should not depend on a large manually curated analogy library either.

Bad framing:

> Build a huge internal library of analogies and retrieve from it.

Why this is currently unrealistic:

- The library would never be complete.
- Populating it requires resources we do not currently have.
- If the domain library is poor, the product fails.
- A project-agnostic tool cannot require hand-curated coverage of every field.

## What The CLI Should Be

The CLI should be a contextual prompt reframer.

It should:

1. Preserve the original prompt.
2. Infer the rough structure of the task from the prompt.
3. Generate a small number of tailored structural lenses.
4. Add those lenses as hypothesis generators, not as directives.
5. Require the downstream agent to validate, test, and reject aggressively.

The core product should be:

> A prompt transformation tool that nudges agents toward structural search while preserving the original objective and constraints.

It should not claim:

> We discover the perfect analogy for your project.

It can claim:

> We add a tailored structural reframing layer that encourages agents to generate, test, and reject cross-domain mechanism hypotheses instead of only continuing local search.

## Who Should Think Of The Analogy?

The answer is: both, but at different layers.

### Human

The human may supply a known high-quality analogy, like F1/neonatal. If available, this is valuable.

But the product cannot require this. If the human has to deeply understand the codebase/project and invent a perfect analogy before using the tool, the CLI fails as a general tool.

### CLI / LLM Backend

The CLI should infer possible structural lenses from the prompt.

For example, in the ED fire prompt, a backend can infer:

- fire spread;
- regional behavior;
- one global formula;
- fixed input contract;
- local benchmark already strong;
- need for mechanistic, interpretable improvement;
- avoid region routing;
- failure likely in regimes.

That is enough to propose high-level structural lenses:

- percolation / epidemic spread;
- combustion or chemical reaction windows;
- seasonal harvest readiness / stock-flow;
- control systems with guardrails.

But the CLI should not decide the final mechanism.

### Downstream Agent

The downstream autoresearch agent must do the domain-specific mapping after reading:

- `AGENTS.md`;
- `program.md`;
- `WORKSPACE_MANIFEST.md`;
- `BASELINE_REPRO.md`;
- codebase;
- benchmark failures;
- regional analysis;
- logs and prior evaluations.

It should decide which lens is actually useful and which is nonsense.

The CLI can nudge, but the agent has to earn the mechanism.

## Why Fixed Categories Are Dangerous

One proposed design was to classify all problems into categories:

- bottleneck;
- handoff;
- timing;
- gating;
- local optimum;
- hidden state;
- missing limiter;
- regime mixture;
- stock-flow;
- feedback loop;
- allocation under uncertainty;
- spread/containment.

This is useful as an internal nudge, but dangerous as a rigid taxonomy.

Problems:

- Categories will keep expanding.
- A fixed taxonomy can force the wrong frame.
- Agents may overfit to the menu.
- Some important structures will be outside the categories.

Better approach:

Use open-ended structural dimensions, not a closed taxonomy.

For example:

```md
Describe the structure of the problem yourself. Consider dimensions like timing, coordination, bottlenecks, hidden state, feedback, resource allocation, sequencing, constraints, failure propagation, local-vs-global tradeoffs, and regime mixtures. This list is suggestive, not exhaustive.
```

That gives the model a steer without trapping it.

## Why Hard Scoring Is Also Dangerous

Another proposed design was to score candidate analogies.

That is probably bad for the MVP.

Problems:

- Human scoring does not scale.
- LLM-as-judge scoring can be noisy and self-confirming.
- A numeric score creates false precision.
- Some weak-looking analogies may become useful after exploration.
- Some strong-looking analogies may be shallow or harmful.

Better approach:

Use soft guardrails, not scores.

The simplest useful rule:

> An analogy is useful only if it changes what the agent would try next.

If it does not lead to a concrete research direction, mechanism family, diagnostic, experiment, ablation, or evaluation lens, discard it.

This avoids pretending we can objectively score creativity.

## How To Avoid Cooking The Research

The reframe prompt must not make the agent overcommit to the analogy.

Bad instruction:

> Use this analogy to solve the problem.

Better instruction:

> Use this analogy only as a hypothesis generator. Reject it quickly if it does not produce useful evidence.

For autoresearch, every analogy-derived direction should require:

- a concrete mechanism;
- a cheap diagnostic;
- an ablation when feasible;
- a rejection condition;
- evaluation under original acceptance criteria;
- logging in `decision_trace.md`.

The agent should not be allowed to accept analogy-derived work because it sounds clever.

It must still pass:

- official global evaluation;
- official regional evaluation;
- public benchmark if serious;
- mechanism explanation;
- constraint compliance;
- ablation/diagnostic support.

## Search And API Constraints

Search helps discover far analogies.

But depending on live search in the first product version is risky:

- latency;
- cost;
- inconsistency;
- dependency on API/provider support;
- harder reproducibility;
- harder product packaging.

OpenAI/Azure caveat:

- Some modern OpenAI/Azure Responses API setups can use web search tools.
- But support depends on provider, model, deployment, region, and API mode.
- Azure OpenAI via older Chat Completions does not automatically browse.
- If the CLI needs search, the CLI should own search/retrieval explicitly rather than assuming the LLM API has browsing.

For the MVP, the safest route:

- no mandatory web search;
- deterministic/contextual prompt transformation;
- optional search later.

## MVP Design

Command shape:

```bash
reframe prompt.md --mode autoresearch --output prompt.reframed.md
```

Or:

```bash
reframe prompt.md --mode coding
reframe prompt.md --mode science
reframe prompt.md --mode general
```

MVP behavior:

1. Read original prompt.
2. Preserve it unchanged.
3. Generate a tailored addendum.
4. The addendum includes:
   - original-objective preservation;
   - constraint preservation;
   - 3-5 structural lenses tailored to the prompt;
   - instruction to treat lenses as hypotheses;
   - cheap-test/reject discipline;
   - decision logging requirements.

This makes the CLI more useful than a static pasted paragraph because it adapts the reframe lenses to the actual prompt.

## The Static Addendum Problem

If the CLI always emits the same paragraph, there is little point.

A static addendum might still be useful as a baseline experimental treatment, but it is not a compelling product.

Static addendum:

```md
Draw parallels and look at other fields...
```

Better product:

```md
For this task, the strongest structural lenses appear to be:
1. epidemic/percolation spread;
2. combustion reaction windows;
3. harvest readiness / stock-flow;
4. control systems with guardrails.

Use these only as hypothesis generators...
```

That is contextual and project-agnostic at the same time.

## ED Fire Prompt Reframe Example

The user provided the following autoresearch prompt:

```md
Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, and BASELINE_REPRO.md before doing anything else. Do not stop until final_report.md is written.

Start from original Model (C). Your job is to push the model-improvement process to a defensible stopping point. The current model performs well (offline) and ranks #1 on the benchmark. However, there are caveats and improvements which can be made. The scientific goal is not merely to increase one scalar metric. The goal is to find whether a unified, mechanistic, interpretable burned-area functional form can improve global fit and regional fire behavior under the fixed input contract.

First triage where the base model is performing well and where it is not over regions by running the benchmark. Then figure out how to incrementally help improve the per region scores without cheating (see below) one by one by trying out different things while adhering to the pipeline. Do a deep dive.

You are free to alter the functional form along with the hyperparams (by using optuna by using 500-2000 trials at most). Once you believe there is meaningful change, you MUST run the official global and regional ILAMB and use all aspects of the scores to make your judgement.

You are welcome to view this from an angle of different fire types: such as cropland, forest fire, etc. or different region types or any other angle/hybrid you may deem worthy. But you must have one global formula, ie. you may not have seperate sub-region level formulas with some black box type routing mechanism for instance. Inferring region level physics/fire type level physics from cell level data and encoding them all in some global functional form which "acts differently" per "type" is fair game.

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
- decision_trace.md

Maintain `decision_trace.md` as an auditable decision trail. For every major research decision, record: the observed failure or clue, the hypothesis chosen, why that mechanism family was selected next, alternatives considered, the command/evaluation run, the result, the accept/reject/demote decision, and what the result implies for the next loop. This should preserve the external reasoning path behind decisions without inventing certainty or hiding failed directions.

When you believe all possible directions/angles are exhausted note down the set of best models you get: this could be global, regional, both, etc along with related rankings + mechanisms tried + your reasoning behind choosing them, where it is failing and why the remaining failures appear unresolved under the current constraints.

Do not stop until final_report.md is written.

Before proceeding, read necessary files, and reiterate your understanding along with any questions you may have. If you have no blocking questions, continue immediately into baseline verification and the first research loop.
```

If a reframe backend saw that prompt, a reasonable generated addendum would be:

```md
## Structural Reframe Addendum

Preserve the original objective, constraints, evaluation protocol, and final-report requirements exactly. Do not introduce new inputs, region labels, cell lookup tables, latitude/longitude hacks, or residual corrections.

Before continuing ordinary local search, zoom out from "improve per-region scores" and treat this as a structural modeling problem:

The current Model C is already strong globally. That means the next useful improvement is unlikely to come from merely retuning the same knobs. Look for missing global mechanisms that explain why the same formula succeeds in broad fire regimes but fails in specific regional regimes under the fixed input contract.

Use the analogies below as hypothesis generators, not as evidence.

### Lens 1: Epidemic Spread / Percolation Networks

A disease outbreak does not depend only on pathogen strength. It requires a connected susceptible population, transmission pathways, and permissive timing. If the network is fragmented, spread fails even when local conditions look favorable.

Map to burned area:
- susceptible population -> burnable fuel;
- network connectivity -> spatial/temporal fuel continuity;
- transmission probability -> ignition/spread favorability;
- fragmentation -> hyperarid fuel discontinuity, wet forest nonflammability, land-use-like heterogeneity not directly observed;
- outbreak timing -> dry-season curing and release.

Research implication:
Do not only ask whether fire is too high or too low in a region. Ask whether the formula is missing a global proxy for fuel-network connectivity or fragmentation. Test mechanisms where fire is allowed only when fuel, dryness, and continuity align. Consider smooth gates or limiters based on allowed combinations of Dbar, annual precipitation, monthly precipitation, GPP, and temperature.

Cheap tests:
- Add one global fuel-continuity or fragmentation term.
- Ablate it.
- Check whether it repairs weak regions without collapsing already-strong boreal/savanna regions.

### Lens 2: Combustion / Chemical Reactor Window

A reaction can require a substrate, oxygen, temperature, and timing. More substrate helps only up to a point; too much moisture or wrong timing can inhibit the reaction. The right model is often a window, not a monotone effect.

Map to burned area:
- substrate -> GPP/fuel;
- permissive state -> dryness;
- quencher -> current or persistent wetness;
- ignition temperature -> air temperature;
- reaction window -> intermediate regimes where fuel is present and burnable.

Research implication:
Look for variables that Model C treats as mostly monotone but may actually have two-sided effects. Annual precipitation and GPP are especially suspect: they can indicate fuel availability at low/intermediate values but wetness, canopy closure, or nonflammability at high values.

Cheap tests:
- Try combustion-window forms rather than one-sided suppressors.
- Compare standalone window terms against combinations with the existing Model C core.
- Reject if gains are only scalar and damage regional physical behavior.

### Lens 3: Seasonal Agriculture / Harvest Readiness

A crop is not harvested just because biomass exists. It must reach a harvestable state: grown, dried/cured, accessible, and timed with the right operating window. The stock and the readiness state are separate.

Map to burned area:
- crop biomass -> accumulated fuel/GPP;
- harvest readiness -> cured/dry fuel state;
- weather window -> dry month / low current precipitation / rising Dbar;
- harvest failure -> fuel exists but is too wet, too fragmented, or mistimed.

Research implication:
Separate "fuel stock" from "fuel readiness." Current-month GPP may not be enough. Test whether allowed history or transformations of GPP, Dbar, precipitation concentration, or drying tendency can represent accumulation and release.

Cheap tests:
- Lagged or accumulated GPP/fuel stock.
- Drying-rate or curing-phase gates.
- Wet-build / dry-release sequence terms.
- Ablate memory versus readiness to avoid adding complexity that only retunes the old model.

### Lens 4: Control System With Guardrails

A good controller does not maximize one signal everywhere. It uses limiters and guardrails to prevent unsafe regimes while preserving normal operation.

Map to burned area:
- base controller -> original Model C;
- guardrails -> wet, arid, cold, or timing limiters;
- unsafe operating regimes -> regions where Model C overpredicts or underpredicts due to missing regime constraints;
- controller instability -> global scalar gain bought by regional collapse.

Research implication:
Treat Model C as a strong base controller. Prefer small interpretable global guardrails around it before full retuning. A full retune may destroy the already-good global structure.

Cheap tests:
- Fixed-core global limiters.
- Then ablate each limiter.
- Only after a limiter is supported should you test a broader retune.

### Required Reframed Search Discipline

For each outer loop, record in `decision_trace.md`:

1. What structural failure does this loop target?
2. Which analogy/lens motivated the hypothesis?
3. What concrete mechanism follows from that lens?
4. What is the cheapest diagnostic or ablation that could falsify it?
5. What result would make you reject, demote, or continue the family?

Do not accept an analogy as truth. Use it only to generate candidate mechanisms. If an analogy produces no concrete formula change, diagnostic, or ablation, discard it.

Maintain a portfolio across mechanism families:
- at least one local continuation of Model C;
- at least one missing-limiter/guardrail family;
- at least one timing/readiness family;
- at least one fuel-continuity or stock-flow family;
- at least one interaction/window family.

Do not spend the full budget on a far analogy until a cheap diagnostic shows signal. Do not stop at a scalar improvement if it damages important regional behavior. The final accepted model must still satisfy the original evaluation and constraint requirements.
```

## Self-Evaluation Of The ED Fire Reframe

This reframe is decent, not magical.

Strong parts:

- It is contextual to the prompt.
- It preserves constraints.
- It does not tell the agent the final answer.
- It nudges toward structural mechanism families.
- It asks for cheap tests and ablations.
- It pushes against blind Optuna retuning.
- It fits the problem's surface and structure: fire spread, regimes, one global formula, fixed allowed inputs.

Weak parts:

- The backend here had prior knowledge of the experiment artifacts, so the lenses may be contaminated by what already worked.
- Percolation, combustion windows, stock-flow, and control guardrails are plausible even without prior knowledge, but the exact emphasis on wet/arid limiters and curing/readiness is influenced by the experiment history.
- A truly cold backend might generate less useful lenses.
- The addendum may still steer too much if the lenses are framed as too authoritative.

How to mitigate:

- Always include "hypothesis generator, not evidence."
- Always require cheap diagnostics.
- Always require rejection criteria.
- Maintain at least one local continuation family so the agent is not forced into far analogies.
- Require logging of alternatives considered.

## Product Direction

The CLI should produce tailored reframe blocks.

High-level pipeline:

```text
original prompt
  -> preserve original prompt
  -> extract rough task shape
  -> infer 3-5 structural lenses
  -> append mapped but tentative reframe addendum
  -> require cheap tests, ablations, and logging
```

What the CLI should output:

- not a final answer;
- not an analogy library dump;
- not a giant taxonomy;
- not a generic "be creative" paragraph;
- but a small tailored scaffold for structural search.

## Possible CLI Commands

```bash
reframe prompt.md --mode autoresearch --output prompt.reframed.md
```

```bash
reframe prompt.md --mode coding --output prompt.reframed.md
```

```bash
reframe prompt.md --mode science --output prompt.reframed.md
```

```bash
reframe prompt.md --mode general --output prompt.reframed.md
```

Useful flags:

```bash
--append-only
```

Preserve original prompt and append reframe block. Best for experiments.

```bash
--rewrite
```

Rewrite the prompt more naturally. Riskier for experiment validity.

```bash
--num-lenses 4
```

Control number of structural lenses.

```bash
--conservative
```

Use weaker steering and stronger warnings against overcommitting.

```bash
--include-decision-trace
```

Add requirements for auditable decision logging.

```bash
--with-search
```

Optional future mode. Use web/search/retrieval to find far analogies. Not MVP.

## Minimal Architecture

MVP can be simple:

1. CLI reads prompt file.
2. Calls LLM backend with a system prompt:
   - preserve objective/constraints;
   - infer task structure;
   - produce 3-5 structural lenses;
   - map lightly to the task;
   - avoid claiming certainty;
   - include cheap-test/rejection language.
3. CLI appends generated addendum to original prompt.
4. Writes output file.

No local library required.

No scoring required.

No mandatory web search required.

This is enough to test whether contextual reframing is better than a static addendum.

## Later Versions

Possible v2 features:

### Optional Web Retrieval

Use search to retrieve actual far-domain precedent cases.

The CLI, not the LLM, owns the search step.

The LLM receives snippets/articles and extracts structural lessons.

This could improve far analogies but adds latency and complexity.

### User-Supplied Analogy

Let user provide a known analogy:

```bash
reframe prompt.md --analogy "F1 pit crew neonatal handover"
```

The backend then uses that as a few-shot example of desired reasoning style.

### Audit Mode

After the agent run:

```bash
reframe audit run_logs/
```

It checks:

- Did the agent use structural lenses?
- Did it map source to target?
- Did the mapping create mechanisms/experiments?
- Did it reject failed analogies?
- Did it avoid overcommitting?
- Did the reasoning path differ from local continuation?

This is useful for paper/evaluation workflows.

### Prompt Pair Generation

For experiments:

```bash
reframe pair base_prompt.md --mode autoresearch
```

Produces:

- `base_prompt.md`
- `base_prompt.reframed.md`
- `diff.md`
- `metadata.json`

This helps preserve experimental traceability.

## Evaluation Strategy

Do not evaluate only by final score.

Evaluate by reasoning pathway:

- Did the agent explore different mechanism families?
- Did it identify structural failure modes?
- Did it avoid blind local continuation?
- Did it test and reject analogies?
- Did it preserve objective/constraints?
- Did it produce better decision traces?
- Did it reach a more defensible stopping point?

For score-based tasks, final score can be secondary evidence, but not the only signal.

## Failure Modes

### Over-Steering

The addendum gives a lens that sounds plausible and the agent overcommits.

Mitigation:

- require cheap tests;
- maintain portfolio;
- reject if constraints/objective fail;
- mark lenses as tentative.

### Generic Analogies

The backend emits obvious analogies that do not help.

Mitigation:

- require concrete next action;
- discard metaphor-only lenses;
- optionally use search in v2.

### Constraint Drift

The reframe causes the agent to violate the original task.

Mitigation:

- always preserve original prompt;
- always restate hard constraints;
- include explicit "do not change objective" language.

### Fake Creativity

The agent writes clever analogical prose but does the same thing.

Mitigation:

- require `decision_trace.md`;
- audit whether analogies changed mechanism selection;
- compare against control reasoning pathway.

### Prompt Bloat

The reframe block becomes too long and distracts from the task.

Mitigation:

- keep default to 3-4 lenses;
- concise mode;
- append-only with clear section boundaries.

## The Honest Claim

Bad claim:

> This CLI makes agents creative.

Better claim:

> This CLI rewrites prompts with a tailored structural-reframing scaffold that encourages agents to search across mechanisms, analogies, and failure structures while preserving task constraints.

Even better:

> This CLI is a search-prior intervention. It does not guarantee better answers; it changes the shape of the agent's exploration and makes that exploration more auditable.

## Additional Direction: Analogy Cards From Problem Structure

After reviewing the experiment results and the limitations of a pure prompt-rewriting approach, another plausible direction emerged:

> The CLI does not need to rewrite the entire autoresearch prompt. It can take a structured description of the problem and produce a set of cross-domain analogy cards with mappings, transferable moves, risks, and prompt nudges.

This is different from the earlier append-only prompt-reframer idea.

The prompt-reframer idea says:

```text
original prompt
  -> infer structure
  -> append structural-reframe scaffold
  -> downstream agent works inside the reframed prompt
```

The analogy-card idea says:

```text
problem structure
  -> search broadly across domains
  -> identify structurally similar precedents
  -> explain the source-target mapping
  -> extract transferable moves
  -> warn about failure modes
  -> output cards for user/agent use
```

The second version is more modest in one sense, but may be more useful.

It does not pretend that the CLI understands the entire codebase, benchmark, pipeline, or scientific context. It does not try to fully author the autoresearch prompt. Instead, it produces structured reframing material that a human or downstream agent can decide how to use.

### Why This Direction Makes Sense

The core problem we identified is not simply:

> Agents do not receive enough instructions.

The harder problem is:

> Agents often remain inside the local neighborhood of the task unless something pulls them toward remote but structurally relevant precedents.

The original experiment addendum did this weakly:

```text
Draw parallels and look at other fields...
```

That helped, but it relied on the model inventing or retrieving useful analogies on its own.

The small experiments comparing web-grounded analogy generation against no-tool analogy generation showed the important asymmetry:

- with search/tool use, many examples were stronger or medium-strong structural matches;
- without search/tool use, the examples were more likely to be obvious token-neighbor analogies;
- the no-tool examples often stayed near domains that language models have seen paired together many times, such as immune systems/cybersecurity or distributed consistency/bookkeeping;
- the web-grounded examples were more likely to include less obvious transfers where the mapping is not surface-obvious but the operational structure matters.

The key insight:

> Far analogies are often not recoverable from token association alone. Search helps because it exposes real precedents where some human or institution already performed the structural transfer.

This matters for the CLI because an LLM-only reframer may repeatedly produce generic analogies. A web-grounded analogy generator has a better chance of finding specific, weird, high-value precedents.

### What The CLI Would Take As Input

The input should not be only a raw prompt. It may work better if the user provides a structured problem description.

Example:

```md
# Objective
Improve a unified burned-area model without per-region routing.

# Current Failure
Model C has strong global performance but weak regional behavior. Regional repairs often damage global spatial or seasonal fit.

# Constraints
- no new external inputs;
- no latitude/longitude hacks;
- no named-region routing;
- one global functional form;
- mechanistic interpretability matters.

# Available Variables / Mechanisms
- temperature;
- precipitation;
- GPP / productivity;
- dryness;
- fuel availability;
- monthly and annual interactions.

# Desired Output
Cross-domain structural analogies that suggest mechanistic modeling directions.
```

This kind of input is more honest than expecting the CLI to infer everything from an autoresearch prompt. The user supplies the problem skeleton; the CLI supplies external structural parallels.

### What The CLI Would Output

The output should be analogy cards, not a giant rewritten prompt.

Each card should include:

- source domain;
- target problem structure;
- structural mapping;
- transferable move;
- possible model/research implication;
- why the analogy may transfer;
- where it may fail;
- surface-analogy risk;
- optional prompt nudge.

Example shape:

```md
## Analogy: F1 Pit Crew -> Neonatal Handover

Source domain:
F1 pit stops.

Target problem structure:
Time-constrained, high-risk, multi-actor handoff where ambiguity in roles, sequence, and positioning creates avoidable failure.

Structural mapping:
- pit crew roles -> clinical team roles;
- car arrival -> newborn arrival;
- fixed pit-box positioning -> predefined staff positioning;
- rehearsed choreography -> standardized handoff protocol;
- seconds lost -> clinical delay / error risk.

Transferable move:
Convert a loosely coordinated handoff into a choreographed, role-fixed, rehearsed protocol.

Why this may transfer:
Both systems are high-pressure handoffs where speed and correctness depend less on individual intelligence and more on coordination structure.

Where it may fail:
Medical care has diagnostic uncertainty and patient variability that F1 pit stops do not.

Prompt nudge:
Look for whether the current failure is caused by missing role assignment, sequencing, timing, or coordination protocol rather than lack of effort or information.
```

For the ED fire-model scenario, candidate cards might include:

- electrical circuits / gates / fuses;
- reservoir and spillway systems;
- epidemiological spread thresholds;
- supply-chain bottlenecks;
- pharmacological dose-response and toxicity;
- inventory accumulation and delayed release;
- traffic-flow congestion and shockwaves;
- firebreaks and compartmentalization;
- control systems with damping and overshoot;
- queue backlog and draining dynamics.

But the important thing is not the list. The important thing is the mapping quality.

A bad card says:

> Fire spreads like epidemics.

A better card says:

> Burned area may depend on a susceptible stock, transmission window, ignition/contact pressure, and removal/depletion process. The transferable move is to separate fuel availability from spread permissiveness and test whether the current model incorrectly treats productivity as always enabling fire instead of allowing saturation or depletion.

The card needs to translate the source structure into a testable target-side hypothesis.

### Internet Usage

Internet usage should be treated as a serious design axis, not an afterthought.

Relying on the model API's own browsing is fragile:

- some APIs support web search;
- some do not;
- Azure deployments may not expose browsing in the same way;
- local models will not have browsing;
- model-provider browsing behavior may be opaque or inconsistent.

The cleaner architecture is:

```text
CLI owns retrieval.
LLM owns extraction, mapping, critique, and synthesis.
```

The CLI can use a search adapter:

- Brave Search API;
- Tavily;
- SerpAPI;
- Bing Web Search;
- another provider-specific search API;
- later, perhaps local document corpora.

Then the LLM receives retrieved snippets or articles and performs the structural mapping.

This has two benefits:

1. The same CLI can work with OpenAI, Azure OpenAI, Anthropic, local models, or other providers.
2. The retrieval layer is auditable: the output can cite what source inspired each analogy.

This does not mean every run must use search. But for high-quality far analogies, search likely matters.

### Ranking Without Pretending To Have A Real Scoring Function

The CLI should avoid fake precision.

It should not say:

```text
Analogy score: 91/100
```

That implies a scoring function that does not really exist.

Instead, it can use qualitative triage labels:

- structural fit: low / medium / high;
- transferable mechanism clarity: low / medium / high;
- constraint compatibility: low / medium / high;
- surface-analogy risk: low / medium / high;
- actionability: low / medium / high;
- novelty relative to obvious local framing: low / medium / high.

This is not a judge of truth. It is a sorting aid.

The CLI should be explicit:

> These ratings are heuristic triage labels for human review, not proof that the analogy is correct.

### Why This Should Not Automatically Choose The Final Research Direction

The CLI should not say:

> Use analogy X. It is best.

That would be dangerous because a plausible analogy can cook the research if it becomes the answer instead of a hypothesis generator.

Better:

> Here are structurally plausible lenses. Here is why each might transfer. Here is the concrete move each suggests. Here is where each may mislead you.

Then the user or downstream autoresearch agent decides whether to:

- inject one or two cards into the prompt;
- include the full card list as optional inspiration;
- ask the agent to choose among cards;
- use cards only as decision-trace scaffolding;
- ignore cards that look weak.

This preserves agency and reduces over-steering.

### Relationship To Prompt Rewriting

This direction does not eliminate prompt rewriting. It changes its role.

A possible workflow:

```bash
reframe analogies problem_structure.md --web --out analogy_cards.md
```

Then later:

```bash
reframe prompt base_prompt.md --cards analogy_cards.md --append-only --out prompt.reframed.md
```

But the first command is useful by itself.

This is important because the user may not want the CLI to touch the autoresearch prompt at all. They may only want a high-quality set of structural analogies and mechanism nudges, then manually decide what belongs in the prompt.

That may be the more robust product shape:

> First generate useful reframe material. Only later automate prompt integration.

### Experiment 5 Implication

This suggests a cleaner future experiment.

Instead of only testing:

```text
control prompt
vs
control prompt + generic "draw parallels" paragraph
```

we can test:

```text
control prompt
vs
generic structural-reframe paragraph
vs
LLM-only generated analogy cards
vs
web-grounded analogy cards
```

This would separate several effects:

1. Does merely asking for structural analogy help?
2. Does an LLM-generated list of analogies help more than the generic paragraph?
3. Does web-grounded analogy retrieval produce better reasoning traces than LLM-only analogy generation?
4. Does the agent use the cards as hypothesis generators or as decorative language?
5. Does the agent test, reject, and refine analogies instead of overcommitting?

For the ED fire task, experiment 5 could proceed like this:

1. Write a structured problem description of the burned-area model task.
2. Generate analogy cards with search enabled.
3. Generate another analogy-card set without search.
4. Inject a controlled number of cards into otherwise matched autoresearch prompts.
5. Require `decision_trace.md` to log whether a card caused a mechanism choice.
6. Compare reasoning pathways, not only scores.

The key analysis question would be:

> Did the analogy cards create genuinely different mechanism families or only rename ordinary local moves?

This connects directly to the earlier experiment analyses.

### Updated Product Interpretation

The earlier document leaned toward:

> Build a CLI that appends a tailored structural-reframe scaffold to a prompt.

The newer idea is:

> Build a CLI that helps users discover and inspect structurally relevant analogies before deciding how to steer the agent.

These are compatible, but they are not the same.

The analogy-card approach is less magical and more inspectable. It makes the uncertain part visible:

- what analogy is being proposed;
- what structural mapping is claimed;
- what move is transferable;
- what could go wrong;
- how the downstream agent might test it.

This is probably a better way to avoid both extremes:

- a static paragraph that is too weak;
- a giant prompt rewrite that over-steers the agent.

The product can remain project-agnostic because it does not need to understand the full project internals. It only needs a structured problem description and constraints. The deeper project-specific translation can remain with the human or with the downstream autoresearch agent.

## Current Bottom Line

The most promising v1 is not retrieval-heavy and not library-heavy.

Build:

- append-only prompt reframer;
- contextual LLM-generated structural lenses;
- project-agnostic but task-aware;
- conservative guardrails;
- cheap-test/reject discipline;
- decision-trace requirement;
- optional user-supplied analogy;
- optional future search mode.

The key product bet:

> Agents do not reliably perform far structural analogy on their own. But if we prompt them with a contextual structural scaffold and require them to convert analogies into testable hypotheses, we can push autoresearch away from narrow local continuation without forcing a specific answer.
