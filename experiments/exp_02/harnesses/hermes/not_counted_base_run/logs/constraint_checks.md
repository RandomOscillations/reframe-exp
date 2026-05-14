# Constraint Checks

## Input contract
Allowed inputs from WORKSPACE_MANIFEST.md:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- Existing masks/reference data for reproduction and evaluation only.

No candidate used external datasets as model inputs. No candidate used latitude/longitude, named region IDs, per-cell lookup tables, per-region formulas, direct cell-identity residual fitting, or arbitrary residual correction coefficients.

## Candidate mechanism compliance
| Candidate/family | Added inputs? | Region/cell routing? | One global formula? | Mechanistic interpretation | Status |
|---|---|---|---|---|---|
| C1 lagged GPP | No; temporal transform of GPP | No | Yes | fuel persistence | compliant, rejected |
| C2 dryrate | No; temporal transform of Dbar | No | Yes | active curing / dry-down flammability | compliant, useful |
| C3 wetdry | No; temporal transform of precipitation | No | Yes | antecedent fuel from wet-season precipitation | compliant, rejected as near-identity |
| C6/C6b humid suppression | No; smooth transform of annual precipitation | No | Yes | persistent wet-fuel / humid evergreen suppression | compliant, accepted/regional best |
| C7 humid+dryrate | No; annual precip + Dbar temporal transform | No | Yes | humid wet-fuel ceiling plus active dry-down | compliant, final balanced model |

## Final C7 formula compliance
C7 uses only:
- Original Model C allowed fields: Dbar, P_ann, P_month, GPP_month, T_air.
- `Dbar - mean(Dbar previous 3 months)`, a global temporal transform of Dbar.
- A smooth annual-precipitation humid gate.

The formula is global and continuous/smooth except for the existing ED rate cap in the output transform. It contains no region-specific constants, cell-specific tables, latitude/longitude terms, or learned residuals.

## Evaluation compliance
Serious candidates C2, C6/C6b/C6d, and C7 received official global and regional ILAMB. C7 received a clean public TRENDY/firepipe comparison. C6b and C6d served as ablations for the humid-suppression complexity; C5 served as broad retune ablation for dryrate. Logs and final_report.md were written.
