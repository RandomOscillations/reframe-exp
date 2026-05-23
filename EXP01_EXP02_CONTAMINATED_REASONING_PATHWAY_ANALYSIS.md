# Exp 01 / Exp 02 Contaminated Reasoning Pathway Analysis

Date: 2026-05-22

Scope: ED fire Model C autoresearch experiments `exp_01` and `exp_02`.

Question: did the reframe agents reason differently from the control/base agents, or did they mostly benefit from seeing control results and benchmark artifacts?

Important constraint for this document: the score outcomes are not the object of analysis. Scores are used only as evidence for what the agents noticed, what they optimized toward, what they rejected, and what they treated as a promising direction. The real object is the search trajectory: hypothesis formation, choice of mechanism families, failure interpretation, ablation logic, and final decision policy.

## Executive conclusion

Exp 01 and exp 02 should not be used as clean benchmark evidence for the reframe prompt. They are still useful as contaminated reasoning case studies.

The short version:

- Exp 01 reframe shows a genuinely different style from exp 01 base/control: it starts from structural analogies like percolation, epidemic spread, chemical reactors, wet/canopy inhibition, and arid fuel discontinuity, then composes global limiters on top of Model C. The base/control path is more local and incremental: wet suppression, lagged fuel, lag+wet, precipitation memory. However, exp 01 reframe ran with path/root contamination and had visibility into artifacts outside the intended isolated workspace. Therefore the trajectory cannot be causally attributed to the reframe paragraph alone.

- Exp 02 contaminated reframe is even less usable as clean prompt-effect evidence. The high-ceiling trajectory is strongly entangled with already visible benchmark/control artifacts. The reframe log explicitly uses existing public benchmark artifacts including `ED-loop13-combined`, `ED-loop13-aridatt`, and `ED-loop13-aridboreal-5`; it also adopts the P2F3 -> curing/hotwet line that the base/control continuation had already developed. The reasoning is structurally phrased, but the direction selection is almost certainly leakage-assisted.

- Exp 02 also contains a later clean/isolated reframe record. That clean reframe pass did not reproduce the 0.69 ceiling trajectory. It explored structural analogies and mechanism families, but retained original Model C after finding no defensible step-function improvement. This is strong evidence that the contaminated exp 02 high ceiling was not cleanly caused by the reframe prompt alone.

- Across both experiments, the reframe prompt seems to increase the probability of structural-language reasoning: substrate inhibition, readiness gates, percolation, fuel continuity, queueing, combustion timing, ecological niche curves. But in exp 01 and especially exp 02, the strongest final directions are not clean evidence of independent discovery because the agent had access to conclusions or artifacts that should have been hidden.

My attribution judgement:

| Experiment | Was reframe reasoning visibly different? | Was it cleanly attributable to the prompt? | Main reason |
|---|---|---|---|
| Exp 01 | Yes, moderately to strongly | No | Reframe workspace/path contamination gave access outside the intended run boundary. |
| Exp 02 contaminated archive | Yes in wording, but heavily aligned with leaked directions | No, very likely contamination-dominated | Reframe saw/used existing public/control artifacts and selected from that discovered frontier. |
| Exp 02 later clean reframe record | Yes, but conservative | Partly, for reasoning style only | It used structural analogies but did not find the high-ceiling path. |

## Evidence map

Primary exp 01 records:

- `reframe-exps/experiments/exp_01/harnesses/hermes/base_run/logs/research_log.md`
- `reframe-exps/experiments/exp_01/harnesses/hermes/base_run/logs/final_report.md`
- `reframe-exps/experiments/exp_01/harnesses/hermes/base_run/logs/candidate_registry.md`
- `reframe-exps/experiments/exp_01/harnesses/hermes/reframe_pass_1/logs/research_log.md`
- `reframe-exps/experiments/exp_01/harnesses/hermes/reframe_pass_1/logs/final_report.md`
- `reframe-exps/experiments/exp_01/harnesses/hermes/reframe_pass_2_continuation/logs/research_log.md`
- `_archive/2026-05-14__ed_fire_exp01_hermes_structural_reframe_pass1_completed_run/full_workspace/research_log.md`
- `_archive/2026-05-14__ed_fire_exp01_hermes_structural_reframe_pass1_completed_run/full_workspace/final_report.md`

