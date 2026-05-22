# Regional Analysis

Official regional ILAMB for original Model C (C0), output `ilamb/output_modelC_regions/scalar_database.csv`.

| Region | Bias | RMSE | Seasonal | Spatial | Overall | Initial interpretation |
|---|---:|---:|---:|---:|---|
| euro | 0.3934 | 0.2618 | 0.8082 | 0.0805 | 0.3611 | Very low spatial and RMSE; likely over/fire placement issues in low-fire fragmented region. |
| ceam | 0.2869 | 0.3104 | 0.8475 | 0.1256 | 0.3762 | Bias and spatial very weak despite good seasonality; humid/tropical suppression likely missing. |
| tena | 0.4371 | 0.3080 | 0.6940 | 0.1603 | 0.3815 | Low spatial/RMSE and moderate seasonality; fire placement and overprediction in temperate mosaic. |
| mide | 0.4367 | 0.3101 | 0.7658 | 0.0912 | 0.3828 | Very low spatial; arid/irrigated/low-fuel constraints not captured by allowed inputs. |
| seas | 0.4962 | 0.3773 | 0.8267 | 0.3586 | 0.4872 | Humid monsoon region; reasonable seasonality but poor magnitude/spatial. |
| shsa | 0.4731 | 0.4298 | 0.8200 | 0.3836 | 0.5072 | Bias/spatial weak; may need better annual precipitation or productivity upper suppression. |
| eqas | 0.4771 | 0.5231 | 0.8365 | 0.1771 | 0.5074 | Humid tropical spatial failure; high-rainfall suppression hypothesis. |
| nhsa | 0.5014 | 0.4932 | 0.9144 | 0.6270 | 0.6058 | Good seasonality/spatial, bias still weak. |
| nhaf | 0.7693 | 0.4795 | 0.9010 | 0.5998 | 0.6459 | Strong seasonal, acceptable regional behavior. |
| shaf | 0.7597 | 0.5023 | 0.9021 | 0.5671 | 0.6467 | Strong seasonal, acceptable regional behavior. |
| aust | 0.7456 | 0.6520 | 0.5795 | 0.7219 | 0.6702 | Good bias/RMSE/spatial; seasonality comparatively weak. |
| ceas | 0.7834 | 0.5603 | 0.7222 | 0.7265 | 0.6705 | Good bias/spatial; moderate seasonality/RMSE. |
| boas | 0.8408 | 0.6192 | 0.7966 | 0.7679 | 0.7287 | Strong. |
| bona | 0.8840 | 0.7425 | 0.9251 | 0.6549 | 0.7898 | Best regional behavior. |
| global | 0.7281 | 0.5058 | 0.8457 | 0.7724 | 0.6715 | Baseline rank-1 global model. |

Triage summary:
- The baseline's global score is strong because Bias and Seasonal are high, and global Spatial is good.
- Weak regional behavior clusters in regions with low observed burned area and/or humid/fragmented burning (EURO, CEAM, TENA, MIDE, SEAS, EQAS, SHSA).
- Many weak regions have acceptable/high Seasonal score, so the primary missing mechanism is unlikely to be timing alone.
- Main targets are reducing regional overprediction and improving spatial distribution without sacrificing African savanna, boreal, Central Asia, and global performance.

## Candidate regional comparison

Overall Score by weak region and global (official ILAMB):

| Region | C0 | H1 retuned humid | H1m mild humid | H2 wet-month | H3 seasonal contrast |
|---|---:|---:|---:|---:|---:|
| euro | 0.3611 | 0.5173 | 0.4096 | 0.4932 | 0.4198 |
| ceam | 0.3762 | 0.5039 | 0.4269 | 0.4327 | 0.4104 |
| tena | 0.3815 | 0.4727 | 0.4258 | 0.4865 | 0.4289 |
| mide | 0.3828 | 0.4191 | 0.4101 | 0.4089 | 0.4115 |
| seas | 0.4872 | 0.5749 | 0.5377 | 0.5272 | 0.5149 |
| shsa | 0.5072 | 0.6404 | 0.5755 | 0.5844 | 0.5551 |
| eqas | 0.5074 | 0.6801 | 0.5694 | 0.6268 | 0.5525 |
| global | 0.6715 | 0.6384 | 0.6538 | 0.6534 | 0.6654 |

Interpretation:
- All three added precipitation/curing mechanisms improve the targeted weak regions, confirming that Model C is missing some wet-fuel/curing limitation in regional low-fire/humid areas.
- The improvements consistently trade off against global Spatial Distribution. H1 retuned is the clearest example: large regional gains but global Spatial falls from 0.7724 to 0.5837.
- H3 is the least damaging compromise: it raises weak regions modestly and preserves global Overall 0.6654, but still loses -0.0061 Overall and -0.0457 Spatial against C0, and public benchmark falls below CLASSIC.
- Remaining regional failures appear unresolved under current allowed inputs because the weak regions likely require information not available in the fixed contract: land use/cropland/pasture fragmentation, human suppression/ignition, fuel continuity, peat/deforestation fires, and sub-grid vegetation structure. Smooth precipitation-only global gates can reduce magnitude but cannot place fire correctly without damaging savanna/boreal spatial skill.
