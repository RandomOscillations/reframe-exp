# Regional Analysis

## Official regional ILAMB baseline: original Model C
Regional ILAMB was run over ILAMB's built-in GFED regions:
`bona tena ceam nhsa shsa euro mide nhaf shaf boas ceas seas eqas aust`.

Output: `ilamb/output_modelC_regions/scalar_database.csv`

ILAMB emitted regional component scores but not regional `Overall Score`. The table below includes a derived diagnostic Overall using the same tier-2 aggregation used globally: `(2*Bias + 2*RMSE + Seasonal + Spatial)/6`. The official evidence is the component scores.

| Region | Bias | RMSE | Seasonal | Spatial | Derived Overall | Initial triage |
|---|---:|---:|---:|---:|---:|---|
| ceam | 0.286887 | 0.310422 | 0.847470 | 0.125564 | 0.361275 | Very poor bias/RMSE/spatial despite good seasonality; likely magnitude/spatial allocation failure in Central America. |
| euro | 0.393450 | 0.261763 | 0.808165 | 0.080499 | 0.366842 | Weakest spatial/RMSE; small-fire/high-human-management region may be poorly represented under limited inputs. |
| mide | 0.436689 | 0.310067 | 0.765840 | 0.091179 | 0.391755 | Poor spatial and magnitude in arid/semiarid transition. |
| tena | 0.437076 | 0.307975 | 0.694036 | 0.160304 | 0.390740 | Poor magnitude and spatial, weaker seasonality than most regions. |
| shsa | 0.473091 | 0.429758 | 0.820024 | 0.383616 | 0.501556 | Moderate; bias/RMSE/spatial need improvement. |
| seas | 0.496169 | 0.377266 | 0.826697 | 0.358569 | 0.488689 | Moderate-low; tropical/monsoon humid behavior may need precipitation/moisture mechanism. |
| eqas | 0.477132 | 0.523149 | 0.836452 | 0.177092 | 0.502034 | Good RMSE/seasonal but weak spatial; humid-region spatial allocation issue. |
| nhsa | 0.501408 | 0.493150 | 0.914425 | 0.626989 | 0.588922 | Good seasonality/spatial, moderate magnitude. |
| aust | 0.745626 | 0.652014 | 0.579524 | 0.721918 | 0.682787 | Strong magnitude/spatial but poor seasonality; candidate mechanisms must not damage this region. |
| shaf | 0.759732 | 0.502274 | 0.902122 | 0.567063 | 0.665533 | Good seasonal/bias, moderate RMSE/spatial. |
| nhaf | 0.769337 | 0.479548 | 0.901029 | 0.599810 | 0.666435 | Similar to SHAF; central to global score. |
| ceas | 0.783351 | 0.560258 | 0.722163 | 0.726466 | 0.690975 | Strong spatial/bias, moderate seasonality/RMSE. |
| boas | 0.840753 | 0.619204 | 0.796639 | 0.767865 | 0.747403 | Strong. |
| bona | 0.883981 | 0.742535 | 0.925121 | 0.654858 | 0.805502 | Best regional behavior. |

## Failure pattern summary
- Model C is globally strong because global seasonal phase and large-fire regions are well represented.
- Weak regions cluster into:
  1. low/spatially heterogeneous fire regions with low spatial scores (EURO, MIDE, CEAM, TENA),
  2. humid/monsoon tropical regions with spatial allocation issues (EQAS, SEAS),
  3. Australia with good magnitude/spatial but poor seasonality.
- The first search wave targeted mechanisms that alter cell behavior by physically allowed state variables: precipitation-shape, humid suppression, heat-window suppression, and dry-season fuel/moisture balance.

## Candidate regional outcomes
Official regional component scores were summarized in:
`experiments/modelC_mechanism_search/official_regional_scores.csv`

Derived regional means:
| Model | Mean | Min | Max | Interpretation |
|---|---:|---:|---:|---|
| ED-ModelC-precip_shape | 0.615108 | 0.357003 | 0.782779 | Best average regional diagnostic; repairs EURO/EQAS/SEAS/SHSA but damages global spatial enough to reject as final. |
| ED-ModelC-humid_suppression | 0.601833 | 0.347296 | 0.728462 | Strong CEAM/NHSA/AUST improvements but global loss and weak worst-region. |
| ED-ModelC-fuel_moisture_balance | 0.594038 | 0.421151 | 0.701360 | Best worst-region repair and best TENA/MIDE among candidates, but global loss remains too large. |
| ED-ModelC-base_refit | 0.590194 | 0.403365 | 0.726535 | Refit alone improves regional mean, showing tradeoff frontier rather than new mechanism success. |
| ED-ModelC-temp_window | 0.589537 | 0.364386 | 0.775945 | Closest global candidate but not a regional step-function. |
| ED-ModelC-final | 0.560591 | 0.361275 | 0.805502 | Best global; regional weaknesses remain. |

Best-by-region diagnostics show no single candidate dominates: original Model C remains best in BONA, NHAF, and SHAF; precipitation-shape helps BOAS/EQAS/EURO/SEAS/SHSA; humid suppression helps AUST/CEAM/NHSA; fuel-moisture balance helps MIDE/TENA. This split suggests unresolved processes differ by region, but the fixed input contract lacks land management, lightning/human ignition, vegetation type, and suppression information needed to separate those failures mechanistically without prohibited routing.