Primary exp 02 records:

- `reframe-exps/experiments/exp_02/harnesses/hermes/base_run/pass_1_p2f3_continuation/logs/research_log.md`
- `reframe-exps/experiments/exp_02/harnesses/hermes/base_run/pass_2_ceiling_continuation/logs/research_log.md`
- `reframe-exps/experiments/exp_02/harnesses/hermes/base_run/pass_3_loop13_ceiling_check/logs/research_log.md`
- `_archive/exp_02_contaminated_base_and_reframe_20260515_010741/reframe/research_log.md`
- `_archive/exp_02_contaminated_base_and_reframe_20260515_010741/reframe/final_report.md`
- `_archive/exp_02_contaminated_base_and_reframe_20260515_010741/reframe/candidate_registry.md`
- `reframe-exps/experiments/exp_02/harnesses/hermes/reframe_run/pass_1_clean_reframe_from_original_model_c/logs/research_log.md`
- `reframe-exps/experiments/exp_02/harnesses/hermes/reframe_run/pass_1_clean_reframe_from_original_model_c/logs/final_report.md`

Prompt difference caveat:

- Exp 02 prompt diff is close to the intended comparison: the reframe prompt adds the structural analogy paragraph and some stronger "do not stop at small gains" language.
- Exp 01 prompt diff is less clean: the reframe prompt is not merely the base prompt plus the analogy paragraph. It also changes phrasing around fire types/region types, final reporting, and stopping. This makes exp 01 less clean even before considering workspace contamination.

## What counts as contamination here

I am using "contamination" in two senses.

First, visibility contamination: the agent could see files, prior artifacts, benchmark rows, candidate names, or final reports that a clean independent run should not have been able to see.

Second, trajectory contamination: the agent's actual search path appears to depend on those visible artifacts. This is stronger than mere visibility. It means the agent did not just reason in a similar way; it selected hypotheses, candidates, or continuation points that were already available in another run's artifacts.

Exp 01 has very strong visibility contamination and moderate trajectory-contamination evidence.

Exp 02 contaminated archive has both strong visibility contamination and strong trajectory-contamination evidence.

## Exp 01: base/control reasoning pathway

The exp 01 base/control run is a local mechanistic extension search around original Model C.

It starts by accepting original Model C as the baseline and then asks: which nearby smooth physical terms might repair the observed failures without breaking the fixed input contract?

The key pattern is local repair around existing Model C factors:

1. Wet suppression
2. Lagged fuel
3. Lag plus wet
4. Precipitation memory

### Base loop 1: WET-SUPP-v1

The first base hypothesis is direct and local: perhumid climates may suppress fire through persistent wet fuels or boundary-layer moisture despite abundant fuel.

The formula change is a high-annual-precipitation dampener:

```text
fire *= 1 / (1 + (P_ann / P_wet_half) ^ P_wet_pow)
```

Reasoning pathway:

- The agent observes weak humid/tropical regions.
- It interprets the failure as overfire in wet regimes.
- It adds one smooth global suppressor based on annual precipitation.
- It evaluates the result, sees some regional gains, but sees global and savanna/Australia tradeoffs.
- It rejects the candidate as final.

This is a classic "add missing suppressor" move. It is mechanistic, but it is not a zoomed-out structural search. The agent does not start from an abstract problem structure; it starts from a direct fire-process term.

### Base loop 2: LAG-FUEL-v1

The second hypothesis is that fire responds to antecedent or cured productivity, not only same-month GPP.

The formula changes the GPP input to a lagged mean:

```text
GPP_eff = (1 - alpha) * GPP_month + alpha * mean(previous window months)
```

Reasoning pathway:

- The agent notices that Model C's current-month GPP may not represent burnable cured fuel.
- It tries a recent-productivity memory term.
- The candidate improves scalar/global/public score slightly.
- It damages multiple regional scores.
- The agent rejects it as an accepted model, but records it as highest scalar/global trial.

