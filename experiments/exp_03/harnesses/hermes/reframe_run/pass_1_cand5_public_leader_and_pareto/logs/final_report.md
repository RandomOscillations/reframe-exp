# Final Report: Model C constrained fire-model continuation

Rewritten: 2026-05-19 01:26:21

## Executive conclusion

This continuation found a new clean-public/global score leader and, separately, a more balanced regional Pareto candidate, but still did not find a single model that cleanly dominates every prior best on both global/public score and all important regional behavior.

Best-by-use-case after this cycle:

| Use case | Model | Evidence | Caveat |
|---|---|---|---|
| Clean public/global leaderboard | `ED-Cand5Abl-no_edge_mix` | Official diagnostic 0.688648; clean public Overall 0.679633, rank #1. | Improves only 8/14 named regions vs Cand3; edge repair is pruned, so NHSA/SHSA are not fully recovered. |
| Best balanced global+regional Pareto compromise | `ED-Cand5Sweep-edgefrac_0p50` | Official diagnostic 0.688490; clean public Overall 0.679346; improves 12/14 regions vs Model C and 11/14 vs Cand3. | Still below `ED-Cand4Abl-no_hotboost`/`ED-Cand5Abl-no_edge_mix` globally and publicly; BONA remains worse than Model C/Cand3. |
| Strongest broad weak-region repair | `ED-Cand5-mosaic_edge_release` | Improves 13/14 regions vs Model C and 10/14 vs Cand3; repairs NHSA/SHSA/SEAS/CEAM/EURO. | Global/public lower than the pruned no-edge and Cand4Abl candidates; BONA/African-belt tradeoff. |

The previous split has shifted: `ED-Cand4Abl-no_hotboost` is no longer the public/global leader because `ED-Cand5Abl-no_edge_mix` reaches public Overall 0.679633. The previous broad-regional candidate `ED-Cand3-release_window_wetcap` is also no longer the best regional compromise by simple regional-improvement counts, because `ED-Cand5Sweep-edgefrac_0p50` improves 11/14 named regions versus Cand3 while retaining a higher global diagnostic and public score. However, the aspirational target remains only partially met: the remaining BONA/strong-belt and NHSA/SHSA tradeoffs form a visible Pareto frontier.

## Files and constraints re-read before this continuation

Before modifying code or parameters, I re-read: `AGENTS.md`, `program.md`, `WORKSPACE_MANIFEST.md`, `BASELINE_REPRO.md`, `research_log.md`, `eval_log.md`, `regional_analysis.md`, `candidate_registry.md`, `constraint_checks.md`, `final_report.md`, plus `README.md`, `WRITEUP.md`, and `models/C/formula.md`. I also loaded the constrained-model-improvement workflow skill.

Constraints maintained:
- one global formula only;
- fixed input contract: dbar, annual/monthly precipitation, air temperature, monthly GPP and transformations of those fields;
- no external runtime inputs, latitude/longitude hacks, named-region routing, per-cell lookup tables, residual maps, per-region formulas, or direct cell-identity fitting;
- GFED/public benchmark data used only for screening and evaluation.

## Failure learning carried forward

From the previous cycle:
- `ED-Cand4Abl-no_hotboost` won global/public score but degraded NHSA/SHSA/SEAS/CEAM/TENA mostly through regional Spatial/Seasonal losses.
- `ED-Cand3-release_window_wetcap` remained more regional than Cand4Abl but had lower public/global score and BONA/NHSA caveats.
- Dual-corridor mechanisms repaired weak regions but hurt BONA/African strong belts.
- Senescence mechanisms repaired some humid/temperate regions but lost strong-belt fidelity.
- Hotboost and month-to-month dbar drydown were pruned; blunt wet suppression hurt global Spatial.

The next hypotheses therefore targeted not another generic boost, but the specific handoff between wet-season fuel charging, dry-season rain breaks, live-fuel senescence, hyperarid limits, and wet-canopy caps.

