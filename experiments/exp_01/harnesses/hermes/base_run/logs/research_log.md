# Research Log

Formal base local-search run.

## Setup

- Workspace rebuilt from clean Model C source at `ed-autoresearch` commit `1bac731`.
- Prior pilot run archived outside this workspace.
- Baseline artifacts regenerated in this workspace; see `BASELINE_REPRO.md`.

## Baseline verification and official evidence

Hypothesis/function: original Model C from `models/C/params.json`, a unified global formula with dryness onset/suppression, annual precipitation floor, monthly rain dampening, monthly GPP hump, and air-temperature ignition.

Commands run:

```bash
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_baseline" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_baseline" bash scripts/run_official_regions.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" MODEL_NAME="ED-ModelC-baseline-formal" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-baseline-formal" bash scripts/run_public_trendy_firepipe.sh
```

Results:
- `scripts/verify.py`: PASS, all 24 required inputs/artifacts present and matching expected hashes.
- Official global ILAMB output: `ilamb/output_modelC_baseline`, Overall 0.671529.
- Official regional ILAMB output: `ilamb/output_regions_baseline`.
- Public TRENDY/firepipe output: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-baseline-formal`, rank #1 at Overall 0.671274. JSBACH produced the documented benchmark `IndexError` during model-confrontation but completed post-processing; other model comparisons completed.

Decision: retain original Model C as starting accepted model and comparison baseline.

## Loop 1: WET-SUPP-v1 annual wetness ceiling

Physical hypothesis: In perhumid climates, annual precipitation should not only increase fuel availability; it can maintain high live/dead fuel moisture and a humid boundary layer that suppress combustion even where fuel is abundant. Original Model C has a low-precipitation floor and monthly rain dampener but no smooth annual wetness ceiling.

Unified functional-form change:

```text
wet_supp(P_ann) = 1 / (1 + (P_ann / P_wet_half)^P_wet_pow)
Model C product := Model C product * wet_supp(P_ann)
fire = product^fire_exp
```

Inputs/constraints: uses only existing `p_ann_monthly.npy`; no coordinate, region, lookup, residual, or external input.

Search space and command:

```text
P_wet_half in [400, 600, 800, 1000, 1250, 1500, 2000, 3000, 5000]
P_wet_pow  in [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
```

```bash
.venv/bin/python scripts/scan_candidate_wet_suppression.py
```

Best deterministic proxy: `P_wet_half=3000`, `P_wet_pow=3.0`; proxy Overall 0.673109 vs proxy baseline 0.672789.

Implementation/evaluation commands:

```bash
# patched scripts/reproduce_modelC.py to activate optional P_wet_half/P_wet_pow keys
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_wet_supp_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_wet_supp_v1" bash scripts/run_official_regions.sh
```

Official global ILAMB: Overall 0.671384, Bias 0.729325, RMSE 0.506214, Seasonal 0.845835, Spatial 0.769334. This is -0.000145 vs baseline Overall.

Official regional ILAMB: broad regional improvements in wet/tropical regions (TENA +0.003254, CEAM +0.009207, NHSA +0.008031, SHSA +0.010717, SEAS +0.009698, EQAS +0.027613), but small damage to BONA, NHAF, SHAF, AUST and lower global Overall.

Public TRENDY/firepipe: not run because the candidate did not become a serious best-so-far candidate after official global ILAMB declined.

Decision: reject as best-so-far. Mechanism is plausible and regionally useful, but it lowers official global Overall and weakens African/australian fire regimes. Keep as diagnostic evidence that perhumid suppression helps some failures but creates arid/savanna trade-offs.

## Loop 2: LAG-FUEL-v1 antecedent/cured GPP fuel

Physical hypothesis: Burned area often responds to fuel produced before the fire month, after curing, not necessarily same-month GPP. A global antecedent GPP blend could improve seasonal phase and fire-season fuel limitation.

Unified functional-form change:

```text
GPP_eff = (1 - alpha) * GPP_month + alpha * mean(GPP[t-1] ... GPP[t-window])
Use GPP_eff inside the existing Model C GPP hump.
```

Inputs/constraints: uses only existing monthly GPP from `data/trendy_v14/EDv3_S3_gpp.nc`; no calendar-specific branch, region routing, coordinates, lookup tables, or residual corrections.

Search space and command:

```text
gpp_lag_window in [1, 2, 3, 4, 6, 9, 12]
gpp_lag_alpha  in [0.25, 0.5, 0.75, 1.0]
```

```bash
.venv/bin/python scripts/scan_candidate_lagged_fuel.py
```

Best deterministic proxy: `gpp_lag_window=12`, `gpp_lag_alpha=1.0`; proxy Overall 0.673435 vs proxy baseline 0.672789.

Implementation/evaluation commands:

```bash
# patched scripts/reproduce_modelC.py to activate optional gpp_lag_window/gpp_lag_alpha keys
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_lag_fuel_pure_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_lag_fuel_pure_v1" bash scripts/run_official_regions.sh
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" PATH="$PWD/.venv/bin:$PATH" MODEL_NAME="ED-ModelC-lag-fuel-pure-v1" OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/output_with_ED-ModelC-lag-fuel-pure-v1" bash scripts/run_public_trendy_firepipe.sh
```

Official global ILAMB: Overall 0.672274, Bias 0.727752, RMSE 0.505788, Seasonal 0.850890, Spatial 0.771151. This is +0.000745 vs baseline Overall, mostly from Seasonal Cycle, with slightly worse Bias and Spatial.

Official regional ILAMB: improves AUST (+0.008933) and tiny improvements in BONA/NHSA/CEAM/EQAS, but worsens TENA (-0.001043), EURO (-0.001970), MIDE (-0.007065), SHAF (-0.000875), BOAS (-0.000248), CEAS (-0.000851), and SEAS (-0.003994). This is exactly the prohibited pattern of a small global gain hiding regional damage.

Public TRENDY/firepipe: candidate ranks #1 among completed public comparisons at Overall 0.672014. JSBACH again hit the documented `IndexError`. Note: the benchmark script symlinks `SRC` into model folders; because `ED-ModelC-baseline-formal` was also a symlink to the workspace `burntArea.nc`, the later candidate public run printed an identical baseline-formal row. The uncontaminated baseline public run remains `output_with_ED-ModelC-baseline-formal` from the baseline loop with Overall 0.671274.

Decision: reject as accepted best-so-far despite higher official global/public Overall. The mechanism is plausible and serious, but the official regional table shows non-negligible damage in multiple already weak/important regimes. This candidate is recorded as the highest global-score trial, not as acceptable under the protocol.

## Loop 2b: LAG+WET combined diagnostic/ablation

Physical hypothesis: antecedent fuel and perhumid wetness suppression may complement each other: lagged fuel improves seasonal phase while annual wetness suppression prevents humid overprediction.

Functional form: simultaneous activation of WET-SUPP-v1 and LAG-FUEL-v1 with `P_wet_half=3000`, `P_wet_pow=3`, `gpp_lag_window=12`, `gpp_lag_alpha=1`.

Commands:

```bash
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_lag_wet_combo_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_lag_wet_combo_v1" bash scripts/run_official_regions.sh
```

Official global ILAMB: Overall 0.672173, Bias 0.728988, RMSE 0.506241, Seasonal 0.850932, Spatial 0.768463.

Official regional ILAMB: improves several humid/tropical regions and AUST but still damages EURO, MIDE, NHAF, SHAF, CEAS. It also has lower global than pure LAG-FUEL-v1.

Public TRENDY/firepipe: not run; pure LAG-FUEL was already the serious public benchmark candidate and the combo did not remove the regional-damage failure mode.

Decision: reject. The WET ablation reduces some humid overprediction but does not solve the regional trade-off introduced by lagged fuel, and it further lowers Spatial Distribution.

## Loop 3: PRECIP-MEM-v1 antecedent precipitation moisture

Physical hypothesis: fuel moisture and access respond to recent rainfall, not just precipitation during the fire month. A rolling memory term in the existing rain dampener might correct too-early or too-wet burning.

Unified functional-form change:

```text
P_month_eff = (1 - alpha) * P_month + alpha * mean(P_month[t-1] ... P_month[t-window])
p_damp = 1 / (1 + P_month_eff / pre_dampen_half)
```

Inputs/constraints: uses only existing `p_month_monthly.npy`; no external input, region routing, coordinate hack, lookup table, or residual coefficient.

Search space and command:

```text
precip_memory_window in [1, 2, 3, 4, 6]
precip_memory_alpha  in [0.25, 0.5, 0.75, 1.0]
```

```bash
.venv/bin/python scripts/scan_candidate_precip_memory.py
```

Best deterministic proxy: `precip_memory_window=1`, `precip_memory_alpha=0.25`; proxy Overall 0.671594 vs proxy baseline 0.672789.

Implementation/evaluation commands:

```bash
# patched scripts/reproduce_modelC.py to activate optional precip_memory_window/precip_memory_alpha keys
.venv/bin/python scripts/reproduce_modelC.py
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_modelC_precip_mem_v1" bash scripts/run_ilamb.sh
ILAMB_ROOT="$PWD/ilamb" PATH="$PWD/.venv/bin:$PATH" OUT="$PWD/ilamb/output_regions_precip_mem_v1" bash scripts/run_official_regions.sh
```

Official global ILAMB: Overall 0.670193, Bias 0.728316, RMSE 0.506595, Seasonal 0.846707, Spatial 0.762754. This is -0.001336 vs baseline.

Official regional ILAMB: improves many lower-scoring regions (TENA +0.011514, CEAM +0.011640, NHSA +0.015017, SHSA +0.025846, EURO +0.012152, MIDE +0.010737, SEAS +0.025434, EQAS +0.011763, AUST +0.010295) but substantially damages NHAF (-0.017440) and SHAF (-0.005173), and lowers global Spatial Distribution by about 0.0096.

Public TRENDY/firepipe: not run because official global declined and the candidate was not a serious best-so-far.

Decision: reject as best-so-far. This mechanism is diagnostically valuable: moisture memory helps many non-African and humid/tropical regional scores, but it degrades African savanna fire regimes enough that the global and regional acceptance criteria fail.

## Final restoration

After candidate evaluations, the workspace model was restored to original Model C params and regenerated:

```bash
cp models/C/params.BASELINE-formal.json models/C/params.json
.venv/bin/python scripts/reproduce_modelC.py
sha256sum models/C/params.json ilamb/MODELS/ED-ModelC-final/burntArea.nc
.venv/bin/python scripts/verify.py
```

Restored hashes:

```text
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
```

`verify.py` PASS after restoration.

## Stopping decision

Constrained exploration covered the plausible smooth extensions available from the existing inputs that directly address the observed failure modes: perhumid wetness ceiling, antecedent/cured fuel, their combination, and antecedent precipitation moisture. The searches found only small global gains tied to regional damage, or regional improvements tied to global/spatial loss. Under the protocol, original Model C remains the best accepted model; LAG-FUEL-v1 is the highest global/public trial but rejected. See `stuck_state.md` for supporting stuck-state documentation.

## Final report generation

`final_report.md` was written as the required final stopping artifact. It records original Model C as the final accepted model, LAG-FUEL-v1 as the rejected scalar-best trial, the official global/regional ILAMB evidence, public TRENDY/firepipe comparison, constraint compliance, remaining failures, and the rationale for stopping. It also clarifies that GFED is reference/evaluation data, not a new model predictor or direct fitted input.
