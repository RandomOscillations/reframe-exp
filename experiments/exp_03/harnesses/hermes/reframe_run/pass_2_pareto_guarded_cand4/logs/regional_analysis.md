# Regional Analysis

## Baseline Model C regional ILAMB triage
Official regional ILAMB scalar output: ilamb/output_modelC_regions/scalar_database.csv
Regions: GFED/ILAMB regions global, bona, tena, ceam, nhsa, shsa, euro, mide, nhaf, shaf, boas, ceas, seas, eqas, aust.

ILAMB did not emit an `Overall Score` scalar for each region. For triage, I computed:
`diagnostic_overall = (2*Bias + 2*RMSE + Seasonal + Spatial)/6`.
This is not used as an official acceptance metric; official global Overall remains from ILAMB.

## Regional score table, sorted by diagnostic_overall ascending
| Region | Bias | RMSE | Seasonal | Spatial | Diagnostic overall | Triage read |
|---|---:|---:|---:|---:|---:|---|
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3613 | Magnitude/spatial failure despite good seasonal phase; candidate mechanisms need to suppress/redistribute fire in mixed tropical/agricultural cells using physical proxies only. |
| euro | 0.3935 | 0.2618 | 0.8082 | 0.0805 | 0.3665 | Very poor spatial and RMSE; likely non-climate/human land-use structure cannot be directly represented, but high productivity + moderate climate may need stronger suppression. |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3907 | Poor spatial and seasonal; suggests missing temperate seasonal curing/antecedent fuel timing. |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3918 | Arid/semi-arid spatial failure; may need sharper fuel-limited/hyperarid suppression or annual precip floor. |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4887 | Mixed monsoon/cropland/forest; possible wet-season fuel charging plus dry-month ignition mismatch. |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5016 | Spatial/magnitude weakness in savanna/forest transition; possible high-GPP moist suppression or antecedent fuel effects. |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5024 | Moist tropical forest/peat/agricultural complexity; physical proxies may only partially separate high-rain high-GPP closed canopy from burnable edges. |
| nhsa | 0.5014 | 0.4931 | 0.9144 | 0.6270 | 0.5884 | Seasonality excellent; bias/RMSE are main weaknesses. |
| shaf | 0.7597 | 0.5023 | 0.9021 | 0.5671 | 0.6655 | Strong seasonality and bias; RMSE/spatial leave room. |
| nhaf | 0.7693 | 0.4795 | 0.9010 | 0.5998 | 0.6664 | Similar to SHAF; main global fire belt well captured. |
| aust | 0.7456 | 0.6520 | 0.5795 | 0.7219 | 0.6828 | Spatial/magnitude good, seasonality poor; candidate dry-down timing may help. |
| ceas | 0.7834 | 0.5603 | 0.7222 | 0.7265 | 0.6893 | Mostly decent; seasonal weakness. |
| boas | 0.8408 | 0.6192 | 0.7966 | 0.7679 | 0.7474 | Strong. |
| bona | 0.8840 | 0.7425 | 0.9251 | 0.6549 | 0.8055 | Strongest region. |

## Hypothesis ordering
1. Antecedent fuel charging / dry-down timing: analogous to a rechargeable battery or epidemic susceptible pool: wet/productive periods charge fine fuels, dry/hot months create transmission. Should target TENA, AUST, SEAS, SHSA without named routing.
2. Hyperarid and closed-canopy suppression: analogous to combustion needing both fuel and oxygen; deserts lack fuel, wet forests lack flammability. Should target MIDE, EQAS, EURO, CEAM.
3. Asymmetric productivity response: current GPP hump is almost monotone for many cells after tuning; a richer but still mechanistic hump/plateau may separate grass/savanna from moist forests.
4. Ablation/pruning: any added complexity must prove global/regional value and not simply chase regional residuals.


## Mechanism family search results

Screened with `scripts/explore_fire_candidates.py` using 500 Optuna trials per family unless noted. The fast proxy deliberately combined global fit with weak-region diagnostics, then serious/promising candidates were promoted to official ILAMB.

Fast screening summary:
- C_reopt: fast objective 0.573881; fast global 0.626112; raw land mean 0.068912.
- annual_p_hump: fast objective 0.571907; fast global 0.617062; raw land mean 0.052945.
- wetforest_curing: fast objective 0.567909; fast global 0.622108; raw land mean 0.071295.
- drydown_curing: fast objective 0.567601; fast global 0.629550; selected a near-neutral drydown effect, effectively pruning itself.
- antecedent_fuel: fast objective 0.567219; fast global 0.615867.
- fuel_moisture_balance: fast objective 0.559874; fast global 0.597305.

