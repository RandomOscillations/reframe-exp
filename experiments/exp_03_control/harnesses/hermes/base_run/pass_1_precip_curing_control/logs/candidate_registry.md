# Candidate Registry

| ID | Formula family | Added mechanism(s) | Search/diagnostics | Official global | Official regional outcome | Public benchmark | Decision |
|---|---|---|---|---|---|---|---|
| C0 | Original Model C | None | Original 12-param baseline reproduced | Overall 0.6715; Bias 0.7281; RMSE 0.5058; Seasonal 0.8457; Spatial 0.7724 | Weak: EURO 0.3611, CEAM 0.3762, TENA 0.3815, MIDE 0.3828, SEAS 0.4872, SHSA 0.5072, EQAS 0.5074 | Clean public: Overall 0.6713, tied with copied `ED-ModelC-baseline`, rank #1 above CLASSIC 0.6660 and CLM6.0 0.6606 | Retain as best global/public model |
| H1 | Annual humid suppression with retuned base | `1/(1+(P_ann/P_humid)^q)` | Optuna 500 full-field proxy trials; best `P_humid=2414.9`, `q=4.535`, plus retuned selected base params | Overall 0.6384; Bias 0.7243; RMSE 0.5173; Seasonal 0.8496; Spatial 0.5837 | Large weak-region gains (e.g. EQAS 0.6801, SHSA 0.6404, EURO 0.5173) but harms Africa/boreal/spatial | Not run; rejected before public due global/spatial collapse | Reject: mechanism helps humid regional bias but over-suppresses/warps global spatial distribution |
| H1m | Mild annual humid suppression ablation on fixed C base | Same as H1 with `P_humid=1500`, `q=0.5` | Deterministic grid ablation over P_humid/q on fixed base | Overall 0.6538; Spatial 0.6828 | Moderate weak-region gains (e.g. EQAS 0.5694, SHSA 0.5755, SEAS 0.5377) but weaker than C0 globally | Not run; rejected before public | Reject: regional improvements not worth -0.0177 global Overall and -0.0896 Spatial |
| H2 | Wet-month logistic suppression | `supp(P_month; wet_k, wet_c)` added to Model C | Deterministic grid over wet_k/wet_c on fixed base; best proxy at wet_k=0.1, wet_c=20 | Overall 0.6534; Seasonal 0.8521; Spatial 0.6524 | Improves weak-region bias/overall (EURO 0.4932, EQAS 0.6268) but hurts boreal/spatial | Not run; rejected before public | Reject: good timing/seasonality but spatial loss too large |
| H3 | Seasonal contrast / curing gate | `1/(1+(P_month/(P_ann/12+eps))^q)` | Deterministic grid over eps/q on fixed base; best proxy eps=0.5, q=0.25 | Overall 0.6654; Bias 0.7304; RMSE 0.5110; Seasonal 0.8480; Spatial 0.7267 | Best compromise candidate: weak regions improve, but C0 still better globally/spatially | Clean public: Overall 0.6652; below Model C 0.6713 and CLASSIC 0.6660, above CLM6.0 0.6606 | Reject as final global model; record as regional-compromise alternative only |

Artifacts:
- Candidate score table: `artifacts/official_candidate_regional_scores.csv`
- H1 params: `models/H1_annual_humid_supp/params.json`
- H1m params: `models/H1m_mild_humid/params.json`
- H2 params: `models/H2_wetmonth/params.json`
- H3 params: `models/H3_seasonal_contrast/params.json`
