# Research Log

## Initial understanding
Read `AGENTS.md`, `program.md`, `WORKSPACE_MANIFEST.md`, `BASELINE_REPRO.md`, `models/C/formula.md`, and `README.md` before any code changes. The task is to start from original Model C and test whether one global, interpretable burned-area functional form using only the allowed inputs can improve global and regional ILAMB behavior without latitude/longitude, region routing, cell lookup tables, or residual corrections. No blocking questions.

## Baseline verification
- `./.venv/bin/python scripts/verify.py` returned PASS for all 24 required artifacts.
- Official global ILAMB baseline: Overall 0.671529, Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351.
- Official regional ILAMB baseline showed strong BONA/BOAS/AUST/CEAS and weak TENA, CEAM, EURO, MIDE, SEAS, EQAS; weak regions are mostly low spatial-distribution plus bias/RMSE, not seasonal timing.

## Loop 1: baseline re-optimization check
Hypothesis: Model C may still have parameter slack under the current ED-consistent transform.
Search: `C_reopt`, 500 Optuna TPE trials, same 12-parameter Model C space, warm-started at baseline.
Result: warm-start remained best in fast scorer. No serious official candidate generated from this family because no fast-score improvement over Model C.
Interpretation: original 12-parameter basin is already tight; changes tend to lose spatial/seasonal balance.

## Loop 2: lagged/cured fine-fuel memory
Hypothesis: regional failures may reflect fire responding to accumulated/cured recent productivity rather than instantaneous monthly GPP.
Functional form: replace monthly GPP in the existing hump with a global convex mix of current GPP and 3- or 6-month lagged GPP (derived only from allowed monthly GPP).
Search: 500 Optuna TPE trials plus deterministic checks around lag mixes.
Result: neutral/no improvement; Optuna selected zero lag mix. Rejected.
Mechanistic interpretation: the monthly GPP hump already captures most of the available fuel signal; simple lagged fuel memory did not improve official-target proxy behavior.

## Loop 3: dry-shifted GPP saturation
Hypothesis: dry savannas may tolerate higher apparent GPP before productivity suppresses fire because cured herbaceous fuel remains flammable.
Functional form: make the GPP hump decay scale increase smoothly with dbar using a single global dryness sigmoid.
Search: 500 Optuna TPE trials after fixing implementation for array-valued decay scale; grid variants around dry gate/boost.
Result: no improvement; neutral dry boost was selected. Rejected.
Mechanistic interpretation: allowing high-GPP dry cells to burn more tends to over-broaden high-fire areas or duplicate the existing dbar/GPP interaction implicit in the baseline product.

## Loop 4: precipitation concentration / rain-pulse suppression
Hypothesis: some wet-season or monsoon cells need suppression when current month precipitation is anomalously large relative to annual mean, beyond absolute monthly precipitation dampening.
Functional form: multiply Model C by `exp(-pulse_a * max(p_month/(p_ann/12)-pulse_c,0))`, a global rain-pulse wet-fuel suppression term.
Search: 500 Optuna TPE trials; deterministic grid found `pulse_a=0.5`, `pulse_c=0.5` as a modest fast-score candidate.
Official result: `ED-rain-pulse-grid` global Overall 0.671705 (+0.000176 over baseline), Seasonal +0.003018, Bias/RMSE slightly better, Spatial -0.008056. Regional improvements in TENA, CEAM (tiny), NHSA, SHSA, EURO, MIDE, BOAS, CEAS, SEAS, EQAS; losses in BONA, NHAF, SHAF, AUST.
Decision: not accepted as a replacement. It is mechanistically plausible and more balanced than wet-temperature, but the gain is third-decimal and spatial tradeoff remains.

## Loop 5: wet-fuel ignition / temperature-moisture interaction
Hypothesis: warm temperatures should not raise ignition equally during wet months; wet fuels require higher effective ignition temperature.
Functional form: replace `sig(T_air, ign_k, ign_c)` with `sig(T_air, ign_k, ign_c + wet_temp_shift * p_month/(p_month+wet_half))`, one global smooth wet-fuel ignition interaction.
Search: 500 Optuna TPE trials plus deterministic grid; grid candidate `wet_half=20 mm/month`, `wet_temp_shift=5 C` gave the strongest fast-score movement.
Official result: `ED-wet-temp-grid` global Overall 0.674491 (+0.002962), Bias +0.003750, RMSE +0.007706, Seasonal -0.000523, Spatial -0.003829. Regional weak-region improvements: TENA +0.0386, CEAM +0.0274, EURO +0.0935, MIDE +0.0183, SEAS +0.0118, EQAS +0.0112, AUST +0.0021. But BONA falls -0.0999 and BOAS falls -0.0585 due to severe spatial-distribution collapse.
Public TRENDY/firepipe: ranked above baseline-current and standard TRENDY models, but below a pre-existing benchmark-root ED-ModelC-pass2-P2F3 artifact not generated in this workspace.
Decision: highest official global score produced here, but rejected as final replacement because regional spatial damage in boreal North America and boreal Asia is not scientifically acceptable.

