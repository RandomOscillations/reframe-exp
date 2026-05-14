# Workspace Manifest

Experiment: ED fire formal autoresearch run, Hermes harness.

Source:
- ED fire code copied from clean `ed-autoresearch` commit `1bac731`.
- Public TRENDY fire benchmark source available at `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source`, commit `f041ba3`.
- Prior pilot and operator-audit artifacts are archived outside this workspace and must not be used as evidence for this run.

Allowed model inputs:
- `data/crujra/dbar_monthly.npy`
- `data/crujra/p_ann_monthly.npy`
- `data/crujra/p_month_monthly.npy`
- `data/crujra/t_air_monthly.npy`
- `data/trendy_v14/EDv3_S3_gpp.nc`
- `data/gfed/GFED4.1s_2001.hdf5` through `data/gfed/GFED4.1s_2016.hdf5`
- Existing baseline source files in this workspace.

Allowed evaluation/reference artifacts:
- `ilamb/DATA/burntArea/GFED4.1S/burntArea.nc`
- `ilamb/burntArea_official.cfg`
- public TRENDY benchmark files under `/Users/adithyasrinivasan/Projects/creativity-docs/trendy-v14-fire-benchmark-source`
- `scripts/run_ilamb.sh`
- `scripts/run_official_regions.sh`
- `scripts/run_public_trendy_firepipe.sh`
- `scripts/verify.py`

Allowed research use:
- Web/literature search may be used for conceptual understanding of fire mechanisms.
- External information may inform hypotheses and explanations.

Disallowed model use:
- Do not add any new external data source as a model input.
- Do not use per-cell lookup tables.
- Do not use latitude/longitude hacks or coordinate-indexed correction maps.
- Do not route by named region or use per-region formulas.
- Do not add free residual coefficients whose main role is to absorb variance without a physical mechanism.
- Do not optimize by hiding regional damage behind global score gains.

Required live logs in this workspace:
- `research_log.md`
- `candidate_registry.md`
- `eval_log.md`
- `regional_analysis.md`
- `constraint_checks.md`
- `stuck_state.md` when local search is exhausted

