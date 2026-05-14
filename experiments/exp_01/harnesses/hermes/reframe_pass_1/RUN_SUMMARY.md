# Reframe Pass 1

Hermes profile: `adireframe1`

Workspace source:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/reframe`

Prompt:
`prompt/reframe_fresh_run_prompt.md`

## Result

Final accepted model: `F3b`, original Model C plus two pruned global suppressors:

- wet/canopy-moisture suppressor from annual precipitation;
- hyperarid fuel-discontinuity suppressor from `Dbar / (P_ann + ratio_p0)`.

Official global ILAMB:

| Model | Overall |
|---|---:|
| Baseline Model C | 0.671529 |
| Final F3b | 0.676543 |
| Delta | +0.005014 |

Public TRENDY/firepipe:

| Model | Overall | Produced-table rank |
|---|---:|---:|
| ED-ModelC-formal-candidate | 0.676313 | 1 |

Weak-region average improved from `0.429051` to `0.468025`, a delta of `+0.038973`.

## Contents

- `logs/`: agent-authored markdown logs and `final_report.md`.
- `candidates/`: Optuna/search candidate JSONs.
- `model/`: final formula documentation and parameter JSONs.
- `scripts/`: scripts changed or created by the agent for this pass.
- `official_ilamb/`: compact official ILAMB CSV/JSON/log outputs.
- `public_trendy/`: compact public TRENDY/firepipe CSV/JSON/log outputs.
- `metadata/`: governing workspace docs read by the agent.

## Excluded

Heavy generated artifacts are intentionally not committed here:

- `ilamb/MODELS/*/*.nc`
- ILAMB `.pkl` files
- `out_terms/*.nc`
- full copied data directories

The compact CSV/JSON/log outputs are enough for paper evidence and comparison. Full artifacts remain in the local workspace and benchmark directories listed above.