This is still local extension logic: "replace one input in one existing factor with a memory version." It does not reorganize the model around a new system structure.

### Base loop 2b: LAG+WET

The third move combines the two local repairs.

Reasoning pathway:

- If lagged fuel helps seasonality but damages humid regions, maybe wet suppression can compensate.
- The agent combines the best lagged-fuel and wet-suppression settings.
- It sees that the regional-damage failure mode persists.
- It rejects the combination.

This is a local ablation/composition step: combine two nearby terms and see if their failures cancel.

### Base loop 3: PRECIP-MEM-v1

The next hypothesis is antecedent precipitation moisture.

The formula changes current monthly precipitation into a recent precipitation memory:

```text
P_month_eff = (1 - alpha) * P_month + alpha * mean(previous window months)
```

Reasoning pathway:

- The agent realizes current-month rainfall dampening may be too instantaneous.
- It tests whether recent precipitation memory better captures moisture/accessibility.
- It observes many weak-region improvements but African savanna damage and global spatial decline.
- It rejects the candidate.

Again the structure is local: substitute a smoothed version of an existing driver into an existing dampening term.

### Exp 01 base final reasoning

The base run concludes that the explored local smooth extensions expose a tradeoff surface:

- wet/moisture terms can repair some weak humid/temperate regions;
- lag/fuel-memory terms can move scalar/global scores;
- but the improvements come with regional damage, especially savanna, boreal, or spatial-distribution losses.

The final decision is conservative: original Model C remains the accepted model, while LAG-FUEL-v1 is retained only as a rejected scalar-best diagnostic.

This is local-search behavior: propose plausible nearby process terms, evaluate, reject when tradeoffs appear, and stop when no local extension improves both global and regional behavior.

## Exp 01: reframe reasoning pathway

The exp 01 reframe pass has a visibly different reasoning style.

It begins by explicitly framing fire as a structural system:

- outbreak/percolation system;
- fuel must be built and spatially/temporally connected;
- drying/ignition releases the system;
- analogies to epidemics, percolation, and chemical reactors;
- excessive resource can inhibit the reaction.

That is not just a different name for the base path. It changes what the agent treats as a candidate mechanism.

### Reframe pass 1 loop 1: antecedent fuel / wet-dry pulse

The first reframe loop resembles the base lagged-fuel idea on the surface, but the reasoning is framed differently.

Base framing:

- maybe same-month GPP should be recent GPP;
- test lagged GPP in the GPP hump.

Reframe framing:

- fire occurrence is an outbreak/percolation event;
- fuel must become connected;
- the system then needs drying/ignition release;
- test a wet-dry pulse or antecedent fuel mechanism.

The actual mechanism overlaps with base local search, but the framing is more structural. The reframe agent is not only asking "should GPP be lagged?" It is asking "what is the latent system state that permits spread?"

It rejects the loop because the useful signal collapses back to baseline or is captured by Model C's existing GPP/monthly seasonality.

### Reframe pass 1 loop 2: annual precipitation combustion window

The second loop reframes annual precipitation as a two-sided process:

- low/intermediate precipitation supplies fuel;
- high precipitation inhibits combustion/canopy drying.

This is the substrate-inhibition or chemical-reactor style move: the same resource can help at one level and suppress at another.

The base run also tested wet suppression. The difference is that the reframe run's conceptual category is broader: precipitation is not merely a scalar wetness penalty, it is a combustion window.

The standalone attempt is rejected because it over-suppresses or trades off against savanna signal.

### Reframe pass 1 loop 3: fixed-core wet/arid/cool suppressors

This is the main exp 01 reframe shift.

Instead of continuing to tune memory or precipitation terms inside the existing Model C factors, the agent keeps the original Model C core and adds missing global limiters:

- wet/canopy inhibition for persistently wet regimes;
- hyperarid fuel-discontinuity inhibition using `Dbar / (P_ann + ratio_p0)`;
- a small cool suppressor later pruned.

Reasoning pathway:

