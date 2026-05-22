# Constraint Checks

## Global constraints for all candidates

Allowed inputs:
- data/crujra/dbar_monthly.npy
- data/crujra/p_ann_monthly.npy
- data/crujra/p_month_monthly.npy
- data/crujra/t_air_monthly.npy
- data/trendy_v14/EDv3_S3_gpp.nc
- existing GFED/reference/evaluation files in this workspace for scoring only

Forbidden and compliance status:
- No external data as model input: compliant so far.
- No latitude/longitude hacks: compliant so far; latitude cosine is used only for benchmark-style weighting, not model formula.
- No per-cell lookup tables: compliant so far.
- No named-region routing or per-region formulas: compliant so far.
- No arbitrary residual correction coefficients: compliant so far.
- No direct cell-identity fitting to GFED: compliant so far.
- No prior/archive experiment evidence outside this workspace: compliant so far.

C0 baseline formula compliance:
- One global formula: yes.
- Inputs only from allowed fields: yes.
- Mechanistic interpretation: dbar ignition onset and hyperarid suppression; annual precip fuel floor; monthly precip dampening; GPP productivity hump; air-temperature ignition; ED annual-rate saturation/monthly transform.

Candidate search harness reviewed: `scripts/research_model_variants.py` defines global formula families using only allowed inputs and writes candidate artifacts under `models/research/<MODEL_NAME>/` and `ilamb/MODELS/<MODEL_NAME>/`. The predefined macroregion scoring inside the harness is diagnostic/objective weighting only; it is not a model input and must not be used to route formulas.

Final accepted candidate C2-rain compliance:
- One global formula: yes.
- Inputs: original Model C allowed inputs only; C2-rain uses monthly precipitation and monthly air temperature to condition ignition.
- No region/cell routing: yes, no named regions or coordinates in the formula.
- No external data: yes.
- No per-cell lookup or residual fitting: yes.
- Mechanistic terms: rain/humidity raises effective ignition threshold; rate_power is a global intensity/patchiness compression analogous to Model C's existing global exponent.
- Ablations support mechanism: rate_power alone and rain-conditioned ignition alone both reduce official Overall substantially; the accepted gain requires the combined physically motivated change.

Caveat: C2-rain improves local official global ILAMB and many regional failures, but in the public benchmark root it is slightly below the included ED-ModelC-baseline by 0.000065. It should therefore be framed as a defensible mechanistic candidate and regional/global tradeoff improvement in the local official run, not an unequivocal public leaderboard replacement.
