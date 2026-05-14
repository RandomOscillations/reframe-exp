# Constraint Checks

For each serious candidate, explicitly check:

- [x] Uses only inputs listed in `WORKSPACE_MANIFEST.md`.
- [x] Does not add external data as a model input.
- [x] Does not use per-cell lookup tables.
- [x] Does not use latitude/longitude hacks.
- [x] Does not route by named region.
- [x] Does not use per-region formulas.
- [x] Does not add arbitrary residual coefficients.
- [x] Has a physical/mechanistic explanation.
- [x] Has official global ILAMB evaluation.
- [x] Has official regional ILAMB evaluation.
- [x] Has public TRENDY/firepipe evaluation if it is a serious best-so-far candidate.
- [x] Has ablation or diagnostic support when feasible.

## Baseline / original Model C

- Inputs: allowed `dbar`, `p_ann`, `p_month`, `t_air`, EDv3 GPP, and GFED reference/mask in existing baseline source.
- No external model input: yes.
- No lookup/table/coordinate/region routing: yes.
- No per-region formulas/residuals: yes.
- Mechanistic explanation: documented in `models/C/formula.md`.
- Official global ILAMB: `ilamb/output_modelC_baseline`, Overall 0.671529.
- Official regional ILAMB: `ilamb/output_regions_baseline`.
- Public TRENDY/firepipe: `output_with_ED-ModelC-baseline-formal`, rank #1 Overall 0.671274.
- Verdict: constraint-compliant accepted baseline and final best accepted model.

## WET-SUPP-v1

- Inputs: only existing `p_ann` annual precipitation driver.
- No external model input: yes.
- No lookup/table/coordinate/region routing: yes.
- No per-region formulas/residuals: yes.
- Mechanism: smooth annual wetness ceiling for perhumid fuel-moisture/combustibility limitation.
- Parameter/search space: documented deterministic grid over `P_wet_half`, `P_wet_pow`.
- Official global ILAMB: `ilamb/output_modelC_wet_supp_v1`, Overall 0.671384.
- Official regional ILAMB: `ilamb/output_regions_wet_supp_v1`.
- Public TRENDY/firepipe: not required/run because official global declined and the candidate was not a serious best-so-far.
- Ablation/diagnostic: standalone candidate plus LAG+WET combination.
- Verdict: scientifically plausible and constraint-compliant, but rejected for lower global Overall and regional savanna/Australia damage.

## LAG-FUEL-v1

- Inputs: only existing monthly GPP driver from `data/trendy_v14/EDv3_S3_gpp.nc`.
- No external model input: yes.
- No lookup/table/coordinate/region routing: yes.
- No calendar-specific branch: yes; a global rolling lag is applied uniformly.
- No per-region formulas/residuals: yes.
- Mechanism: antecedent/cured productivity controls fuel available for burning.
- Parameter/search space: deterministic grid over lag window and blend alpha.
- Official global ILAMB: `ilamb/output_modelC_lag_fuel_pure_v1`, Overall 0.672274.
- Official regional ILAMB: `ilamb/output_regions_lag_fuel_pure_v1`.
- Public TRENDY/firepipe: `output_with_ED-ModelC-lag-fuel-pure-v1`, candidate rank #1 Overall 0.672014. JSBACH documented `IndexError`; baseline symlink caveat logged in `eval_log.md`.
- Ablation/diagnostic: LAG+WET combination tested; WET-SUPP standalone tested.
- Verdict: constraint-compliant but rejected as accepted model because the small global/public gain hides regional damage in TENA/EURO/MIDE/SEAS and other regions.

## LAG+WET-v1

- Inputs: only existing monthly GPP and annual precipitation drivers.
- No external model input: yes.
- No lookup/table/coordinate/region routing: yes.
- No per-region formulas/residuals: yes.
- Mechanism: combined antecedent fuel and perhumid wetness limitation.
- Official global ILAMB: `ilamb/output_modelC_lag_wet_combo_v1`, Overall 0.672173.
- Official regional ILAMB: `ilamb/output_regions_lag_wet_combo_v1`.
- Public TRENDY/firepipe: not run because pure LAG-FUEL was the serious public candidate and the combo did not fix regional damage or exceed pure lag.
- Ablation/diagnostic: explicit combination/ablation of two standalone mechanisms.
- Verdict: constraint-compliant but rejected; regional damage persists.

## PRECIP-MEM-v1

- Inputs: only existing monthly precipitation driver `p_month`.
- No external model input: yes.
- No lookup/table/coordinate/region routing: yes.
- No calendar-specific branch: yes; a global rolling lag is applied uniformly.
- No per-region formulas/residuals: yes.
- Mechanism: recent rainfall memory affects fuel moisture/accessibility beyond the burn month.
- Parameter/search space: deterministic grid over precipitation-memory window and blend alpha.
- Official global ILAMB: `ilamb/output_modelC_precip_mem_v1`, Overall 0.670193.
- Official regional ILAMB: `ilamb/output_regions_precip_mem_v1`.
- Public TRENDY/firepipe: not required/run because official global declined and the candidate was not a serious best-so-far.
- Ablation/diagnostic: standalone diagnostic with strong regional-signature contrast.
- Verdict: constraint-compliant but rejected; regional gains in many weak regions are offset by African savanna damage and global Spatial loss.

## Final code/workspace compliance

`models/C/params.json` and `ilamb/MODELS/ED-ModelC-final/burntArea.nc` were restored to the original Model C baseline hashes after candidate testing. The optional branches in `scripts/reproduce_modelC.py` are inactive unless candidate parameter keys are present; therefore final generated `burntArea.nc` is bit-identical to the documented baseline.