- Model C already captures broad seasonal phase.
- The failures look like missing regime limiters, not wholesale parameter slack.
- Fire spread requires a connected susceptible/fuel network.
- High wetness and hyperaridity are opposite ways the network fails.
- Keep the validated Model C core.
- Add smooth global limiters for the two failure modes.
- Ablate unnecessary complexity.

This is qualitatively different from the base path. The base run kept testing substitutions inside existing terms. The reframe run treated Model C as a strong core and searched for missing boundary conditions around it.

### Reframe pass 1 loop 4: full retune rejected

The reframe agent then tests whether the accepted suppressors permit full core retuning.

The important reasoning is not the outcome. The important reasoning is the rejection:

- the broader 22-parameter family is less stable;
- the best internal candidate collapses back toward baseline;
- preserving the validated core plus interpretable limiters is more defensible.

That is a model-selection policy based on mechanistic parsimony, not merely score chasing.

### Reframe pass 2: continuation from F3b

Pass 2 continues from the reframe pass 1 accepted state.

The agent explicitly reads prior reframe artifacts and asks what structural failures remain:

- F3b uses static annual wet/arid limiters;
- remaining failures may require timing/synchronization;
- arid fuel-continuity may need two thresholds rather than a single cliff;
- seasonal wet inhibition may need timing dependence.

The pass 2 loops are:

1. Seasonal curing/synchronization gate
2. Seasonal wet/canopy inhibition
3. Two-threshold arid fuel-continuity limiter
4. Hybrid seasonal wet plus arid two-threshold limiter

The reasoning is structural:

- traffic-light phase control / combustion-engine ignition timing for curing gates;
- warehouse scheduling / bottleneck timing for seasonal wetness;
- communications networks / epidemics / percolation for arid fragmentation.

The most important part is the two-threshold arid limiter:

- a dryland fuel network does not fail at one hard cliff;
- it first loses redundancy, then becomes desert-discontinuous;
- the final accepted family represents gradual network degradation plus strong desert cutoff.

This is not the same pathway as the exp 01 base run. It is a structural refinement of an already structural reframe pass 1 model.

## Exp 01 contamination assessment

Exp 01 cannot be used as a clean causal comparison.

The contamination evidence:

- The completed reframe archive is stored as `_archive/2026-05-14__ed_fire_exp01_hermes_structural_reframe_pass1_completed_run/full_workspace/`, not merely a clean isolated `exp-workspaces/exp_01/hermes/reframe` subtree.
- The archive README describes `full_workspace/` as the full local Hermes experiment workspace after the run.
- The public benchmark output table in the reframe final report contains rows for artifacts that look like broader/root benchmark state, including `ED-ModelC-precip-conc-wet-curing-lag-v1-current`, `ED-ModelC-precip-conc-wet-v1-current`, `ED-ModelC-dryseason-wet-v1-current`, and `ED-ModelC-curing-lag-v1-current`.
- The user also flagged that the reframe agent got paths mixed up and ended up at root, meaning it could see the control prompt experiment fully.

What can be claimed:

- The reframe agent's written reasoning is structurally different from the base/control reasoning.
- It uses the addendum style: analogical transfer, process structure, percolation, reaction/substrate inhibition, phase control.
- It builds mechanisms as missing global system limiters rather than only local substitutions.

What cannot be claimed:

- We cannot say that the reframe paragraph alone caused the F3b/P2F3 direction.
- We cannot say the agent independently discovered the improvement path without access to control or root artifacts.
- We cannot use exp 01 as clean benchmark evidence for score improvement or step-function reasoning improvement.

My best interpretation:

Exp 01 reframe probably did reason differently, but the run is too contaminated to prove that this different reasoning was caused only by the reframe addendum. It is useful as a qualitative example of the kind of reasoning the addendum encourages, not as clean experimental evidence.

## Exp 02: base/control reasoning pathway

Exp 02 base/control is important because it creates the trajectory that later contaminates the reframe run.

Unlike exp 01 base, exp 02 base did eventually develop the high-ceiling line:

1. Local/nearby mechanisms
2. Wet-temperature failure
3. Warm-gated wet variants
4. Annual wet/dry-month mechanisms
5. P2F3 wet/arid limiters
6. Curing-phase enhancement
7. Hot/warm wet-month compensation
8. Loop13 ceiling checks around arid attenuation, boreal protection, and wet/productive attenuation