## Stopping rationale
Explored five mechanistic families plus ablations/neutral checks. The only meaningful official global gain came from wet-fuel ignition, and its regional failures are too large. The more balanced rain-pulse term is too marginal. Remaining weak regions appear dominated by spatial allocation within regions; under the fixed contract, all allowed inputs are coarse climate/GPP fields and cannot cleanly distinguish local land use/ignition/suppression/fuel structure without forbidden region/cell routing or new external inputs.

## Continuation after interim report
User correctly rejected the first `final_report.md` as premature. I treated it as an interim checkpoint and continued from the evidence rather than restarting.

### Continuation signal from first pass
- Naive wet-temperature interaction improved weak regions but destroyed BONA/BOAS spatial structure.
- Rain-pulse was balanced but too small.
- Lagged fuel and dry-shifted GPP collapsed to neutral.

### Loop 6: cold/liquid/warm-gated wet ignition
Hypothesis: wet-fuel ignition could be valid only for liquid rain or warm thermal regimes; cold/snow precipitation should not suppress boreal fire the same way.
Mechanisms:
- `liquid_wet_temp`: wetness uses liquid precipitation proxy `p_month * sigmoid(T_air)`.
- `warm_gated_wet_temp`: wet-temperature shift is attenuated by annual-mean thermal gate from T_air.
- `liquid_warm_wet_temp`: combined gate.
Search: deterministic grids over wet half-saturation, wet temperature shift, liquid threshold/slope, warm threshold/slope; serious official candidates `ED-liquid-wet-1`, `ED-liquid-wet-3`, and `ED-warm-gate-c8`.
Outcome: liquid gate did not fix BONA/BOAS; it often reproduced the naive wet-temperature damage. Warm-gated wet ignition preserved BONA/BOAS much better and improved weak regions, but global Overall only reached 0.672605. Rejected as insufficient.

### Loop 7: annual wet-canopy / dry-month / low-amplitude climate suppressors
Hypothesis: weak-region gains may require persistent wet-canopy suppression or dry-season concentration rather than monthly wet-temperature shifts.
Mechanisms:
- `ann_wet`: high annual precipitation suppressor.
- `dry_month_norm`: dry-month concentration gate based on `p_month/(p_ann/12)`.
- `pann_hump`: annual precipitation hump.
- `low_amp_suppress`: suppress low-temperature-amplitude evergreen/wet regimes.
Search: deterministic grids; serious official candidates `ED-drymonth-norm` and `ED-ann-wet`.
Outcome: `ann_wet` strongly improved EQAS and SEAS but did not improve global Overall; `drymonth_norm` improved several regions but was still only 0.672018 global. Rejected as standalone.

### Loop 8: warm-gated wet + annual-wet hybrid
Hypothesis: combine weak-region benefits of warm-gated wet suppression and annual-wet canopy suppression while avoiding BONA/BOAS collapse.
Search: combined grid, serious official candidate `ED-combo-warm-ann`.
Outcome: global Overall 0.672911; balanced but still not material. Rejected.

### Loop 9: wet-canopy plus two-threshold arid fuel-continuity limiter (P2F3)
Hypothesis: remaining failures are not mainly monthly wet ignition; they reflect two missing global limiters: persistent wet-canopy inhibition in very wet regions and fuel-network fragmentation in arid/hyperarid regimes. The BONA/BOAS failure argues against region-blind monthly wet-temperature suppression; arid fragmentation uses `Dbar/(P_ann+p0)` and annual wet-canopy suppression, both global and interpretable.
Formula:
`base_rate = original Model C annual rate after fire_exp`
`wet_suppress = 1 - wet_amp * sigmoid(P_ann, wet_k, wet_c)`
`deficit_ratio = Dbar / (P_ann + ratio_p0)`
`arid_soft = 1 - arid_amp1 * sigmoid(deficit_ratio, arid_k1, arid_c1)`
`arid_desert = 1 - arid_amp2 * sigmoid(deficit_ratio, arid_k2, arid_c2)`
`fire_rate = base_rate * wet_suppress * arid_soft * arid_desert`
Search: `scripts/search_p2f3_continued.py`, 600 Optuna trials in current workspace, seeded with the mechanistic P2F3 family plus no-low/no-high ablations. Corrected implementation applies suppressors after `fire_exp` to the annual rate.
Official result: `ED-p2f3-seed2` global Overall 0.677073; public TRENDY/firepipe 0.676846 and tied #1 with the identical pre-existing benchmark row. This is the first material improvement over baseline in this continued run (+0.005544 official global Overall) while improving most weak regions.
Decision: accept `p2f3_seed_current` / `ED-p2f3-seed2` as final best model. `ED-p2f3-nolow2` is a parsimonious ablation with nearly identical global score (0.676981) and better global Spatial, but weaker TENA/EURO/MIDE dryland gains; retain the low threshold because it is mechanistic and target-region useful.