## Cycle-5 mechanisms explored

Script: `scripts/explore_cycle5_mechanisms.py`, 500 Optuna trials per family.

| Family | Structural analogy | Physical test | Official outcome |
|---|---|---|---|
| `monsoon_break_release` | Supply-chain handoff / F1 pit-stop: all stations must align. | Wet/productive fuel charging only matters if a rain-free break and curing follow. | Diagnostic 0.685937; strong regional repair, lower global. |
| `mosaic_edge_release` | Fire-line / forest-edge mosaic. | Wet productive cores stay capped, but humid-region dry edges become burnable when high fuel, rain hiatus, and senescence coincide. | Diagnostic 0.687870; best full regional repair. |
| `protected_corridor` | Power-grid protection. | Keep corridor/global terms but guard cold productive short-season cells and monsoon phase. | Diagnostic 0.687291; useful but dominated by mosaic/sweep candidates. |

## Official global ILAMB diagnostic comparison

| Model | Bias | RMSE | Seasonal | Spatial | Diagnostic |
|---|---:|---:|---:|---:|---:|
| ED-ModelC-final | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.680956 |
| ED-Cand3-release_window_wetcap | 0.731876 | 0.509663 | 0.852544 | 0.789014 | 0.687439 |
| ED-Cand4Abl-no_hotboost | 0.735210 | 0.511005 | 0.846055 | 0.795285 | 0.688962 |
| ED-Cand5Abl-no_edge_mix | 0.732520 | 0.511578 | 0.853499 | 0.790195 | 0.688648 |
| ED-Cand5Sweep-edgefrac_0p50 | 0.733009 | 0.511882 | 0.853270 | 0.787890 | 0.688490 |
| ED-Cand5-mosaic_edge_release | 0.733281 | 0.512082 | 0.853194 | 0.783297 | 0.687870 |
| ED-Cand5-monsoon_break_release | 0.731848 | 0.510109 | 0.847982 | 0.783724 | 0.685937 |
| ED-Cand5-protected_corridor | 0.732924 | 0.511487 | 0.850344 | 0.784580 | 0.687291 |

## Official regional comparison for balanced candidate

`ED-Cand5Sweep-edgefrac_0p50` is the best balanced compromise: it gives up only 0.000472 diagnostic global versus Cand4Abl, beats Cand3 by 0.001051, and improves 11/14 named regions versus Cand3.

| Region | Diagnostic | Delta vs Model C | Delta vs Cand3 | Delta vs Cand4Abl |
|---|---:|---:|---:|---:|
| global | 0.688490 | +0.007534 | +0.001051 | -0.000471 |
| bona | 0.787193 | -0.018309 | -0.006312 | -0.005963 |
| tena | 0.412644 | +0.021904 | +0.008714 | +0.015503 |
| ceam | 0.379557 | +0.018282 | +0.010704 | +0.018780 |
| nhsa | 0.586348 | -0.002074 | +0.000843 | +0.022128 |
| shsa | 0.501834 | +0.000278 | -0.005881 | +0.019011 |
| euro | 0.403252 | +0.036737 | +0.015649 | +0.030017 |
| mide | 0.396184 | +0.004429 | +0.000825 | -0.001610 |
| nhaf | 0.684979 | +0.018544 | +0.000024 | -0.000835 |
| shaf | 0.682536 | +0.017003 | +0.001474 | -0.013242 |
| boas | 0.758680 | +0.011277 | +0.002005 | -0.000364 |
| ceas | 0.697440 | +0.008132 | +0.001898 | +0.004125 |
| seas | 0.506124 | +0.017434 | +0.008546 | +0.019591 |
| eqas | 0.552770 | +0.050419 | +0.022535 | +0.002272 |
| aust | 0.686633 | +0.003846 | -0.000921 | +0.001431 |