### Base phase 1: local checks and wet-temperature path

The base run begins with familiar local questions:

- Is there parameter slack in original Model C?
- Does lagged/cured fine-fuel memory help?
- Does dry-shifted GPP saturation help?
- Does precipitation concentration suppress wet-season/monsoon cells?
- Should wet fuels require a higher ignition temperature?

The first material movement comes from wet-temperature interaction:

```text
T_ignition_threshold = ign_c + wet_temp_shift * p_month / (p_month + wet_half)
```

The reasoning is straightforward:

- warm temperatures should not raise ignition equally during wet months;
- wet fuels require higher effective ignition temperature;
- this improves many weak regions;
- but it severely damages BONA/BOAS spatial structure.

This failure becomes a crucial branch point. It tells the base agent not just what works, but what kind of thing fails: region-blind monthly wet suppression is too blunt, especially for boreal/cold wet regimes.

### Base continuation: warm/liquid/cold gating

The next base loops are direct repairs to the wet-temperature failure:

- liquid-rain wetness proxy;
- warm-gated wet temperature;
- combined liquid/warm gate.

Reasoning:

- the wet-temperature idea may be valid only where precipitation is liquid/warm;
- cold/snow precipitation should not suppress boreal fire the same way;
- gate wet suppression by thermal regime to avoid BONA/BOAS collapse.

This is still local repair, but now the agent is using failure analysis to add conditional guards.

### Base annual wet/dry-month mechanisms

The base then moves to persistent wet-canopy and dry-month concentration:

- annual wet suppression;
- dry-month concentration;
- low-amplitude climate suppressors;
- warm-gated wet plus annual-wet hybrid.

Reasoning:

- weak-region gains may require persistent wet-canopy suppression or precipitation seasonality rather than monthly wet-temperature shifts;
- annual wet suppression has a strong EQAS/SEAS signal but not enough global gain;
- hybridizing gives balance but not a material step.

This is the bridge toward P2F3.

### Base P2F3

The base then identifies the central structural mechanism:

```text
base_rate = original Model C annual rate
wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)
arid_soft = 1 - arid_amp1 * sigmoid(Dbar / (P_ann + p0), arid_k1, arid_c1)
arid_desert = 1 - arid_amp2 * sigmoid(Dbar / (P_ann + p0), arid_k2, arid_c2)
fire_rate = base_rate * wet_suppress * arid_soft * arid_desert
```

Reasoning pathway:

- remaining failures are not mainly monthly wet ignition;
- they reflect missing global limiters at wet and arid extremes;
- BONA/BOAS failure argues against monthly wet-temperature suppression;
- arid fragmentation can be represented by `Dbar / P_ann`;
- persistent wetness can be represented by annual precipitation;
- two arid thresholds represent different degrees of fuel-network fragmentation.

This is a genuine structural move, even though it occurs in the base/control run. It means the reframe prompt is not the only route by which this agent can reach structural mechanism composition.

### Base curing/hotwet line

After P2F3, the base continues:

- P2F3 fixes wet/arid overprediction but misses within-year fire-season amplification.
- Add a drying/curing phase enhancement using Dbar tendency, dry-month concentration, and warm-month gate.
- Then add warm/hot wet-month compensation to avoid over-burning warm wet regimes.

The accepted balanced line becomes `ED-next-curing-hotwet-1`.

Reasoning pathway:

- P2F3 is a structural boundary-condition model.
- It improves broad weak regions but does not fix AUST seasonality/global spatial enough.
- Fire-season hazard is not only state but transition: actively drying fuels become flammable.
- Curing boost improves global/AUST/spatial.
- Wet-month compensation is needed to prevent over-burn in warm wet regimes.
- Warm/hot gating avoids the earlier BONA/BOAS collapse.

### Base loop13 ceiling check

The final base pass tests whether the hotwet line can be pushed further:

- boreal-protected wet compensation;
- arid-deficit curing attenuation;
- wet/productive curing attenuation;
- combined protection/attenuation.

