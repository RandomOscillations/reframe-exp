# Final Report: Model C constrained fire-model continuation

Rewritten: 2026-05-19 00:04:18

## Executive conclusion

The continuation found a new global/public score leader, but not an unambiguous regional-behavior replacement for the previous best model.

- Best global/public score candidate: `ED-Cand4Abl-no_hotboost`, the pruned Pareto guarded-corridor model.
  - Official diagnostic global: 0.688962 versus `ED-Cand3-release_window_wetcap` 0.687439 and original `ED-ModelC-final` 0.680956.
  - Clean public Overall: 0.679480, rank #1 in the clean public run, just ahead of full Pareto guarded 0.679479 and Cand3 0.678312.
- Best broad regional-behavior candidate remains `ED-Cand3-release_window_wetcap`.
  - Cand3 improves 12/14 named non-global regions versus original Model C in the previously completed official diagnostic.
  - Cand4Abl improves 9/14 named non-global regions versus original Model C and only 5/14 versus Cand3.
- Therefore, the scientifically defensible endpoint is split:
  - If the objective is global/public benchmark rank, use `ED-Cand4Abl-no_hotboost` with explicit regional caveats.
  - If the objective is a unified model with the best broad regional behavior, keep `ED-Cand3-release_window_wetcap` as the safer recommendation.

The requested step-function improvement in both global ILAMB and regional behavior was not found. The empirical ceiling under the fixed input contract appears to be a Pareto frontier: small global/public gains can be bought by damaging NHSA/SHSA/SEAS/CEAM/TENA relative to Cand3, while broad regional repair mechanisms tend to give back global Spatial or strong fire-belt fidelity.

## Files and constraints re-read before continuation

Before modifying or evaluating new candidates, the run re-read `AGENTS.md`, `program.md`, `WORKSPACE_MANIFEST.md`, `BASELINE_REPRO.md`, `research_log.md`, `eval_log.md`, `regional_analysis.md`, `candidate_registry.md`, `constraint_checks.md`, `final_report.md`, plus `README.md`, `WRITEUP.md`, and `models/C/formula.md`.

Constraints maintained:
- one global formula only;
- fixed input contract: dbar, annual/monthly precipitation, air temperature, monthly GPP and transforms of those fields;
- no external runtime inputs, latitude/longitude hacks, named-region routing, per-cell lookup tables, residual maps, or direct cell-identity fitting;
- GFED/public benchmark data used only for screening/evaluation.

## Prior-cycle failure learning carried forward

- Blunt wet suppression repaired some weak wet/temperate regions but collapsed global Spatial.
- Fuel charging alone and wet/fuel releases damaged strong African/boreal fire belts.
- Month-to-month dbar drydown was pruned in prior ablation; the useful signal was a release window, not drydown itself.
- The previous best, Cand3, used dry/intermediate-precip/intermediate-GPP release plus soft wet/low-deficit cap, but still degraded BONA and NHSA slightly.

## New mechanism families explored

Third-cycle families in `scripts/explore_third_order_candidates.py`:

| Family | Analogy / physical hypothesis | Screening outcome | Official outcome |
|---|---|---|---|
| `guarded_release` | Relay-protection grid: attenuate release in cold, short-warm-season productive climates. | Fast global 0.634411. | Diagnostic 0.685694; rejected. |
| `senescence_release` | Live-fuel curing/senescence: fire follows productivity drawdown rather than raw dbar derivative. | Fast global 0.635967. | Diagnostic 0.687211; near Cand3 but below it. |
| `dual_corridor_balance` | Combustion stoichiometry: suppress both hyperarid fuel absence and wet-canopy nonflammability. | Best weak-region repair, weak mean 0.364882. | Diagnostic 0.686084; rejected due BONA/Africa losses. |
| `warm_dry_supply_chain` | F1/supply-chain bottleneck: fuel, warmth, no recent rain, and dryness must align. | Fast global 0.635042. | Not promoted; less informative than other families. |

Pareto-refinement families in `scripts/explore_pareto_release_candidates.py`:

| Family | Purpose | Official outcome |
|---|---|---|
| `pareto_guarded_corridor` | Combine guarded release with arid/wet corridor after dual-corridor tradeoffs. | Diagnostic 0.688961; public 0.679479; superseded by no-hotboost ablation. |
| `pareto_senescence_corridor` | Combine senescence with corridor protection. | Diagnostic 0.687464; tiny global gain but worse regional tradeoff. |

## Official global ILAMB diagnostic comparison