Official global ILAMB for promoted candidates (ilamb/output_candidates_global_full/scalar_database.csv):
- ED-ModelC-final: Overall 0.671529; Bias 0.728089; RMSE 0.505759; Seasonal 0.845690; Spatial 0.772351.
- ED-Cand-Creopt: Overall 0.665583; Bias/RMSE slightly higher but Spatial fell to 0.732615.
- ED-Cand-WetForestCuring: Overall 0.661118; Spatial 0.719458.
- ED-Cand-AnnualPHump: Overall 0.653225; Spatial 0.665412.
- ED-Cand-AnteFuel: Overall 0.652335; Spatial 0.685066.

Partial wet-suppression ablation:
- Script: scripts/scan_partial_wet_suppression.py
- Grid: P_wet in [1200,1600,2000,2600,3200,4000,6000,10000], pow in [0.25,0.5,0.75,1,1.5,2,3], floor in [0.70,0.80,0.85,0.90,0.93,0.95,0.97,0.99,1.0]. Floor=1 is exact baseline ablation.
- Selected constrained candidate: P_wet=2000, pow=0.25, floor=0.70 based on fast proxy within 0.001 of baseline and better weak-region mean.
- Official global ILAMB: ED-Cand-PartialWetSupp Overall 0.669509 vs C0 0.671529. Bias/RMSE/Seasonal slightly improve, Spatial falls 0.772351 -> 0.759868.
- Official regional diagnostic deltas vs C0: SHSA +0.0169, NHSA +0.0146, EURO +0.0145, EQAS +0.0133, CEAM +0.0123, SEAS +0.0122, TENA +0.0117, MIDE +0.0079; SHAF -0.0090, NHAF -0.0071, BONA -0.0032.
- Clean public benchmark: ED-Cand-PartialWetSupp Overall 0.669258, behind ED-ModelC-baseline 0.675085 and ED-ModelC-current 0.671274 but ahead of CLASSIC 0.666048 in that run. JSBACH emitted the same IndexError caveat as previous public runs.

Stopping assessment:
The explored families produce coherent regional repairs in exactly the initially weak regions, which supports the physical diagnosis, but all repairs reduce official global Spatial Distribution enough to lose Overall. Since the incumbent is already near the public benchmark ceiling, the remaining failures appear tied to heterogeneity not identifiable under the fixed climate/GPP contract without land-use/human/vegetation-structure inputs or forbidden routing.


## Continuation regional findings
Official regional output for the final focused candidates: `ilamb/output_cand3_regions/scalar_database.csv`.

Best final candidate: `ED-Cand3-release_window_wetcap`.
Regional diagnostic deltas vs ED-ModelC-final:
- BONA -0.0120
- TENA +0.0132
- CEAM +0.0076
- NHSA -0.0029
- SHSA +0.0062
- EURO +0.0211
- MIDE +0.0036
- NHAF +0.0185
- SHAF +0.0155
- BOAS +0.0093
- CEAS +0.0062
- SEAS +0.0089
- EQAS +0.0279
- AUST +0.0048
- global diagnostic +0.0065

Regional interpretation:
- The final mechanism preserves the first cycle's wet-region repairs while reversing the earlier global Spatial penalty. EQAS, EURO, TENA, SEAS, SHSA, and CEAM all improve; African fire belts also improve rather than degrade, which was the main failure of blunt wet suppression.
- The remaining losses are concentrated in BONA and slight NHSA. A temperature-conditioned refinement designed to protect BONA failed fast screening, suggesting the BONA loss is not easily separable by a global temperature interlock without damaging spatial/seasonal skill elsewhere.
- CEAM/EURO/TENA remain weak in absolute terms despite improvement, consistent with missing human/land-use/fragmentation controls under the fixed input contract.

## 2026-05-19 00:03:05 continuation cycle 2 regional analysis

Official diagnostic regional comparison for pruned Pareto guarded (`ED-Cand4Abl-no_hotboost`). Positive deltas are relative to original Model C and Cand3 respectively.

| Region | Cand4Abl | delta vs C | delta vs Cand3 |
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

- Cand4Abl improves 9/14 named non-global regions versus original Model C, but only 5/14 versus Cand3.
- Biggest Cand4Abl improvements versus Model C: EQAS, SHAF, NHAF, BOAS, MIDE/EURO/TENA. Biggest regressions versus Model C: NHSA, SHSA, SEAS, CEAM, BONA.
- Versus Cand3, Cand4Abl improves global, EQAS, SHAF, NHAF, BOAS, and MIDE, but worsens NHSA, SHSA, EURO, SEAS, CEAM, TENA, CEAS, AUST, and BONA slightly.
- Interpretation: the pruned guarded corridor is a global/public benchmark leader but not a step-function regional improvement over Cand3. Cand3 remains the best broad regional model; Cand4Abl is best only if global/public score is prioritized with documented regional tradeoffs.