Reasoning:

- high-scalar variants exist;
- arid attenuation and broader wet compensation improve global/public scalar and dryland regions;
- but they repeatedly damage BONA/BOAS and sometimes AUST/wet-region balance;
- boreal protection only partially repairs the damage;
- therefore hotwet remains best balanced, while loop13 combined is highest scalar/public but rejected.

This is a mature local-to-global continuation. The base run itself develops a structural understanding through repeated failures.

## Exp 02 contaminated reframe reasoning pathway

The contaminated exp 02 reframe archive looks structurally sophisticated, but its path is entangled with visible prior/base artifacts.

### Contaminated reframe initial triage

The reframe agent starts with structural language:

- drying-front/curing-rate gate;
- fuel-memory/carryover productivity;
- moisture seasonality/rain concentration;
- temperature/moisture interaction refinements;
- analogies to phase transitions, chemical ignition, capacitor charge/discharge, staged logistics, queueing burstiness.

This is a real reframe-style hypothesis set. It is broader and more analogical than a purely local parameter search.

### Contaminated reframe loop 1: base search families

The first reframe layer implements:

- `drying`
- `fuelmem`
- `relwet`
- `annwet`
- `tempopt`
- `gppdry`
- `combined`
- `combined2`

The serious first-layer candidates are `combined` and `combined2`.

Reasoning pathway:

- weak regions are mostly spatial/regional, not seasonal;
- missing mechanisms might be drying-front timing, fuel memory, relative rain concentration, wet suppression, temperature optimum, or joint fuel-dryness gates;
- combine them into global formula families;
- use official/regional/public evidence for acceptance;
- reject standalone combined mechanisms because they improve some regions but cause spatial/boreal or regional tradeoffs.

This first layer looks more independently generated. It does not simply copy P2F3 at the start.

### Contaminated reframe loop 2: P2F3

Then the reframe trajectory moves to P2F3:

- persistent wet-climate suppression;
- arid-deficit fuel limitation based on `Dbar / P_ann`;
- both wet and arid extremes limit fire through different mechanisms;
- public/global score improves to the known P2F3 score.

This is where attribution becomes weak.

The P2F3 mechanism is exactly the base/control path's key intermediate. In a clean run, the reframe agent could have rediscovered it. But in this contaminated archive, it had access to public benchmark artifacts and prior rows. Therefore this step cannot be treated as independent discovery.

### Contaminated reframe loop 3: curing phase and hotwet final

The contaminated reframe then adds:

- drying-front phase boost from Dbar tendency;
- precipitation concentration;
- warm-month ignition;
- warm-climate wet-month compensation;
- final reproducible candidate `p2f3_curing_hotwet_final`.

This mirrors the base/control P2F3 -> curing -> hotwet continuation.

Reasoning pathway as written:

- P2F3 improves wet/arid extremes but incomplete spatial/regional behavior remains.
- Fire hazard depends on transition into a flammable phase, not only instantaneous moisture.
- Curing boost captures active drying and dry-month concentration.
- Wet-month compensation prevents warm wet overburn.
- Warm gating avoids excessive suppression of cold/boreal wet periods.

This is coherent reasoning. The problem is attribution. The exact path and candidate family were already present in the contaminated environment.

### Contaminated reframe loop 4: loop13 artifacts

The clearest contamination evidence is in loop 4 of the contaminated reframe log:

- The agent states that existing public benchmark artifacts contain stronger public global variants:
  - `ED-loop13-combined`
  - `ED-loop13-aridatt`
  - `ED-loop13-aridboreal-5`
- It reports these as highest public-score context.
- It does not accept them because it cannot find a reproducible local formula/source path.

This is not merely the agent making a similar inference. It is reading existing artifacts from the contaminated public benchmark state and using them to set the known ceiling.

The final contaminated reframe decision is:

- accept `p2f3_curing_hotwet_final` as the highest defensible reproducible final model;
- report `ED-loop13-combined` as highest public-score artifact/context;
- reject loop13 as final because reproducibility could not be established locally.

This is a good scientific decision under contaminated conditions, but it is not clean experimental evidence.

