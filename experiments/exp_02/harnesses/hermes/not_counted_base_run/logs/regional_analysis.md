# Regional Analysis

## Baseline official regional ILAMB (Model C)
| Region | Overall | Bias | RMSE | Seasonal | Spatial | Obs period mean % | Main failure signal |
|---|---:|---:|---:|---:|---:|---:|---|
| global | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | 0.611164 | strong seasonal/global; spatial lower than CLM6/classic |
| bona | 0.789806 | 0.883981 | 0.742535 | 0.925121 | 0.654858 | 0.043941 | strong; low-fire boreal magnitude ok |
| tena | 0.381473 | 0.437076 | 0.307975 | 0.694036 | 0.160304 | 0.374298 | weak spatial + RMSE; temperate N. America fire placement/magnitude |
| ceam | 0.376153 | 0.286887 | 0.310422 | 0.847470 | 0.125564 | 0.751810 | severe bias/RMSE/spatial despite good seasonality |
| nhsa | 0.605824 | 0.501408 | 0.493150 | 0.914425 | 0.626989 | 0.841181 | seasonality strong; magnitude moderate |
| shsa | 0.507249 | 0.473091 | 0.429758 | 0.820024 | 0.383616 | 0.944540 | magnitude/spatial deficits |
| euro | 0.361128 | 0.393450 | 0.261763 | 0.808165 | 0.080499 | 0.288168 | worst spatial/RMSE; likely missing human/cropland fragmentation under allowed inputs |
| mide | 0.382769 | 0.436689 | 0.310067 | 0.765840 | 0.091179 | 0.341438 | hyperarid/agricultural sparse-fire spatial failure |
| nhaf | 0.645855 | 0.769337 | 0.479548 | 0.901029 | 0.599810 | 1.428940 | high-fire savanna good, RMSE limiting |
| shaf | 0.646693 | 0.759732 | 0.502274 | 0.902122 | 0.567063 | 1.429480 | high-fire savanna good, spatial/RMSE limiting |
| boas | 0.728733 | 0.840753 | 0.619204 | 0.796639 | 0.767865 | 0.073153 | strong |
| ceas | 0.670499 | 0.783351 | 0.560258 | 0.722163 | 0.726466 | 0.258832 | decent, seasonal lower |
| seas | 0.487193 | 0.496169 | 0.377266 | 0.826697 | 0.358569 | 1.036140 | tropical/monsoon spatial and RMSE |
| eqas | 0.507395 | 0.477132 | 0.523149 | 0.836452 | 0.177092 | 0.307191 | severe spatial failure in equatorial Asia |
| aust | 0.670219 | 0.745626 | 0.652014 | 0.579524 | 0.721918 | 0.511498 | main deficit is seasonal phase/timing |

## Serious candidate regional Overall table
| Region | Baseline | C2 dryrate | C6b humid | C7 humid+dry | Best delta vs baseline |
|---|---:|---:|---:|---:|---:|
| bona | 0.789806 | 0.787680 | 0.789910 | 0.788504 | +0.000104 |
| tena | 0.381473 | 0.387950 | 0.385201 | 0.387201 | +0.006477 |
| ceam | 0.376153 | 0.388136 | 0.394321 | 0.395297 | +0.019144 |
| nhsa | 0.605824 | 0.612135 | 0.612635 | 0.614489 | +0.008665 |
| shsa | 0.507249 | 0.514548 | 0.529248 | 0.524389 | +0.021999 |
| euro | 0.361128 | 0.368368 | 0.362372 | 0.366309 | +0.007240 |
| mide | 0.382769 | 0.385654 | 0.382955 | 0.384436 | +0.002885 |
| nhaf | 0.645855 | 0.647620 | 0.646670 | 0.648910 | +0.003055 |
| shaf | 0.646693 | 0.644307 | 0.645391 | 0.643847 | -0.001302 |
| boas | 0.728733 | 0.730300 | 0.728764 | 0.729999 | +0.001567 |
| ceas | 0.670499 | 0.674705 | 0.670835 | 0.672759 | +0.004206 |
| seas | 0.487193 | 0.496964 | 0.505065 | 0.505368 | +0.018175 |
| eqas | 0.507395 | 0.526712 | 0.589676 | 0.574394 | +0.082281 |
| aust | 0.670219 | 0.670222 | 0.668985 | 0.669813 | +0.000003 |

## Interpretation
- Humid annual-precipitation suppression is the clearest regional mechanism: it substantially improves EQAS, SEAS, SHSA, CEAM, and NHSA by reducing over-burning / misplacement in persistently wet climates while preserving seasonal savanna behavior.
- Active dry-down improves seasonal timing and weak dry/temperate regions but costs some global Spatial Distribution and SHAF.
- C7 is the best balanced global model; C6b is the best regional humid-tropical/EQAS model.
- Remaining failures: EURO/MIDE/CEAM/TENA spatial scores remain very low, and AUST seasonal score remains poor. These are likely controlled by unavailable human land-use/suppression/ignition and finer vegetation/fire-management variables rather than by smooth transforms of the five allowed drivers.