| Model | Bias | RMSE | Seasonal | Spatial | Diagnostic |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.680956 |
| ED-Cand3-release_window_wetcap | 0.731876 | 0.509663 | 0.852544 | 0.789014 | 0.687439 |
| ED-Cand4-senescence_release | 0.732805 | 0.510670 | 0.850392 | 0.785921 | 0.687211 |
| ED-Cand4-dual_corridor_balance | 0.734554 | 0.510564 | 0.844058 | 0.782207 | 0.686084 |
| ED-Cand4-guarded_release | 0.731849 | 0.509435 | 0.846159 | 0.785437 | 0.685694 |
| ED-Cand4-pareto_guarded_corridor | 0.735210 | 0.511004 | 0.846055 | 0.795285 | 0.688961 |
| ED-Cand4-pareto_senescence_corridor | 0.731666 | 0.510260 | 0.849232 | 0.791698 | 0.687464 |
| ED-Cand4Abl-no_hotboost | 0.735210 | 0.511005 | 0.846055 | 0.795285 | 0.688962 |

The pruned no-hotboost ablation is the best global diagnostic result by a very small margin. Its gain over Cand3 is +0.001522 diagnostic points, driven mostly by Bias/RMSE/Spatial, while Seasonal is lower than Cand3.

## Official regional comparison for `ED-Cand4Abl-no_hotboost`

| Region | Cand4Abl diagnostic | Delta vs Model C | Delta vs Cand3 |
|---|---:|---:|---:|
| global | 0.688962 | +0.008005 | +0.001522 |
| bona | 0.793156 | -0.012346 | -0.000349 |
| tena | 0.397141 | +0.006401 | -0.006789 |
| ceam | 0.360777 | -0.000499 | -0.008076 |
| nhsa | 0.564220 | -0.024202 | -0.021285 |
| shsa | 0.482823 | -0.018733 | -0.024892 |
| euro | 0.373235 | +0.006720 | -0.014368 |
| mide | 0.397794 | +0.006039 | +0.002435 |
| nhaf | 0.685814 | +0.019379 | +0.000858 |
| shaf | 0.695778 | +0.030245 | +0.014717 |
| boas | 0.759044 | +0.011641 | +0.002369 |
| ceas | 0.693315 | +0.004008 | -0.002227 |
| seas | 0.486533 | -0.002156 | -0.011045 |
| eqas | 0.550498 | +0.048147 | +0.020263 |
| aust | 0.685202 | +0.002415 | -0.002353 |

Cand4Abl improves 9/14 named non-global regions over original Model C and 5/14 over Cand3.

Important regional tradeoffs:
- Improves strongly versus Model C in EQAS (+0.048147), SHAF (+0.030245), NHAF (+0.019379), BOAS (+0.011641), and modestly in TENA/EURO/MIDE/CEAS/AUST.
- Regresses versus Model C in NHSA (-0.024202), SHSA (-0.018733), SEAS (-0.002156), CEAM (-0.000499), and BONA (-0.012346).
- Versus Cand3 it improves EQAS, SHAF, NHAF, BOAS, and MIDE, but worsens NHSA, SHSA, EURO, SEAS, CEAM, TENA, CEAS, AUST, and BONA slightly.

## Clean public TRENDY/firepipe comparison

Clean public run: `public_benchmark_clean/ilamb/output_with_ED-Cand4Abl-no_hotboost/scalar_database.csv`.

| Rank | Model | Public Overall |
|---:|---|---:|
| 1 | ED-Cand4Abl-no_hotboost | 0.679480 |
| 2 | ED-Cand4-pareto_guarded_corridor | 0.679479 |
| 3 | ED-Cand3-release_window_wetcap | 0.678312 |
| 4 | ED-Cand2Abl-no_drydown | 0.677726 |
| 5 | ED-Cand2-curing_window | 0.677232 |
| 6 | ED-ModelC-baseline | 0.675085 |
| 7 | ED-ModelC-current | 0.671274 |
| 8 | ED-Cand-PartialWetSupp | 0.669258 |
| 9 | CLASSIC | 0.666048 |
| 10 | CLM6.0 | 0.660644 |
| 11 | CLM-FATES | 0.656831 |
| 12 | ELM-FATES | 0.656788 |

The public runs retained the known JSBACH IndexError caveat during model-confrontation, but post-processing completed and the same caveat existed in prior public comparisons.

## Ablation and complexity pruning

Ablation script: `scripts/ablate_pareto_guarded_corridor.py`.