## Exp 02 clean reframe record

The later clean exp 02 reframe record is essential for attribution.

It uses a clean benchmark root:

- `public_benchmark_clean`
- `scripts/run_public_trendy_firepipe_clean.sh`
- workspace manifest explicitly says clean benchmark contains only official benchmark models plus `EDv3`.

The clean reframe pass uses structural analogies:

- substrate inhibition;
- readiness gates;
- thermal performance curves;
- percolation/fuel continuity;
- wetness plus curing hybrid.

It tests:

1. Annual wetness suppression / substrate inhibition
2. Seasonal curing/readiness gate
3. High-temperature stress ceiling
4. Annual GPP fuel-continuity/percolation gate
5. Wet suppression plus curing hybrid
6. Full hybrid
7. Fixed-baseline weak wet-suppression ablation

It retains original Model C.

It then has a pass 2 in the live workspace that tries:

1. Flexible GPP shape / asymmetric productivity niche
2. Lagged fuel memory / stock-and-flow inventory
3. Wet-build / dry-burn pulse
4. Memory plus pulse hybrid
5. Flexible dry-window shape
6. Ablation of lagged fuel memory

It again retains original Model C.

This matters because the clean reframe reasoning style is present, but the high-ceiling P2F3/hotwet/loop13 path does not emerge in the same way. That is strong evidence that the contaminated exp 02 high result depended heavily on visible artifacts.

## Exp 02 contamination assessment

Exp 02 contaminated reframe cannot support a clean claim that the reframe prompt caused the 0.69 ceiling.

Evidence:

- The contaminated reframe final report lists `ED-loop13-combined`, `ED-loop13-aridatt`, and `ED-loop13-aridboreal-5` in the public ranking table.
- It says the highest public-score artifact found is `ED-loop13-combined`.
- It says no local reproducible formula/source path was found for loop13 variants.
- It selects `p2f3_curing_hotwet_final` because it is reproducible, while reporting loop13 as context.
- The contaminated reframe research log explicitly says existing public benchmark artifacts contain stronger public global variants.
- The base/control pass had already generated the P2F3 -> curing/hotwet -> loop13 trajectory.

Trajectory contamination is strong:

- P2F3 appears as the same key intermediate.
- Curing/hotwet appears as the same next major line.
- Loop13 artifacts appear as known public ceiling context.
- The reframe agent's final decision depends on reproducibility of known artifacts, not purely on independent hypothesis discovery.

What can be claimed:

- The contaminated reframe agent writes a coherent structural rationale for the P2F3/hotwet line.
- It correctly distinguishes accepted reproducible model from non-reproducible public artifacts.
- It uses the reframe style to narrate the mechanism: drying-front transition, warm-gated wet compensation, wet/arid bounds, queueing/burstiness, combustion systems.

What cannot be claimed:

- That the reframe prompt independently discovered the 0.69 ceiling.
- That the reframe prompt alone caused the P2F3/hotwet direction.
- That exp 02 demonstrates a clean step-function reasoning upgrade.

My best interpretation:

The exp 02 contaminated high-ceiling result is primarily contamination-assisted. The reframe prompt likely helped the agent explain and organize the mechanism structurally, but the direction and ceiling were available through leaked benchmark/control artifacts.

## Direct comparison: exp 01 vs exp 02 vs exp 03

Exp 03 was the cleaner comparison analyzed separately. In exp 03, the reframe prompt changed the search prior but did not yield a huge step-function score jump. It pushed the agent toward structural mechanism composition, but the control eventually also found sophisticated local/state-based suppressors.

Exp 01 is contaminated but shows a strong reframe-style trajectory:

- base/control: local substitutions and suppressors;
- reframe: missing global limiters, percolation/substrate framing, fixed core plus interpretable boundary terms;
- attribution blocked by root/path contamination.

Exp 02 is contaminated and shows why contamination can fake a step function:

- base/control generated the high-ceiling path;
- contaminated reframe could see the public artifact frontier;
- contaminated reframe selected/organized around P2F3/hotwet/loop13;
- clean reframe did not reproduce the 0.69 path.

