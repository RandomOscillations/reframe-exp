# Reframe Pass 2 Continuation

Hermes profile: `adireframe1`

Workspace source:
`/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/reframe`

Prompt:
`prompt/reframe_pass_2_continuation_prompt.md`

## Run Status

This is a continuation run from the completed structural reframe pass 1 state. It starts from the accepted pass-1 model `F3b`, not from original Model C. Treat it as within-condition continuation evidence, not as an equal-start fresh comparison against the base prompt.

## Result

Final accepted model: `P2F3`, which keeps the pass-1 wet/canopy suppressor and replaces the single arid fuel-discontinuity sigmoid with a two-threshold global arid fuel-continuity limiter.

Official global ILAMB:

| Model | Overall | Bias | RMSE | Seasonal | Spatial |
|---|---:|---:|---:|---:|---:|
| F3b incumbent | 0.676543 | 0.738225 | 0.511898 | 0.844302 | 0.776393 |
| P2F3 final | 0.677073 | 0.738666 | 0.512972 | 0.848079 | 0.772673 |
| Delta | +0.000530 | +0.000441 | +0.001074 | +0.003777 | -0.003720 |

Public TRENDY/firepipe:

| Model | Overall | Produced-table rank |
|---|---:|---:|
| ED-ModelC-pass2-P2F3 | 0.676846 | 1 |

Key regional deltas vs F3b:

| Region | Delta |
|---|---:|
| MIDE | +0.010559 |
| EURO | +0.008616 |
| TENA | +0.008019 |
| NHSA | +0.003808 |
| AUST | -0.002780 |
| BONA | -0.006580 |

## Mechanism

The accepted model represents dryland fire spread as a fuel-network/percolation problem. The first arid threshold represents early loss of fuel-continuity redundancy in semi-arid systems. The second threshold represents stronger desert-like fuel fragmentation. Both terms are smooth global functions of allowed climate/productivity-derived inputs.

## Candidate Families

- `P2F1`: seasonal curing/synchronization gate.
- `P2F2`: seasonal wet/canopy inhibition.
- `P2F3`: two-threshold arid fuel-continuity limiter.
- `P2F3abl-no-low`: ablation removing the low arid threshold.
- `P2F3abl-no-high`: ablation removing the high arid threshold.
- `P2F4`: seasonal wet inhibition plus two-threshold arid hybrid.

## Contents

- `logs/`: agent-authored pass-2 markdown logs and `final_report.md`.
- `candidates/`: pass-2 candidate JSONs.
- `model/`: final pass-2 formula documentation and parameter JSONs.
- `scripts/`: scripts changed or created by the agent for this pass.
- `official_ilamb/`: compact official ILAMB CSV/JSON/log outputs.
- `public_trendy/`: compact public TRENDY/firepipe CSV/JSON/log outputs.
- `metadata/`: governing workspace docs read by the agent.
- `prompt/`: recorded continuation prompt.

## Excluded

Heavy generated artifacts are intentionally not committed here:

- `ilamb/MODELS/*/*.nc`
- ILAMB `.pkl` files
- `out_terms/*.nc`
- full copied data directories

The compact CSV/JSON/log outputs are enough for paper evidence and comparison. Full artifacts remain in the local workspace and benchmark directories listed above.
