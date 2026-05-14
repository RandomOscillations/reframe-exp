# Research Log

## 2026-05-14 — initial understanding and baseline verification
Read AGENTS.md, program.md, WORKSPACE_MANIFEST.md, BASELINE_REPRO.md, models/C/formula.md, README.md before any code changes. Understanding: start from original Model C, preserve one global interpretable formula using only allowed existing drivers (dbar, annual precip, monthly precip, monthly t_air, EDv3 monthly GPP, plus masks/reference for evaluation). No latitude/longitude hacks, named-region routing, per-cell lookup tables, arbitrary residual coefficients, external inputs, or per-region formulas. Required process: repeated mechanism hypotheses, searches/ablations, official global/regional ILAMB for serious candidates, public TRENDY/firepipe for serious best candidates, current logs, final_report.md before stopping.

Baseline verification command `.venv/bin/python scripts/verify.py` returned PASS for all 24 pinned artifacts. Official global and regional ILAMB were run before candidate changes.

Baseline official global ILAMB: Bias 0.728089, RMSE 0.505759, Seasonal 0.845690, Spatial 0.772351, Overall 0.671529.

Initial failure triage from regional ILAMB: weakest Overall regions are euro 0.361, ceam 0.376, tena 0.381, mide 0.383, seas 0.487, shsa/eqas about 0.507. Dominant deficits in weak regions are very low Spatial Distribution (euro 0.080, mide 0.091, ceam 0.126, tena 0.160, eqas 0.177) plus low Bias/RMSE in some crop/human-fragmented or tropical regions. Australia has good Overall 0.670 but poor Seasonal 0.580.

No blocking questions. Proceeded into mechanistic search loops.

## Outer loop 1 — fuel persistence / antecedent productivity
Hypothesis: Monthly GPP may be too instantaneous; grass/crop/savanna fine fuels persist after production, so a current+lagged GPP blend might improve regional seasonality and spatial placement.

Unified mechanism: replace `GPP_month` in the GPP hump with `w * GPP_current + (1-w) * mean(GPP previous 3 or 6 months)`. Uses only existing monthly GPP.

Search: C1, Optuna 500 trials, added params only.

Result: proxy score was slightly worse than baseline and optimizer pushed `gpp_cur_w` to ~1, effectively reverting to original Model C. Mechanism rejected/pruned; no official ILAMB because not serious.

## Outer loop 2 — active dry-down / curing
Hypothesis: Fire activity is favored not just by absolute dryness but by active curing during the transition into dry season. This may help Australia/monsoon timing and weak regions with seasonal dry-down.

Unified mechanism: multiply Model C product by `dry_gate = dry_floor + (1-dry_floor) * sigmoid(Dbar - mean(Dbar previous 3 months), dry_k, dry_c)`.

Search: C2, Optuna 500 trials, added params only.

Official ILAMB: global Overall improved from 0.671529 to 0.672542. Seasonal rose to 0.852988; Bias/RMSE rose modestly; Spatial fell from 0.772351 to 0.764830. Regional weak areas improved: TENA, CEAM, EURO, MIDE, SEAS, EQAS. SHAF degraded slightly. Mechanism retained as useful but not enough alone.

A broader retune C5 (1000 trials, base + drygate params) degraded the proxy; conclusion: original base Model C params are already near a robust basin, and the added mechanism is safer as a low-dimensional gate.

## Outer loop 3 — antecedent wet-season fuel gate
Hypothesis: previous wetness may indicate fuel build-up; current precipitation already suppresses burning.

Unified mechanism: multiply by a saturating previous 3/6-month precipitation gate.

Search: C3, Optuna 500 trials; C4 combo with lagged GPP + drygate + wet gate, 700 trials.

Result: wet gate optimum was near identity (`wet_floor` about 0.94 and `wet_half` about 1 mm), and combo was worse than C2/C6/C7. Rejected/pruned as unnecessary complexity.

## Outer loop 4 — high annual precipitation / humid-regime suppression
Hypothesis: Model C's annual precipitation term only imposes a dry fuel floor and lacks an explicit humid-evergreen/wet-fuel ceiling. This can overpredict or misplace humid tropical/equatorial fires (notably EQAS/SEAS/SHSA/NHSA) while still preserving savanna fire through intermediate annual precipitation.

Unified mechanism: multiply Model C by `humid_gate = humid_floor + (1-humid_floor)/(1+(P_ann/humid_half)^humid_pow)`. This is a smooth global annual-precipitation function, not region routing.

Search: C6, Optuna 700 trials, added params only.

Official ILAMB: C6 improved global Overall to 0.672531 and produced large regional gains, especially EQAS +0.074 and SHSA/SEAS/CEAM/NHSA. This was the first clearly meaningful regional mechanism.

Ablations:
- C6b set humid_floor to 0; official global 0.672691 and best regional EQAS 0.589676 (+0.082281 vs baseline).
- C6d rounded to half=2000, power=6, floor=0.05; official global 0.672686 and similar behavior, slightly lower EQAS. This shows the mechanism is not a fragile exact-parameter artifact; a simple threshold-like global humid ceiling carries the signal.

## Outer loop 5 — combine humid suppression and active dry-down
Hypothesis: Humid-regime suppression fixes spatial/magnitude in humid tropics, while active dry-down improves seasonal timing and some temperate/dry weak regions. The two mechanisms are physically distinct and globally applicable.

Unified mechanism: Model C × humid_gate × dry_gate.

Search: C7, Optuna 1000 trials, added params only (base 12 parameters fixed).

Official ILAMB: best balanced global candidate. Overall 0.673264, Bias 0.731755, RMSE 0.508111, Seasonal 0.851062, Spatial 0.767279. It improves global Overall by +0.001735, Bias by +0.003666, RMSE by +0.002352, Seasonal by +0.005372, with Spatial -0.005072.

Regional: broad gains in CEAM (+0.019), SHSA (+0.017), SEAS (+0.018), EQAS (+0.067), NHSA (+0.0087), TENA (+0.0057), EURO (+0.0052), CEAS (+0.0023), NHAF (+0.0031), BOAS (+0.0013); slight losses in BONA (-0.0013), SHAF (-0.0028), AUST (-0.0004). C6b remains the best regional EQAS model, but C7 is the best global/balanced accepted model.

Clean public TRENDY/firepipe: C7 scored 0.673022, above the public baseline-current 0.671274 and all non-ED models, but behind a pre-existing ED-ModelC-pass2-P2F3 at 0.676846 in the benchmark source. Known JSBACH IndexError occurred but score table completed.

## Stopping rationale
The main plausible low-dimensional mechanisms under the fixed input contract were tested: antecedent GPP fuel persistence, active dry-down/curing, antecedent wet fuel, humid annual-precipitation suppression, and combinations. GPP lag and wet-fuel gates collapsed to identity or harmed scores. Dry-down and humid suppression were supported. Combining them gave the best balanced official global/regional result, while C6b is the best regional EQAS/humid-tropical variant. Remaining weak-region failures are dominated by spatial placement in Europe/Mideast/Central America/EQAS and Australia seasonality; these likely need human ignitions/suppression, land use/cropland, lightning, vegetation structure, or region-specific management signals unavailable under the current input contract. Further tuning within the tested families risks score fitting and spatial tradeoffs rather than new mechanism discovery.