The cleanest overall claim remains the exp 03 style claim:

The reframe addendum appears to alter the hypothesis-generation prior. It makes the agent more likely to search for structural analogies, system limiters, regime gates, and mechanism composition. It does not prove a step-function reasoning upgrade in the sense of new capability. In contaminated exp 01/02, the strongest apparent upgrades are not causally interpretable.

## Reasoning-pathway coding dimensions

If these experiments are later coded for the paper, I would code the trajectories on these dimensions.

### 1. Starting frame

Base/control often starts with:

- parameter slack;
- direct physical missing term;
- current-term substitution;
- wetness/gpp/precip memory.

Reframe often starts with:

- process structure;
- spread/percolation;
- resource inhibition;
- readiness gates;
- phase transition;
- queueing/burstiness;
- stock-flow inventory.

### 2. Unit of hypothesis

Base/control often uses one local modified factor:

- replace GPP with lagged GPP;
- replace P_month with precipitation memory;
- add wet-month ignition penalty;
- add rain pulse suppressor.

Reframe often uses mechanism families:

- wet and arid extremes as boundary conditions;
- stock plus release;
- curing phase plus compensation;
- two-threshold network fragmentation.

### 3. Failure interpretation

Base/control often says:

- this candidate improves scalar but damages region X;
- this local term is too blunt;
- try a gated version.

Reframe often says:

- the system is missing a limiter;
- the failure is a boundary condition problem;
- the same resource has opposite effects at different regimes;
- a process requires timing alignment or connectedness.

### 4. Abstraction level

Base/control:

- mostly driver-level and term-level.

Reframe:

- more system-level and regime-level.

### 5. Attribution vulnerability

Exp 01:

- high vulnerability due workspace/root visibility;
- different reasoning visible, causal attribution weak.

Exp 02 contaminated:

- very high vulnerability due benchmark/public artifact leakage;
- high-ceiling path likely contamination-driven.

Exp 02 clean:

- lower vulnerability;
- structural style visible but no high-ceiling result.

Exp 03:

- best available comparison for prompt-effect reasoning-pathway claims.

## Paper-use recommendation

Do not use exp 01 or exp 02 as clean evidence of performance improvement.

Use exp 01 and exp 02, if at all, as:

1. Negative controls / contamination case studies.
2. Examples of why artifact isolation matters in autoresearch evaluation.
3. Qualitative evidence that reframe-style language appears in agent logs when prompted.
4. Evidence against overclaiming step-function reasoning improvements from contaminated score gains.

A careful paper phrasing would be:

> In contaminated preliminary runs, reframe agents often produced more structural explanations and mechanism-composition narratives. However, because those agents had access to prior control artifacts or shared benchmark state, their strongest apparent improvements cannot be attributed to the prompt intervention. A later clean comparison showed a more modest but still visible shift in search style, supporting the weaker claim that reframing changes the agent's search prior rather than granting a step-function reasoning capability.

Avoid saying:

> The reframe prompt caused the 0.69 result.

Avoid saying:

> The reframe prompt made the agent discover P2F3/hotwet independently.

Defensible claim:

> The reframe prompt appears to encourage structural hypothesis generation. Exp 01 and exp 02 contaminated runs show the kinds of structural narratives and mechanism families that emerge, but they cannot establish causal performance improvement because the candidate frontier was partially visible.

## Bottom line

Exp 01:

- Reasoning difference: yes.
- Clean causal attribution: no.
- Likely role of reframe: changed framing toward global structural limiters.
- Likely role of contamination: prevents confidence that the path was independent.

Exp 02:

- Reasoning difference: superficially yes, especially in narrative structure.
- Clean causal attribution: no.
- Likely role of reframe: helped organize/explain candidate mechanisms as structural analogies.
- Likely role of contamination: decisive for the high-ceiling path, because the agent could see P2F3/hotwet/loop13 artifact evidence.

Overall:

The contaminated experiments are useful precisely because they separate two phenomena:

1. Structural reasoning style can appear in reframe logs.
2. High score jumps can be created or amplified by leaked candidate-frontier information.

For the paper, these should support methodological caution, not headline performance claims.