| Variant | Official diagnostic global | Interpretation |
|---|---:|---|
| Full Pareto guarded corridor | 0.688961 | Reference full form. |
| Remove cold/short-season guard | 0.688355 | Small global loss; guard supports weak-region/global balance but removing it improves BONA/Africa. |
| Remove hyperarid corridor suppression | 0.683534 | Large loss; hyperarid fuel-limit term is necessary. |
| Remove hot-temperature boost | 0.688962 | Slightly best; hotboost is neutral and pruned. |
| Remove wet/low-deficit cap | 0.687848 | Clear loss; wet/low-deficit cap is useful. |

Pruned final/global formula: `models/explore4/pareto_guarded_corridor_pruned_no_hotboost/formula.md`.

## Mechanistic interpretation of the pruned global/public leader

`ED-Cand4Abl-no_hotboost` keeps:

- the successful release-window idea from Cand3: dry months in intermediate precipitation and intermediate GPP regimes get additional burned-area potential;
- a cold/short-season productive guard, analogous to a relay-protection circuit, to reduce over-activation in boreal-like cold productive systems without using regions or coordinates;
- a hyperarid fuel-continuity suppressor, representing the low-fuel end of the fire corridor;
- a wet/low-deficit cap, representing the wet-canopy/nonflammability end of the corridor.

The hot-temperature boost was removed because ablation showed it contributed no meaningful official/global improvement.

## Best models by use case

| Use case | Model | Evidence | Caveat |
|---|---|---|---|
| Global/public leaderboard | `ED-Cand4Abl-no_hotboost` | Official diagnostic 0.688962; clean public Overall 0.679480 rank #1. | Regional regressions in NHSA/SHSA/SEAS/CEAM/BONA; only 9/14 named regions improve over Model C. |
| Broad regional behavior | `ED-Cand3-release_window_wetcap` | Official diagnostic 0.687439; previously documented 12/14 named-region improvements over Model C; clean public 0.678312. | Slightly lower global/public score than Cand4Abl; BONA/NHSA caveats remain. |
| Mechanistic weak-region repair study | `ED-Cand4-dual_corridor_balance` | Strong repairs in EURO/EQAS/SHSA/NHSA/TENA versus Cand3. | Damages BONA/NHAF/SHAF and loses global score. |

## Why the remaining failures appear unresolved under the fixed contract

The continuation exposed a stable tradeoff. The allowed climate/productivity fields can distinguish broad dryness, productivity, temperature, wetness, and fuel-continuity regimes, but they do not directly encode land use, human ignitions/suppression, crop/grass/forest structure, peat/soil constraints, lightning, fragmentation, or management. The weak-region fixes that help EQAS/EURO/SHSA/NHSA tend to use the same intermediate-wet/intermediate-fuel corridors that also change strong fire belts and some tropical regions. Without forbidden region routing or new external predictors, the optimizer finds a Pareto frontier rather than a clean regional step-function.

## Reproducibility artifacts

- Third-cycle search script: `scripts/explore_third_order_candidates.py`
- Pareto search script: `scripts/explore_pareto_release_candidates.py`
- Ablation script: `scripts/ablate_pareto_guarded_corridor.py`
- Global/public leader artifact: `ilamb/MODELS/ED-Cand4Abl-no_hotboost/burntArea.nc`
- Global/public leader formula: `models/explore4/pareto_guarded_corridor_pruned_no_hotboost/formula.md`
- Global/public leader params/result: `models/explore4/pareto_guarded_corridor_pruned_no_hotboost/result.json`
- Official Pareto regional output: `ilamb/output_pareto_regions/scalar_database.csv`
- Official ablation regional output: `ilamb/output_pareto_ablation_regions/scalar_database.csv`
- Public output: `public_benchmark_clean/ilamb/output_with_ED-Cand4Abl-no_hotboost/scalar_database.csv`
- Previous broad-regional best: `ilamb/MODELS/ED-Cand3-release_window_wetcap/burntArea.nc` and `models/explore3/release_window_wetcap/formula.md`

## Final accept/reject decision

I do not claim a single model satisfies the full aspirational target of a step-function improvement in both official global ILAMB and regional behavior. The continuation found:

1. A new global/public leader: `ED-Cand4Abl-no_hotboost`.
2. A better broad-regional compromise remains: `ED-Cand3-release_window_wetcap`.
3. Mechanistically informative rejected families that demonstrate why the remaining residuals are hard under the fixed input contract.

Recommended final handling: preserve both `ED-Cand4Abl-no_hotboost` and `ED-Cand3-release_window_wetcap` as best-by-use-case candidates. Do not present Cand4Abl as a clean regional replacement for Cand3; present it as a pruned, mechanistic global/public benchmark improvement with explicit regional tradeoffs.

