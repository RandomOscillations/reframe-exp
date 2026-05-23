# Candidate Registry

| Candidate | Mechanism family | Search | Official global Overall | Regional diagnostic | Decision |
|---|---|---:|---:|---:|---|
| ED-ModelC-final | Original Model C | Baseline reproduction | 0.671529 | mean derived regional 0.560591; min 0.361275 | Best global / final selected |
| ED-ModelC-base_refit | Same formula, global+regional proxy refit | 500 Optuna trials | 0.648144 | mean 0.590194; min 0.403365 | Rejected: regional improvement but large global loss |
| ED-ModelC-precip_shape | Adds global exponents on precipitation floor/dampening | 500 Optuna trials | 0.646299 | mean 0.615108; min 0.357003 | Rejected as final: best regional mean but large global loss |
| ED-ModelC-temp_window | Adds high-temperature suppression window | 500 Optuna trials | 0.659200 | mean 0.589537; min 0.364386 | Rejected: closest candidate globally, still -0.012329 Overall |
| ED-ModelC-humid_suppression | Adds annual-precip humid suppression | 500 Optuna trials | 0.649253 | mean 0.601833; min 0.347296 | Rejected: regional gains but global loss |
| ED-ModelC-fuel_moisture_balance | Adds dryness relief of monthly precipitation dampening | 500 Optuna trials | 0.657146 | mean 0.594038; min 0.421151 | Rejected: best worst-region repair, but global loss |

## Artifact paths
- Search summary: `experiments/modelC_mechanism_search/summary.json`
- Official global score table: `experiments/modelC_mechanism_search/official_global_scores.csv`
- Official regional score table: `experiments/modelC_mechanism_search/official_regional_scores.csv`
- Proxy ablations: `experiments/modelC_mechanism_search/proxy_ablation_scores.csv`
- Candidate NetCDFs: `ilamb/MODELS/ED-ModelC-*/burntArea.nc`
