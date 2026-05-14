# Final Report: ED Fire Model C Outer Autoresearch Continuation

## Executive summary

Best accepted final model: PRECIP-CONC-WET-v1.

Highest official global/public scalar model: PRECIP-CONC-WET-CURING-LAG-v1, rejected as final because it damages MIDE, an already weak region, for a small scalar gain over the accepted model.

Original Model C remains an excellent baseline, but the outer autoresearch loop found a defensible unified mechanistic improvement: annual wetness suppression relieved by an allowed precipitation-concentration / dry-season contrast term.

Final accepted mechanism:

```text
Model C product *= wet_multiplier

wet = 1 / (1 + (P_ann / P_wet_half)^P_wet_pow)

dry_frac = trailing-12-month fraction of months where P_month < dry_month_threshold
season_gate = sigmoid(dry_frac; dryfrac_k, dryfrac_c)
D_support = sigmoid(Dbar; D_support_k, D_support_c)
relief = season_gate * ((1 - d_support_weight) + d_support_weight * D_support)

wet_multiplier = 1 - wet_strength * (1 - wet) * (1 - relief_strength * relief)
```

Physical interpretation: high annual precipitation suppresses fire in perhumid/wet forest-like regimes, but this suppression is relieved where the same allowed precipitation sequence shows a strong dry season. This distinguishes high-rainfall seasonal savannas from high-rainfall perhumid forests without using region labels, coordinates, land-cover data, per-cell lookup tables, or residual correction.

Final accepted parameters:

```json
{
  "family": "precip_concentration_wet_relief",
  "wet_strength": 0.9749769007371538,
  "P_wet_half": 1779.4206816068952,
  "P_wet_pow": 4.698056826790257,
  "relief_strength": 0.7909704781841365,
  "dry_month_threshold": 18.752075249354416,
  "dryfrac_k": 23.195108254021612,
  "dryfrac_c": 0.2251706610087917,
  "D_support_k": 0.0003532027606815267,
  "D_support_c": 169.58180624426103,
  "d_support_weight": 0.31657480284868766
}
```

Final workspace output state:

```text
ilamb/MODELS/ED-ModelC-final/burntArea.nc
sha256 c97b536687cb1512f879cc22a21bdfe83acfa18229d45ef013d269543a550434
```

The baseline `models/C/params.json` was left unchanged and remains hash-matched to original Model C; the accepted extension parameters are stored in:

```text
models/C/candidate_search/precip_concentration_wet_search_500_trials.json
sha256 d803675a83fef6c0a7d78b75de9f774b23ed00d89d9c6cdb08247187f51ba6be
```

## Protocol compliance

The initial required files were read before code/model changes:

- `AGENTS.md`
- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

Allowed predictive inputs used by the baseline and all candidates:

- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`

GFED and ILAMB data were used only as reference/evaluation data and for the baseline mask/evaluation workflow, not as predictive inputs.

Disallowed shortcuts not used:

- no external model input data;
- no latitude/longitude hacks;
- no named-region routing;
- no per-cell lookup tables;
- no per-region formulas;
- no arbitrary residual correction coefficients;
- no direct fitting to GFED by cell identity.

## Baseline reproduction and evaluation context

Baseline verification at the start of the run:

```bash
.venv/bin/python scripts/verify.py
```

Result: PASS, 24/24 files present and hash-matched.

Important ILAMB note: `ILAMB_ROOT="$PWD/ilamb"` did not contain `DATA/burntArea/GFED4.1S/burntArea.nc` in this workspace and produced `MisplacedData`. Official evidence in this report uses the local reference-data root:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb
```

## Outer autoresearch loop summary

### Round 1 candidates

1. OPT-WET-v1: annual wetness ceiling.
   - Mechanistic signal: strong humid/tropical improvements.
   - Failure: annual wetness alone over-suppressed seasonal savanna/Australia and lowered Spatial Distribution.
   - Inference: need a dry-season/savanna relief term.

2. LAG-FUEL-v1: uniform 12-month antecedent GPP.
   - Mechanistic signal: improves global Seasonal Cycle and Australia.
   - Failure: damages MIDE, SEAS, EURO, TENA, CEAS, NHAF, SHAF, and BOAS.
   - Inference: antecedent fuel must be gated by curing/dry-season accessibility, not applied everywhere.

### Round 2 mechanism queue and outcomes

Q1. DRYSEASON-WET-v1:
- Added current-month Dbar/low-precipitation relief to annual wetness suppression.
- Improved over OPT-WET-v1 and fixed NHAF, but still had SHAF/AUST and Spatial damage.
- Result: diagnostic, not final.

