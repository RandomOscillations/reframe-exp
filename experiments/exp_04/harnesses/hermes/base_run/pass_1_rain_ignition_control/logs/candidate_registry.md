# Candidate Registry

| ID | Formula family | Status | Search | Mechanism | Key evidence |
|---|---|---|---|---|---|
| C0 | Original Model C | Baseline / best global so far | Existing 12 params | Dbar onset/suppression × annual precip floor × monthly precip dampening × GPP hump × air-temp ignition, ED annual-rate transform | Official global ILAMB Overall 0.6715; regional weaknesses logged in regional_analysis.md |
| C1-wet | wet_gpp_supp | Rejected/no-op | 500 Optuna broad full refit | Suppress high-GPP cells under wet annual precipitation | Best trial selected amp=0; identical to C0 |
| C1-annualP | annual_p_hump | Regional diagnostic, rejected as global replacement | 500 Optuna broad full refit | Annual precip supplies fuel at low values but suppresses fire in very wet climates | Official global Overall 0.6426; improves many worst regional aggregates but Spatial drops to 0.6287 |
| C1-rainT | rain_temp_shift | Regional diagnostic, rejected as global replacement | 500 Optuna broad full refit | Monthly rain raises ignition temperature threshold | Official global Overall 0.6568; improves Bias/RMSE and several regional failures but Seasonal/Spatial decline |
| C1-dry | dry_season_gate | Rejected/no-op | 500 Optuna broad full refit | Fire requires monthly dry anomaly relative to annual water supply | Best trial selected amp=0; identical to C0 |
| C1-base | base_refit | Rejected/no-op | 500 Optuna broad 12-param refit | Same Model C mechanisms | Best trial selected original params; supports local optimality of C0 under proxy |
| C2-annualWet | annual_wet_amp | Rejected/global, useful diagnostic | 1000 Optuna targeted fixed-core gate | High annual precipitation suppresses spread; optional rate-power compression | Official Overall 0.668582; regional improvements but global Spatial loss |
| C2-wetGPP | wet_gpp_amp | Tied global diagnostic | 1000 Optuna targeted fixed-core gate | Wet/high-GPP live-fuel or closed-canopy suppression | Official Overall 0.671533 vs C0 0.671529; regional improvements, but tiny global gain and Spatial loss |
| C2-rainIgn | rain_ignition_shift | Accepted best local official candidate | 1000 Optuna targeted fixed-core gate | Monthly precipitation raises effective ignition temperature; rate-power compression | Official Overall 0.675267, regional improvements in worst regions; public benchmark rank #2 behind public ED baseline by 0.000065 |
| C2-combined | combined_wet_rain | Rejected by parsimony | 1000 Optuna targeted fixed-core combined gate | Annual wet suppression + wet-GPP suppression + rain-conditioned ignition | Official Overall 0.673055; lower than rain-only with much more complexity |
| C2-ablate-power | rate_power_only | Rejected ablation | deterministic from C2-rain `rate_power` only | Intensity compression without rain physics | Official Overall 0.661221 |
| C2-ablate-rain | rain_no_power | Rejected ablation | deterministic from C2-rain rain gate, rate_power=1 | Rain-conditioned ignition without intensity compression | Official Overall 0.660225 |