## Public TRENDY/firepipe comparison

Clean public output for the new public leader: `public_benchmark_clean/ilamb/output_with_ED-Cand5Abl-no_edge_mix/scalar_database.csv`.

| Rank | Model | Public Overall |
|---:|---|---:|
| 1 | ED-Cand5Abl-no_edge_mix | 0.679633 |
| 2 | ED-Cand4Abl-no_hotboost | 0.679480 |
| 3 | ED-Cand4-pareto_guarded_corridor | 0.679479 |
| 4 | ED-Cand5-mosaic_edge_release | 0.678548 |
| 5 | ED-Cand3-release_window_wetcap | 0.678312 |
| 6 | ED-Cand2Abl-no_drydown | 0.677726 |
| 7 | ED-Cand2-curing_window | 0.677232 |
| 8 | ED-Cand5-monsoon_break_release | 0.676513 |
| 9 | ED-ModelC-baseline | 0.675085 |
| 10 | ED-ModelC-current | 0.671274 |
| 11 | ED-Cand-PartialWetSupp | 0.669258 |
| 12 | CLASSIC | 0.666048 |

Additional public scores:
- `ED-Cand5Sweep-edgefrac_0p50`: 0.679346.
- `ED-Cand5-mosaic_edge_release`: 0.678548.
- `ED-Cand5-monsoon_break_release`: 0.676513.
- Known JSBACH IndexError caveat persisted, as in prior public runs; scalar post-processing completed.

## Ablations and deterministic Pareto sweep

Ablation script: `scripts/ablate_mosaic_edge_release.py`.
Sweep script: `scripts/sweep_mosaic_edge_mix.py`.

| Model | Bias | RMSE | Seasonal | Spatial | Diagnostic |
|---|---:|---:|---:|---:|---:|
| ED-Cand5-mosaic_edge_release | 0.733281 | 0.512082 | 0.853194 | 0.783297 | 0.687870 |
| ED-Cand5Abl-no_edge_mix | 0.732520 | 0.511578 | 0.853499 | 0.790195 | 0.688648 |
| ED-Cand5Abl-no_cap_relief | 0.733284 | 0.512084 | 0.853194 | 0.783295 | 0.687871 |
| ED-Cand5Abl-no_arid | 0.731478 | 0.510680 | 0.853226 | 0.782734 | 0.686713 |
| ED-Cand5Abl-no_cold_guard | 0.731396 | 0.510507 | 0.853362 | 0.789733 | 0.687817 |
| ED-Cand5Sweep-edgefrac_0p50 | 0.733009 | 0.511882 | 0.853270 | 0.787890 | 0.688490 |

Interpretation:
- `no_cap_relief` is effectively identical to full mosaic, so cap-relief complexity is not needed.
- `no_edge_mix` improves global/public score and becomes the public leader, but sacrifices part of the NHSA/SHSA/SEAS recovery.
- Removing the arid term lowers global score, supporting the hyperarid fuel-continuity mechanism.
- Removing the cold guard recovers BONA but damages NHSA/SHSA/SEAS and does not beat no-edge globally.
- Edge-mix sweep exposes a real Pareto knob: 0.0 is public/global best, 1.0 is regional-repair best, and 0.5 is the strongest balanced compromise.

## Mechanistic interpretation of the best candidates

`ED-Cand5Abl-no_edge_mix` is best for leaderboard score. It keeps the release-window/corridor machinery and protective guards, but the explicit mosaic-edge replacement is pruned. Its result says that some edge complexity sounds plausible but, under public/global scoring, the data prefer a simpler release/corridor expression.

`ED-Cand5Sweep-edgefrac_0p50` is the scientifically more interesting compromise. The half-strength edge term acts like a controlled valve: it reintroduces humid/monsoon edge burning enough to repair NHSA, SHSA, SEAS, CEAM, and EURO relative to Cand4Abl/Cand3, while not fully paying the global/strong-belt cost of the full mosaic edge.