Q2. CURING-LAG-v1:
- Gated antecedent GPP by Dbar/low-precipitation curing indicators.
- Reduced uniform LAG-FUEL damage and improved Australia/seasonality, but did not dominate wetness-relief candidates and still harmed some weak regions.
- Result: diagnostic, not final.

Q3. PRECIP-CONC-WET-v1:
- Used trailing-12 dry-month fraction as annual dry-season contrast to relieve annual wetness suppression.
- Improved global/public score and broadly improved weak regions while preserving MIDE and NHAF.
- Result: accepted final model.

Constrained Q3+Q2 combo:
- Fixed Q3 wetness parameters and searched only a curing-gated one-month GPP lag.
- Highest scalar model, but reintroduced MIDE damage for small scalar gain.
- Result: rejected as final, retained as highest global/public scalar candidate.

## Search setup and trial counts

| Search | Mechanism | Trials | Output JSON |
|---|---|---:|---|
| Round 1 generic extension search | wetness, lag fuel, precip memory, drydown, hybrids | 500 | `models/C/candidate_search/optuna_extension_search_500_trials.json` |
| Q1 | dry-season-relieved wetness suppression | 500 | `models/C/candidate_search/dryseason_wet_search_500_trials.json` |
| Q2 | curing-gated antecedent fuel | 500 | `models/C/candidate_search/curing_lag_search_500_trials.json` |
| Q3 | precipitation-concentration wetness relief | 500 | `models/C/candidate_search/precip_concentration_wet_search_500_trials.json` |
| Constrained combo | fixed Q3 + curing-gated lag | 500 | `models/C/candidate_search/precip_conc_wet_curing_lag_search_500_trials.json` |

All searches used Optuna as an inner tuning loop tied to a stated mechanism family. The outer loop used rejected-candidate failure patterns to propose the next mechanism.

## Official global ILAMB comparison

Official output directories:

- Baseline: `ilamb/output_modelC_baseline`
- OPT-WET-v1: `ilamb/output_modelC_opt_wet_v1`
- DRYSEASON-WET-v1: `ilamb/output_modelC_dryseason_wet_v1`
- PRECIP-CONC-WET-v1: `ilamb/output_modelC_precip_conc_wet_v1`
- LAG-FUEL-v1: `ilamb/output_modelC_lag_fuel_v1`
- CURING-LAG-v1: `ilamb/output_modelC_curing_lag_v1`
- PRECIP-CONC-WET-CURING-LAG-v1: `ilamb/output_modelC_precip_conc_wet_curing_lag_v1`

| Model | Status | Bias | RMSE | Seasonal | Spatial | Overall | Period Mean |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline Model C | baseline | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.671529 | 0.611164 |
| OPT-WET-v1 | rejected diagnostic | 0.730475 | 0.506667 | 0.845975 | 0.768628 | 0.671682 | 0.567266 |
| DRYSEASON-WET-v1 | rejected diagnostic | 0.731037 | 0.506947 | 0.846199 | 0.770020 | 0.672230 | 0.564224 |
| PRECIP-CONC-WET-v1 | accepted final | 0.731487 | 0.507071 | 0.845979 | 0.770753 | 0.672472 | 0.554164 |
| LAG-FUEL-v1 | rejected diagnostic | 0.728075 | 0.505767 | 0.848154 | 0.771532 | 0.671859 | 0.622335 |
| CURING-LAG-v1 | rejected diagnostic | 0.727997 | 0.505755 | 0.848710 | 0.771904 | 0.672024 | 0.614471 |
| PRECIP-CONC-WET-CURING-LAG-v1 | highest scalar, rejected | 0.731335 | 0.507024 | 0.847636 | 0.770385 | 0.672681 | 0.558436 |

Accepted final global delta vs baseline:

- Overall: +0.000943
- Bias: +0.003398
- RMSE: +0.001312
- Seasonal: +0.000289
- Spatial: -0.001598
- Period Mean: -0.057000

Interpretation: PRECIP-CONC-WET-v1 improves Bias/RMSE and preserves Seasonal Cycle while taking a modest Spatial penalty. The regional evidence below is why the Spatial penalty is considered acceptable: it buys broad improvements in the weakest humid/tropical regions without the larger savanna damage of simpler wetness suppression.

## Official regional ILAMB comparison

Regional Overall deltas versus baseline:

