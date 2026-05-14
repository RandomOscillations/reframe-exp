# Regional Analysis

## Baseline failure pattern

Baseline official regional ILAMB showed that weak regions were dominated by amplitude/spatial failures, not seasonal phase.

Weakest baseline regions:

| Region | Overall | Bias | RMSE | Seasonal | Spatial | Model/obs period-mean ratio |
|---|---:|---:|---:|---:|---:|---:|
| euro | 0.361128 | 0.393450 | 0.261763 | 0.808165 | 0.080499 | ~12.8 |
| ceam | 0.376153 | 0.286887 | 0.310422 | 0.847470 | 0.125564 | ~10.4 |
| tena | 0.381473 | 0.437076 | 0.307975 | 0.694036 | 0.160304 | ~14.8 |
| mide | 0.382769 | 0.436689 | 0.310067 | 0.765840 | 0.091179 | ~16.9 |
| seas | 0.487193 | 0.496169 | 0.377266 | 0.826697 | 0.358569 | ~7.6 |
| shsa | 0.507249 | 0.473091 | 0.429758 | 0.820024 | 0.383616 | ~6.7 |
| eqas | 0.507395 | 0.477132 | 0.523149 | 0.836452 | 0.177092 | ~8.7 |

Feature diagnostics using ILAMB/GFED regions and allowed inputs showed:
- Wet/tropical overprediction regimes: CEAM, SEAS, EQAS, NHSA have high P_ann and/or high GPP where persistent moisture/canopy effects can quench fire.
- Hyperarid overprediction: MIDE has very high Dbar and low P_ann/GPP; dryness alone is not enough without fuel continuity.
- Savanna regions NHAF/SHAF are closer to observed amplitudes and should not be broadly suppressed.

## Final F3b regional impact

| Region | Baseline Overall | F3b Overall | Delta | Main interpretation |
|---|---:|---:|---:|---|
| global | 0.671529 | 0.676543 | +0.005014 | Bias/RMSE/spatial improved with tiny seasonal loss |
| tena | 0.381473 | 0.406672 | +0.025199 | Lower overprediction improves bias/RMSE |
| ceam | 0.376153 | 0.403003 | +0.026850 | Wet suppressor reduces major amplitude overprediction |
| shsa | 0.507249 | 0.543078 | +0.035829 | Amplitude improves despite slight spatial tradeoff |
| euro | 0.361128 | 0.376821 | +0.015693 | Bias/RMSE improve; spatial still poor |
| mide | 0.382769 | 0.408459 | +0.025690 | Arid fuel-discontinuity suppressor reduces desert overprediction |
| nhaf | 0.645855 | 0.652601 | +0.006746 | Spatial improves; amplitude remains acceptable |
| shaf | 0.646693 | 0.657096 | +0.010403 | Spatial improves |
| ceas | 0.670499 | 0.678107 | +0.007608 | RMSE/seasonal improve, small spatial loss |
| seas | 0.487193 | 0.509196 | +0.022003 | Wet suppressor reduces overprediction |
| eqas | 0.507395 | 0.628943 | +0.121548 | Strongest improvement; wet suppressor corrects severe overprediction and spatial failure |
| aust | 0.670219 | 0.670563 | +0.000344 | Essentially preserved |
| bona | 0.789806 | 0.777787 | -0.012019 | Tradeoff: lower spatial score in already-good low-fire boreal region |
| nhsa | 0.605824 | 0.602484 | -0.003340 | Tradeoff: wet suppressor reduces Amazon-adjacent spatial performance |
| boas | 0.728733 | 0.727964 | -0.000769 | Essentially preserved/slight loss |

Remaining unresolved failures:
- EURO/TENA/MIDE/CEAM still have very low spatial scores even after amplitude improvement. Likely missing land-use, cropland/fragmentation, human suppression/ignition, lightning, vegetation type, and subgrid fuel-continuity information, none of which are allowed inputs.
- AUST seasonal score remains low and appears tied to timing/regime details not solved by global wet/arid suppressors.
- Wet suppressor improves EQAS/SEAS/CEAM but can slightly damage NHSA and BONA/BOAS spatial distribution, reflecting the fact that annual P_ann is an imperfect proxy for canopy moisture and fire management.