`ED-Cand5-mosaic_edge_release` is the strongest regional repair signal. It supports the fire-line/forest-edge hypothesis: wet productive regions cannot be represented by a single wet cap; some cells/months behave like dry edges after rain breaks and live-fuel senescence. But the same mechanism degrades BONA and African strong-belt fidelity, so it is not a clean global replacement.

## Why the remaining failures still appear unresolved under the fixed contract

The continuation improved the Pareto frontier but did not remove it. The allowed fields can infer broad fuel, wetness, dry-season, productivity, temperature, and hyperarid regimes. They cannot directly encode land-use, cropland/forest mosaics, ignition sources, suppression, fragmentation, peat/soil constraints, canopy structure, livestock/grazing, or management. The new edge-mix sweep shows the identifiability limit: increasing the edge mechanism repairs humid/monsoon weak regions but progressively loses global/public and BONA/Africa fidelity. Decreasing it recovers global/public but leaves NHSA/SHSA/SEAS less repaired.

## Reproducibility artifacts

- Cycle-5 search script: `scripts/explore_cycle5_mechanisms.py`.
- Mosaic ablation script: `scripts/ablate_mosaic_edge_release.py`.
- Edge-mix sweep script: `scripts/sweep_mosaic_edge_mix.py`.
- Public/global leader artifact: `ilamb/MODELS/ED-Cand5Abl-no_edge_mix/burntArea.nc`.
- Public/global leader formula summary: `models/explore5/mosaic_edge_release_ablation/no_edge_mix/formula.md`.
- Balanced Pareto artifact: `ilamb/MODELS/ED-Cand5Sweep-edgefrac_0p50/burntArea.nc`.
- Balanced Pareto formula summary: `models/explore5/mosaic_edge_mix_sweep/edgefrac_0p50/formula.md`.
- Regional-repair artifact: `ilamb/MODELS/ED-Cand5-mosaic_edge_release/burntArea.nc`.
- Regional-repair formula summary: `models/explore5/mosaic_edge_release/formula.md`.
- Official cycle-5 regional output: `ilamb/output_cand5_regions/scalar_database.csv`.
- Official cycle-5 ablation output: `ilamb/output_cand5_ablation_regions/scalar_database.csv`.
- Official edge-sweep output: `ilamb/output_cand5_edge_sweep_regions/scalar_database.csv`.
- Public outputs: `public_benchmark_clean/ilamb/output_with_ED-Cand5Abl-no_edge_mix/scalar_database.csv`, `public_benchmark_clean/ilamb/output_with_ED-Cand5Sweep-edgefrac_0p50/scalar_database.csv`, `public_benchmark_clean/ilamb/output_with_ED-Cand5-mosaic_edge_release/scalar_database.csv`.

## Final accept/reject decision

I do not claim that a single model fully satisfies the aspirational target of a step-function improvement with no regional caveats. The continuation did, however, materially improve the evidence frontier:

1. New public/global leader: `ED-Cand5Abl-no_edge_mix`, public Overall 0.679633.
2. New best balanced regional/global compromise: `ED-Cand5Sweep-edgefrac_0p50`, official diagnostic 0.688490, public 0.679346, and 11/14 regional improvements versus Cand3.
3. Strongest regional repair mechanism: `ED-Cand5-mosaic_edge_release`, supporting the monsoon/edge-fire hypothesis but with strong-belt tradeoffs.

Recommended handling: preserve all three as best-by-use-case candidates. If the deployment criterion is public/global rank, use `ED-Cand5Abl-no_edge_mix`. If the scientific criterion is the best single unified compromise across global score and named regional behavior, use `ED-Cand5Sweep-edgefrac_0p50`. Do not present either as eliminating all regional failure modes; the remaining BONA/strong-belt versus humid/monsoon repair tradeoff appears unresolved under the current fixed input contract.
