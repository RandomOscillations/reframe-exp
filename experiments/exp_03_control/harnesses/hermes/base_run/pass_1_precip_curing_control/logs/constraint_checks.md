# Constraint Checks

## Fixed input contract
Allowed inputs only:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- existing GFED/reference/evaluation files already present in workspace for scoring.

## Baseline C0
- Formula: original global Model C product of Dbar onset/suppression, annual/monthly precipitation, monthly GPP hump, and air-temperature ignition, raised to global exponent.
- Inputs: allowed fixed inputs only.
- No latitude/longitude terms in model formula.
- No named-region routing.
- No per-cell lookup tables.
- No external data.
- No residual correction coefficients.
- Official global/regional ILAMB run from regenerated artifact.
- Clean public benchmark run in `public_benchmark_clean`.

## Candidate H1 annual humid suppression
Formula factor:
`humid_supp(P_ann) = 1 / (1 + (P_ann / P_humid)^P_humid_q)`

Compliance assessment:
- Uses only allowed annual precipitation field.
- One global smooth factor with globally tuned parameters.
- Mechanistic interpretation: high annual rainfall limits burnability by wet fuels and lack of sustained curing; completes the upper wet limb of a pyrogeographic precipitation response.
- No region names, lat/lon, per-cell identity, lookup table, or residual correction.
- Official global and regional ILAMB completed for retuned H1 and mild ablation H1m.
- Rejected due global/spatial degradation.

## Candidate H2 wet-month logistic suppression
Formula factor:
`wet_supp(P_month) = 1 / (1 + exp(wet_k * (P_month - wet_c)))`

Compliance assessment:
- Uses only allowed monthly precipitation.
- One global smooth factor.
- Mechanistic interpretation: active burning is suppressed by wet fuels/rain during the current month, beyond the original hyperbolic monthly dampener.
- No forbidden routing/lookup/residual correction.
- Official global and regional ILAMB completed.
- Rejected due global spatial degradation.

## Candidate H3 seasonal contrast / curing gate
Formula factor:
`contrast_supp = 1 / (1 + (P_month / (P_ann/12 + contrast_eps))^contrast_q)`

Compliance assessment:
- Uses only allowed monthly and annual precipitation.
- One global smooth factor.
- Mechanistic interpretation: fire requires current-month dryness relative to local annual precipitation climatology; this captures curing/seasonal contrast without region labels.
- No forbidden routing/lookup/residual correction.
- Official global/regional and public benchmark completed.
- Rejected as final because C0 remains better globally and publicly, though H3 is a credible regional-compromise alternative.

## Candidate helper scripts
- `scripts/fire_explore.py` is an exploration helper. It mirrors Model C and writes candidate NetCDFs using only allowed inputs.
- Its proxy diagnostics are for search triage only; acceptance decisions used official ILAMB outputs.