| Region | Baseline | OPT-WET | DRYSEASON-WET | PRECIP-CONC-WET | LAG-FUEL | CURING-LAG | COMBO |
|---|---:|---:|---:|---:|---:|---:|---:|
| global | 0.671529 | +0.000153 | +0.000701 | +0.000943 | +0.000330 | +0.000495 | +0.001152 |
| bona | 0.789806 | +0.000040 | +0.000072 | +0.000109 | +0.000015 | -0.000020 | +0.000085 |
| tena | 0.381473 | +0.003903 | +0.003591 | +0.005959 | -0.001323 | -0.001105 | +0.004818 |
| ceam | 0.376153 | +0.013998 | +0.014943 | +0.020241 | +0.000093 | +0.000035 | +0.020252 |
| nhsa | 0.605824 | +0.009945 | +0.008846 | +0.010228 | +0.000140 | +0.000080 | +0.010256 |
| shsa | 0.507249 | +0.016485 | +0.017608 | +0.018546 | -0.000005 | +0.000402 | +0.018569 |
| euro | 0.361128 | +0.001563 | +0.001228 | +0.002298 | -0.001974 | -0.000819 | +0.001006 |
| mide | 0.382769 | +0.000386 | +0.000228 | +0.000362 | -0.006462 | -0.001335 | -0.002080 |
| nhaf | 0.645855 | -0.001075 | +0.000443 | +0.001573 | -0.000901 | -0.000268 | +0.001264 |
| shaf | 0.646693 | -0.002837 | -0.001779 | -0.000543 | -0.000879 | -0.000061 | -0.000674 |
| boas | 0.728733 | +0.000156 | +0.000065 | +0.000165 | -0.000439 | +0.000014 | +0.000159 |
| ceas | 0.670499 | +0.000450 | +0.000339 | +0.000565 | -0.000946 | +0.001870 | +0.001791 |
| seas | 0.487193 | +0.014521 | +0.014257 | +0.010724 | -0.004259 | -0.002021 | +0.007885 |
| eqas | 0.507395 | +0.052015 | +0.060745 | +0.076892 | +0.000036 | +0.000002 | +0.076895 |
| aust | 0.670219 | -0.001146 | -0.001444 | -0.000646 | +0.006033 | +0.004197 | +0.001516 |

Accepted final regional interpretation:

- Major weak-region gains: EQAS +0.076892, CEAM +0.020241, SHSA +0.018546, SEAS +0.010724, NHSA +0.010228, TENA +0.005959, EURO +0.002298.
- MIDE is preserved: +0.000362, unlike LAG-FUEL, CURING-LAG, and the combo.
- NHAF improves: +0.001573, showing the dry-season contrast successfully avoids the earlier wetness damage there.
- Remaining losses are small: SHAF -0.000543, AUST -0.000646. These are much smaller than the regional gains and smaller than the OPT-WET/DRYSEASON-WET losses.

Why the combo is rejected despite higher Overall:

- Combo global Overall is 0.672681, only +0.000209 over PRECIP-CONC-WET-v1.
- It improves AUST (+0.001516) and Seasonal Cycle, but damages MIDE (-0.002080), an already weak region.
- It also weakens the SEAS gain relative to Q3 and has lower global Spatial than Q3.
- The added curing-lag complexity is not justified by the regional trade-off.

## Public TRENDY/firepipe comparison

Public output directories:

