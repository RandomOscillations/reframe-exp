# Base Prompt Run

Hermes profile: formal base run profile from archived session.

Workspace source:
`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-13_181113__ed_fire_exp01_hermes_base_prompt_completed_run/exp-workspaces/exp_01/hermes/base`

Prompt:
`prompt/base_fresh_run_prompt.md`

## Result

Final accepted model: original Model C.

The highest scalar-score candidate was `LAG-FUEL-v1`, but it was rejected because the small global gain hid regional damage.

Official global ILAMB:

| Model | Overall | Bias | RMSE | Seasonal | Spatial | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Original Model C | 0.671529 | 0.728089 | 0.505759 | 0.845690 | 0.772351 | accepted |
| WET-SUPP-v1 | 0.671384 | 0.729325 | 0.506214 | 0.845835 | 0.769334 | rejected |
| LAG-FUEL-v1 | 0.672274 | 0.727752 | 0.505788 | 0.850890 | 0.771151 | rejected |
| LAG+WET-v1 | 0.672173 | 0.728988 | 0.506241 | 0.850932 | 0.768463 | rejected |
| PRECIP-MEM-v1 | 0.670193 | 0.728316 | 0.506595 | 0.846707 | 0.762754 | rejected |

Public TRENDY/firepipe:

| Model | Overall | Produced-table rank |
|---|---:|---:|
| ED-ModelC-baseline-formal | 0.671274 | 1 before rejected candidate |
| ED-ModelC-lag-fuel-pure-v1 | 0.672014 | 1 in candidate table |

## Candidate Families

- `WET-SUPP-v1`: annual wetness/perhumid suppression.
- `LAG-FUEL-v1`: antecedent/cured GPP fuel.
- `LAG+WET-v1`: lagged fuel plus wetness suppression.
- `PRECIP-MEM-v1`: antecedent precipitation memory.

## Contents

- `logs/`: agent-authored markdown logs and `final_report.md`.
- `candidates/`: candidate/search JSONs.
- `model/`: restored final Model C formula and parameter JSONs.
- `scripts/`: scripts changed or created by the agent for this run.
- `official_ilamb/`: compact official ILAMB CSV/JSON/log outputs.
- `public_trendy/`: compact public TRENDY/firepipe CSV/JSON/log outputs.
- `metadata/`: governing workspace docs read by the agent.
- `prompt/`: recorded base prompt.

## Excluded

Heavy generated artifacts are intentionally not committed here:

- `ilamb/MODELS/*/*.nc`
- ILAMB `.pkl` files
- `out_terms/*.nc`
- full copied data directories

The compact CSV/JSON/log outputs are enough for paper evidence and comparison. Full artifacts remain in the archived workspace listed above.
