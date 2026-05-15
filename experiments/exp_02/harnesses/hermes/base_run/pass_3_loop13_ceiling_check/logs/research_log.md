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
Official result: `ED-p2f3-seed2` global Overall 0.677073; public TRENDY/firepipe 0.676846 and tied #1 with the identical pre-existing benchmark row. This was the first material improvement over baseline in the continued run (+0.005544 official global Overall) while improving most weak regions.
Decision at that point: P2F3 became best-so-far, not endpoint. It preserved BOAS and improved most weak regions, but still had BONA spatial loss, AUST seasonal weakness, and low spatial skill in EURO/TENA/MIDE/CEAM.

### Loop 10: P2F3 failure triage and cold/low-arid relaxation
Hypothesis: P2F3 BONA spatial loss might come from over-applying the low/soft arid threshold or wet/arid suppressors in cold continental climates. A smooth T_air-derived cold/continental gate could relax P2F3 suppression without region routing.
Mechanisms:
- `low_arid_warm_gate`: attenuate the low arid threshold outside warm regimes.
- `cold_continental_relax`: restore a fraction of P2F3-suppressed rate in cold, high-temperature-amplitude climates.
Search: `scripts/search_p2f3_next.py`, 500 Optuna trials for each family.
Result: low-arid warm gate collapsed nearly to identity (`floor=0.9867`) and was rejected. Cold-continental relax slightly recovered BONA/BOAS but official global was 0.676930, below P2F3; rejected as insufficient.

### Loop 11: drying/curing phase enhancement on top of P2F3
Hypothesis: P2F3 fixes structural wet/arid overprediction but misses within-year fire-season amplification when fuels are actively drying. This should affect AUST seasonality and savanna/grass fire regions through allowed dbar tendency, precipitation concentration, and T_air, not region labels.
Formula family:
`drying = sigmoid(delta_Dbar, drying_k, drying_c)`
`drymonth = 1 / (1 + (p_month/(p_ann/12) / pconc_half)^pconc_pow)`
`warm = sigmoid(T_air, temp_k, temp_c)`
`fire_rate = P2F3_rate * (1 + cure_amp * drying * drymonth * warm)`
Search: 500 Optuna trials (`next_curing_phase_opt500`) plus deterministic amplitude scaling.
Official result: full curing phase `ED-next-curing` reached global Overall 0.684534, a major step over P2F3, with global Spatial 0.797406 and AUST 0.678597. Scaling showed monotonic global improvement through about 1.25x (`ED-next-curing-scale-1p25` global 0.684994) while preserving BONA/BOAS. Tradeoff: P2F3's dryland/wet weak-region gains partly eroded in TENA/CEAM/EURO/MIDE/SEAS/EQAS.
Decision: accept as a serious mechanistic improvement family but continue, because it improved global/AUST/spatial while compromising some P2F3 weak-region gains.

### Loop 12: curing plus warm/hot wet-month compensation
Hypothesis: the curing enhancement over-burns some warm wet or transition regimes. Add a separate wet-month compensation term based on precipitation concentration, but gate it by warm climatology to avoid repeating the BONA/BOAS collapse from naive wet-temperature suppression.
Formula family:
`fire_rate = P2F3_rate * (1 + curing_enhancement) * (1 - wet_amp * wetmonth * warm_climate_gate)`
where all components use allowed P/T/Dbar-derived variables.
Search: `scripts/search_p2f3_curing_refine.py`, 700 Optuna trials, plus deterministic hot/warm-gated grids.
Official results:
- `ED-next-curing-warmwet-nowarmgate`: highest official global Overall 0.688603 and public 0.688384, but BONA 0.702599 and BOAS 0.701577 due spatial damage. Rejected as final despite top scalar score.
- `ED-next-curing-hotwet-1`: official global Overall 0.687626; public TRENDY/firepipe 0.687405. BONA 0.769133 (only -0.002074 vs P2F3), BOAS 0.729333 (+0.000603), AUST 0.681726 (+0.013943), TENA 0.419723 (+0.005032), EURO 0.404197 (+0.018760), NHAF/SHAF large gains. Regressions vs P2F3 remain in CEAM, NHSA, SHSA, MIDE, SEAS, EQAS.
Decision: `ED-next-curing-hotwet-1` / `runs/candidates/p2f3_curing_hotwet_final/` became the best balanced continuation model at that point. It beat P2F3 globally and publicly by ~0.0106, improved global spatial/seasonal, fixed AUST materially, and avoided BONA/BOAS collapse. It did not dominate P2F3 region-by-region; P2F3 remained the broadest weak-region improvement model.

### Loop 13: post-hotwet arid/protection/attenuation search
Hypothesis: ED-next-curing-hotwet-1's remaining failures may reflect over-broad curing and wet-month compensation in specific physical regimes, not a need for regional routing. Three global mechanisms were tested: (1) cold/high-temperature-amplitude boreal protection for wet-month compensation, (2) arid-deficit attenuation of curing to recover MIDE/CEAM dryland behavior, and (3) wet/productive attenuation of curing to reduce South American/wet-tropical regressions.
Search: `scripts/search_hotwet_next.py`; 500 Optuna trials each for `boreal_protected_wetcomp`, `arid_curing_attenuation`, and `wet_productivity_curing_attenuation`; a 300-trial combined search after the multi-family run timed out; plus deterministic arid+boreal protection grids.
Official results:
- `ED-loop13-combined`: official global 0.690564, public 0.690353, but BONA 0.703762 and BOAS 0.701550. Rejected as scalar-leading but regionally damaging.
- `ED-loop13-aridatt`: official global 0.690378, public 0.690170, TENA/EURO/MIDE improved, but BONA 0.695631 and BOAS 0.693656. Rejected due renewed boreal collapse.
- `ED-loop13-aridboreal-5`: official global 0.690073, public 0.689864, boreal protection partially restored BONA/BOAS to 0.729587/0.720784, but still clearly below hotwet-1 BONA/BOAS and worsened AUST/CEAM/SEAS/EQAS. Rejected as not a balanced step.
- `ED-loop13-borealdiag`: official global 0.688133, close to hotwet-1 and with BOAS preserved, but BONA 0.751941 and gains were too small to count as a step.
Decision: no new accepted replacement. The loop established an empirical tradeoff: stronger arid attenuation and broad wet compensation can raise global/public scores to ~0.690 and improve TENA/EURO/MIDE, but they systematically buy that score by removing too much boreal fire and weakening AUST/wet-region balance. ED-next-curing-hotwet-1 remains the best balanced model; `ED-loop13-combined` is the highest scalar/public model but rejected.
