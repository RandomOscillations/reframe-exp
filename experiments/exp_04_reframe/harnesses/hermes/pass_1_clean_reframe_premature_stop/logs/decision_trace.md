# Decision Trace

## D0 — Baseline first, no formula changes before reproduction

Observed failure/clue: The program requires reading all setup files and reproducing Model C before any modification. Initial `verify.py` showed generated artifact size differences but fixed inputs and params matched.

Hypothesis/decision: Treat original Model C as C0 incumbent and use locally reproduced official ILAMB as the run baseline, not README numbers or prior artifacts.

Alternatives considered: skip directly to optimization using README baseline; rejected because `BASELINE_REPRO.md` requires local reproduction and mismatch recording.

Command/evaluation run:
- `.venv/bin/python scripts/verify.py`
- `.venv/bin/python scripts/reproduce_modelC.py`
- `PATH="$PWD/.venv/bin:$PATH" ILAMB_ROOT="$PWD/ilamb" bash scripts/run_ilamb.sh`
- regional ILAMB with all built-in GFED/TRENDY regions.

Result:
- Official global baseline: Bias 0.7281, RMSE 0.5058, Seasonal 0.8457, Spatial 0.7724, Overall 0.6715.
- Regional components reveal weak spatial/magnitude behavior in Europe, Central America, Middle East, Temperate North America, Equatorial Asia, Southeast Asia, SH South America, while seasonal phase is often already strong.

Decision: Accept C0 as incumbent. Continue to regional diagnostic and global mechanism families aimed at spatial/magnitude allocation, not merely global Overall.

Implication for next loop: Look for one global, input-derived mechanism that suppresses or reshapes fire in weak humid/fragmented/agricultural/low-continuity regimes without degrading savanna Africa and boreal strengths. Structural analogy: current Model C is a simple series circuit of necessary gates; failures suggest the circuit lacks a “continuity/containment fuse” that trips in regions where climate/productivity can support fire but landscape/fuel continuity inferred from climate/productivity does not support large burned area.


## D1 — Try a wetness/firebreak fuse after weak-region spatial failures

Observed failure/clue: Europe, Central America, Middle East, Temperate North America, Equatorial Asia, Southeast Asia, and SH South America had weak spatial/magnitude components while seasonal timing was often good.

Hypothesis: Model C lacks a global high-wetness/fuel-continuity suppressor. Structural analogy: a circuit can have all upstream gates open but still be stopped by a fuse; humid/productive/fragmented regimes may need a spread-continuity fuse inferred from annual precipitation.

Alternatives considered: direct regional correction or named fire-type routing; rejected as forbidden. External landcover/cropland input; rejected by fixed input contract.

Command/evaluation run: `wet_firebreak`, 500 Optuna trials, regional objective; official global/regional ILAMB.

Result: Regional weak means improved, but official global Spatial fell to 0.5169 and Overall to 0.6185.

Decision: Reject. The mechanism is plausible but too blunt with annual precipitation alone.

Implication: Need a mechanism that distinguishes humid low-fire regions from high-fire productive savannas without suppressing boreal/savanna spatial structure.

## D2 — Try asymmetric GPP dose-response

Observed failure/clue: Wet firebreak over-suppressed spatial structure. GPP might encode fuel amount and humid closure more directly than annual precipitation.

Hypothesis: Replace the Model C GPP hump with separately tunable low-fuel onset and high-productivity closure, analogous to a pharmacological dose-response with toxicity at high dose.

Alternatives considered: adding landcover/cropland state; forbidden. Keeping Model C GPP hump and adding arbitrary residual factor; rejected as non-mechanistic.

Command/evaluation run: `gpp_asym`, 500 Optuna trials, regional objective; official global/regional ILAMB.

Result: Official RMSE improved to 0.5164 and seasonal stayed high at 0.8431, but Spatial fell to 0.6103 and Overall to 0.6417.

Decision: Reject/demote. GPP-only closure cannot cleanly separate weak humid regions from productive fire regimes under this input contract.

Implication: Try seasonal curing/precipitation timing rather than static annual/productivity suppression.

## D3 — Try dbar-buffered monthly curing

Observed failure/clue: Australia seasonal weakness and weak-region magnitude failures suggest monthly precipitation dampening may be too absolute. A wet month during accumulated dry deficit should have a different effect than the same rain in a wet regime.

Hypothesis: Replace absolute monthly precipitation dampening with rain divided by a dbar buffer: `P_month / (1 + Dbar/buffer)^q`. Structural analogy: a queue/bottleneck system where backlog changes the effect of new arrivals; accumulated deficit changes the extinguishing power of rainfall.

Alternatives considered: explicit lagged precipitation memories beyond dbar; dbar already encodes allowed dry-memory, so use it rather than adding opaque lag coefficients.

Command/evaluation run:
- C3: 500 Optuna trials with regional objective.
- C4: 700 Optuna trials with global objective.
- Official global/regional ILAMB for both.
- Clean public TRENDY/firepipe for C4.

Result:
- C3 improved weak-region means but collapsed official global Spatial to 0.3014 and Overall to 0.5698.
- C4 produced the best non-baseline global tradeoff: Bias 0.7295, Spatial 0.7822, but RMSE 0.4992, Seasonal 0.8386, Overall 0.6697, below C0 Overall 0.6715.
- C4 public Overall 0.669487, behind regenerated C0 0.671274 and setup public baseline 0.675085, but ahead of CLASSIC.
- C4 dry-buffer exponent optimized to 0.0559, close to neutral, which is an ablation-like signal that the extra mechanism has little useful global leverage once official fit is protected.

Decision: Demote C4, reject C3. Keep C0 as final recommended model.

Implication: The empirical ceiling under the fixed inputs appears reached for simple global wetness/productivity/curing additions. Remaining failures likely require information not present in the fixed contract (landcover/cropland, human fragmentation/ignitions/suppression, lightning, fuel load/biomass structure), or a more expressive mechanistic term that current searches did not reveal without degrading global behavior.
