# Research Log

## 2026-05-13/14 — Setup and baseline verification

Read required files before any code changes: AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, models/C/formula.md, README.md.

Constraints understood:
- Allowed inputs only: dbar, annual precip, monthly precip, air temperature, monthly EDv3 GPP, existing masks/reference/evaluation assets.
- One global interpretable formula only.
- No latitude/longitude hacks, named-region routing, per-cell lookup tables, per-region formulas, arbitrary residual correction coefficients, or external model inputs.

Baseline verification:
- Command: `.venv/bin/python scripts/verify.py`
- Result: PASS, 24/24 files present, 24/24 hashes OK.

Official baseline global ILAMB:
- Command: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_ilamb.sh`
- Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, Overall 0.671529.

Official baseline regional ILAMB:
- Command: `ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" bash scripts/run_official_regions.sh`
- Weak regions by Overall: euro 0.361128, ceam 0.376153, tena 0.381473, mide 0.382769, seas 0.487193, shsa 0.507249, eqas 0.507395.

Initial failure interpretation:
- Model C has excellent seasonal phase globally and good boreal performance, but weak-region scores show low spatial scores and low bias/RMSE in several moderate-fire tropical/subtropical regions.
- The first research loop will test whether a unified fuel-continuity / wet-dry pulse mechanism can preserve the strong global seasonal score while improving regional spatial/bias behavior.

Structural analogy for loop 1:
- Fire occurrence resembles an outbreak/percolation system: fuel must be built and spatially/temporally connected, then exposed to drying/ignition. Like epidemics need both susceptible stock and contact structure, burned area needs both fuel continuity and a dry-season release. Model C has instantaneous GPP and precipitation controls, but lacks an explicit antecedent productivity/moisture-memory term.


## Research loops summary

### Loop 1 — Antecedent fuel / wet-dry pulse
Hypothesis: previous-season productivity creates connected fine fuel, released by drying and quenched by wet current months.
Searches:
- F1a_wetdry_pulse: 500 Optuna trials. Best internal candidate was baseline-equivalent with pulse_amp=0; no improvement.
- F1b_gpp_memory_replace: 500 Optuna trials. Replacing current GPP with antecedent GPP memory was slightly worse internally than baseline.
Decision: reject/prune. Model C's instantaneous monthly GPP hump already captures the useful fuel-seasonality signal under this scorer; extra memory/pulse complexity was not supported.

### Loop 2 — Annual precipitation combustion window
Hypothesis: annual precipitation should be a window, not only a fuel floor; high annual rainfall should suppress wet forests/poor curing.
Search:
- F2a_precip_window: 500 Optuna trials. Best internal simple score 0.660126, below baseline internal 0.672789.
Decision: reject as standalone formula. High-rainfall inhibition alone over-suppressed or traded off against useful savanna signal.

### Loop 3 — Missing global suppressors on fixed Model C core
Hypothesis: Model C overpredicts several weak regions because it lacks global wet-canopy inhibition and hyperarid fuel-discontinuity inhibition. A small cool-term was also tested.
Search:
- F3a_fixed_suppressors: 800 Optuna trials, fixed original Model C core plus wet/arid/cool suppressors.
- Best internal simple score 0.679074 vs baseline internal 0.672789.
Official global ILAMB (F3a): Overall 0.676544 vs baseline 0.671529.
Official regional ILAMB (F3a): weak-region bias/RMSE improved broadly; eqas improved strongly; some boreal/NHSA/BOAS spatial tradeoffs.
Decision: accept mechanism family as meaningful.

### Loop 3 ablations / pruning
Ablations run with official global ILAMB:
- No wet suppressor: Overall 0.6729.
- No arid suppressor: Overall 0.6753.
- No cool suppressor: Overall 0.676543, essentially identical to full F3a 0.676544.
Decision: prune cool suppressor. Final candidate F3b keeps wet and arid suppressors only (cool_amp=0).

### Loop 4 — Full retune of Model C core plus suppressors
Hypothesis: the accepted suppressors might permit a better retuned core.
Search:
- F4a_full_suppressor_retune: 1000 Optuna trials over 12 Model C parameters plus 10 suppressor parameters.
- Best internal candidate reverted to baseline-equivalent; no candidate beat fixed-core suppressor family.
Decision: reject. The broad 22-parameter space is harder and less defensible; preserving the already-validated Model C core and adding two interpretable limiters is more stable.

### Public benchmark
Final pruned candidate was run through public TRENDY/firepipe:
- Command: `TRENDY_BENCHMARK_ROOT=/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source PATH="$PWD/.venv/bin:$PATH" bash scripts/run_public_trendy_firepipe.sh`
- Caveat observed: JSBACH IndexError during pair run, but benchmark completed and score table was produced.
- Public score: ED-ModelC-formal-candidate Overall 0.676313, rank #1 in the produced table.
