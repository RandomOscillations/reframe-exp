# Experiment 03 Control: ED Fire Non-Reframe

This is the matched non-reframe/control run for Experiment 03.

The workspace starts from the same clean original ED Model C setup used for the exp_03 reframe run, but it is isolated under a separate experiment directory so the control agent cannot see reframe run outputs.

## Live Workspace

- Harness: Hermes Agent
- Workspace: `/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_03_control/hermes/base`
- Prompt: `prompts/control_prompt_draft.md`

## Isolation Notes

The live workspace was prepared from tracked `ed-autoresearch-source` files plus the required pinned input and evaluation assets. It was not copied from the completed exp_03 reframe workspace.

At setup time:

- local `ilamb/MODELS` contains only `ED-ModelC-final`,
- `public_benchmark_clean/ilamb/MODELS` contains only official comparator models plus `ED-ModelC-baseline`,
- no prior candidate names from the reframe run are present in the experiment-facing files,
- `final_report.md` is absent,
- logging files are empty placeholders for the agent to maintain.
