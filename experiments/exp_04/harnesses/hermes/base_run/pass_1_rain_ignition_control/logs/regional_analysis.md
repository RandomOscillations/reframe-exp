# Regional Analysis

## C0 original Model C official regional ILAMB triage

Regional components from `ilamb/output_modelC_regions/scalar_database.csv`. Diagnostic regional aggregate is `(2*Bias + 2*RMSE + Seasonal + Spatial)/6` because ILAMB did not write regional Overall Score rows.

| Region | Bias | RMSE | Seasonal | Spatial | Diagnostic aggregate | Main failure |
|---|---:|---:|---:|---:|---:|---|
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3613 | Severe bias/RMSE and spatial failure despite good phase |
| euro | 0.3935 | 0.2618 | 0.8082 | 0.0805 | 0.3665 | Severe spatial/RMSE failure; likely low-fire human/land-use/cropland behavior not captured by climate/GPP only |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3907 | Poor spatial and RMSE; temperate mixed regimes |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3918 | Poor spatial/RMSE; arid fuel limitation or irrigated/cropland mismatch |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4887 | Wet/high-productivity suppression and spatial mismatch |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5016 | Bias/RMSE and spatial mismatch |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5024 | Wet rainforest/peat/cropland heterogeneity; spatial failure |
| nhsa | 0.5014 | 0.4931 | 0.9144 | 0.6270 | 0.5884 | Moderate bias/RMSE, strong phase |
| shaf | 0.7597 | 0.5023 | 0.9021 | 0.5671 | 0.6655 | Reasonable but RMSE/spatial still weak |
| nhaf | 0.7693 | 0.4795 | 0.9010 | 0.5998 | 0.6664 | Good bias/phase, RMSE/spatial opportunity |
| global | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6810 | Official Overall 0.6715; global score hides regional failures |
| aust | 0.7456 | 0.6520 | 0.5795 | 0.7219 | 0.6828 | Seasonal phase weak despite decent bias/spatial |
| ceas | 0.7834 | 0.5603 | 0.7222 | 0.7265 | 0.6893 | Seasonal/RMSE opportunity |
| boas | 0.8408 | 0.6192 | 0.7966 | 0.7679 | 0.7474 | Generally strong |
| bona | 0.8840 | 0.7425 | 0.9251 | 0.6549 | 0.8055 | Strongest macro-region |

Initial hypotheses from regional failure pattern:
1. Wet/high-GPP suppression: Model C may over-burn wet productive regions because GPP hump and annual precip floor do not fully express live-fuel moisture/rainforest/cropland suppression.
2. Annual precipitation hump: annual precipitation should supply fuel at low values but suppress fire in very wet climates; Model C's annual term is monotone increasing.
3. Rain-temperature ignition coupling: wet months may require higher air temperature to ignite/spread; Model C multiplies independent monthly precip dampening and temperature ignition.
4. Dry-season relative anomaly gate: fire depends on being dry relative to local annual water supply, not merely low absolute monthly precipitation.

## Best final candidate regional behavior: ED-C2-rain_ignition_shift

Official components from `ilamb/output_C2_rainign_regions/scalar_database.csv`. Diagnostic aggregate is the same tier-style regional diagnostic used for C0.

| Region | C0 diag | C2-rain diag | Change | Main change |
|---|---:|---:|---:|---|
| ceam | 0.3613 | 0.4281 | +0.0668 | Bias/RMSE/spatial all improve; seasonal slightly lower |
| euro | 0.3665 | 0.5335 | +0.1670 | Large bias/RMSE gain; spatial still low |
| tena | 0.3907 | 0.4652 | +0.0745 | Bias/RMSE improve; spatial modestly improves |
| mide | 0.3918 | 0.4249 | +0.0331 | Bias/RMSE/spatial improve from very weak base |
| seas | 0.4887 | 0.5151 | +0.0264 | Bias/RMSE improve; spatial slightly lower than desired |
| shsa | 0.5016 | 0.5327 | +0.0311 | Bias/RMSE/spatial improve; seasonal lower |
| eqas | 0.5024 | 0.5598 | +0.0574 | Bias/RMSE/spatial improve; seasonal lower |
| nhsa | 0.5884 | 0.6030 | +0.0146 | Bias improves; spatial/seasonal slightly lower |
| shaf | 0.6655 | 0.6528 | -0.0127 | Southern Africa worsens slightly; main accepted tradeoff |
| nhaf | 0.6664 | 0.6748 | +0.0084 | Slight spatial gain |

Interpretation: the rain-conditioned ignition threshold directly targets weak wet/temperate regions without named-region routing. It improves all initially worst regions, but some already-strong dry savanna regions lose a little spatial/seasonal fidelity. The remaining failures (mide/ceam still below 0.43, euro spatial still low) likely require land-use/cropland/human ignition/suppression or fuel-structure information not available under the fixed input contract.
