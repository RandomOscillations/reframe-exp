# Workspace Manifest

This workspace starts from original Model C at ED autoresearch source commit `1bac731`.

## Allowed Model Inputs

The model may use only the existing inputs already present in this workspace:

- `data/crujra/dbar_monthly.npy`: annual dryness accumulator on the monthly grid.
- `data/crujra/p_ann_monthly.npy`: annual precipitation aligned to monthly samples.
- `data/crujra/p_month_monthly.npy`: current-month precipitation.
- `data/crujra/t_air_monthly.npy`: current-month air temperature.
- `data/trendy_v14/EDv3_S3_gpp.nc`: monthly EDv3 GPP.
- Existing masks/reference data used by the baseline reproduction and ILAMB evaluation.

These inputs may be transformed into interpretable physical quantities such as seasonality, lagged fuel, drying rate, precipitation concentration, inferred fuel limitation, inferred moisture limitation, or smooth latent fire-regime gates.

## Disallowed Model Inputs And Shortcuts

Do not use:

- new external datasets as model inputs,
- latitude/longitude hacks,
- named-region IDs or named-region routing,
- per-cell lookup tables,
- per-region formulas,
- arbitrary residual correction coefficients,
- direct fitting to GFED by cell identity.

## Evaluation Assets

Important local paths:

- Baseline model output: `ilamb/MODELS/ED-ModelC-final/burntArea.nc`
- Official ILAMB config: `ilamb/burntArea_official.cfg`
- Public TRENDY/firepipe benchmark root: `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source`

Helper commands:

- `scripts/run_ilamb.sh`: official global ILAMB for current workspace model.
- `scripts/run_official_regions.sh`: official regional ILAMB for current workspace model.
- `scripts/run_public_trendy_firepipe.sh`: public TRENDY/firepipe benchmark comparison for serious candidates.