- Baseline: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-baseline-current`
- OPT-WET-v1: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-opt-wet-v1-current`
- DRYSEASON-WET-v1: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-dryseason-wet-v1-current`
- PRECIP-CONC-WET-v1: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-precip-conc-wet-v1-current`
- LAG-FUEL-v1: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-lag-fuel-v1-current`
- CURING-LAG-v1: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-curing-lag-v1-current`
- COMBO: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-precip-conc-wet-curing-lag-v1-current`

Known caveat: JSBACH produced the documented ILAMB `IndexError`; score tables completed for the candidate and other comparator rows.

| Rank | Model | Public Overall | Decision |
|---:|---|---:|---|
| 1 | ED-ModelC-precip-conc-wet-curing-lag-v1-current | 0.672433 | rejected, MIDE damage |
| 2 | ED-ModelC-precip-conc-wet-v1-current | 0.672227 | accepted final |
| 3 | ED-ModelC-dryseason-wet-v1-current | 0.671985 | diagnostic |
| 4 | ED-ModelC-curing-lag-v1-current | 0.671767 | diagnostic |
| 5 | ED-ModelC-lag-fuel-v1-current | 0.671600 | diagnostic/rejected |
| 6 | ED-ModelC-opt-wet-v1-current | 0.671436 | diagnostic/rejected |
| 7 | ED-ModelC-baseline-current | 0.671274 | baseline |
| 8 | CLASSIC | 0.666048 | comparator |
| 9 | CLM6.0 | 0.660644 | comparator |
| 10 | CLM-FATES | 0.656831 | comparator |
| 11 | ELM-FATES | 0.656788 | comparator |
| 12 | JULES-ES | 0.590519 | comparator |
| 13 | ELM | 0.556381 | comparator |
| 14 | VISIT-UT | 0.554455 | comparator |
| 15 | LPJmL | 0.548547 | comparator |
| 16 | LPJ-GUESS | 0.479233 | comparator |
| 17 | EDv3 | 0.477410 | comparator |
| 18 | LPJ-EOSIM | 0.463542 | comparator |

## Mechanisms tried and failure-derived conclusions

### Annual wetness ceiling

OPT-WET-v1 proved that humid/perhumid suppression is missing from Model C, but annual wetness alone is too blunt. It damages seasonal savanna/Australia and lowers Spatial Distribution.

### Current dry-season-relieved wetness

DRYSEASON-WET-v1 showed that dry-season relief is the right physical direction. It improved global/public score and fixed NHAF relative to OPT-WET, but current-month Dbar/low-precip relief still left SHAF/AUST damage.

### Uniform lagged fuel

LAG-FUEL-v1 improved seasonality but damaged many regions, proving antecedent productivity cannot be applied everywhere as fuel.

### Curing-gated lagged fuel

CURING-LAG-v1 reduced uniform lag damage and improved Australia, confirming the physical failure diagnosis. It did not dominate wetness-relief candidates and still harmed some weak regions.

### Precipitation-concentration wetness relief

PRECIP-CONC-WET-v1 directly addressed the perhumid-vs-seasonal-savanna distinction using an allowed trailing-12 dry-month fraction. It is the best accepted model because it preserves MIDE, improves NHAF, and gives broad weak-region gains.

### Q3 + curing-lag combo

The constrained combo tested whether curing-gated lag is complementary to Q3. It is not accepted: the global/public scalar gain is small and comes with MIDE damage and added complexity.

## Remaining failures and why the queue is exhausted

Remaining issues in the accepted final model:

- Spatial Distribution still declines slightly versus baseline.
- SHAF and AUST have very small Overall losses.
- MIDE remains weak in absolute terms, although preserved relative to baseline by the accepted model.
- The model still cannot explicitly represent human suppression/ignition, land use, cropland/pasture management, grazing, lightning climatology, vegetation/fuel type, or fragmentation.

Why no valid next mechanism remains under this input contract:

- The wetness/savanna distinction was tested as annual wetness, current dry-season relief, and trailing-12 precipitation concentration. The last is the best regional-balanced form.
- The fuel carry-over hypothesis was tested as uniform lag and curing-gated lag. Curing-gating helps but does not justify inclusion in the accepted model because it damages MIDE when combined with the best wetness form.
- A targeted fix for SHAF/AUST or MIDE would require separating fire regimes beyond what Dbar, P_ann, P_month, GPP, and T_air can robustly distinguish. The likely missing variables are land cover/fuel type, human management/suppression, grazing, fragmentation, and ignition climatology, all unavailable or disallowed as new model inputs.
- Further region-specific or cell-specific corrections would violate the constraints against named-region routing, per-region formulas, coordinate hacks, per-cell lookup tables, or arbitrary residual corrections.

Therefore the next-mechanism queue is exhausted for scientific reasons, not because the first scalar improvement was accepted.

## Reproduction instructions for final accepted model

Accepted model output is currently written to:

```text
ilamb/MODELS/ED-ModelC-final/burntArea.nc
```

To regenerate it from original Model C parameters and the accepted extension JSON:

```bash
.venv/bin/python scripts/generate_candidate_output.py \
  models/C/candidate_search/precip_concentration_wet_search_500_trials.json \
  PRECIP-CONC-WET-v1
```

Then run official evaluations:

```bash
ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" \
PATH="$PWD/.venv/bin:$PATH" \
OUT="$PWD/ilamb/output_modelC_precip_conc_wet_v1" \
bash scripts/run_ilamb.sh

ILAMB_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/ed-autoresearch-source/ilamb" \
PATH="$PWD/.venv/bin:$PATH" \
OUT="$PWD/ilamb/output_regions_precip_conc_wet_v1" \
bash scripts/run_official_regions.sh
```

Public benchmark:

```bash
TRENDY_BENCHMARK_ROOT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source" \
MODEL_NAME="ED-ModelC-precip-conc-wet-v1-current" \
OUT="/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source/ilamb/outputs/output_with_ED-ModelC-precip-conc-wet-v1-current" \
bash scripts/run_public_trendy_firepipe.sh
```

## Final answer

The defensible stopping point is PRECIP-CONC-WET-v1 as the accepted final model. It improves official global Overall from 0.671529 to 0.672472 and public Overall from 0.671274 to 0.672227, while broadly improving weak humid/tropical regions and preserving MIDE. The only higher scalar model, PRECIP-CONC-WET-CURING-LAG-v1, is rejected because its small scalar gain reintroduces MIDE damage and added complexity. The mechanism queue is exhausted: wetness, dry-season relief, precipitation concentration, lagged fuel, curing-gated fuel, and the only physically motivated constrained combination have all been tested with official global and regional ILAMB evidence.
