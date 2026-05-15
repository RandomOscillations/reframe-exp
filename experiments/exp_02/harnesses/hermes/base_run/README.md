# Base Run Artifacts

Status: active run records now include the pass 3 loop-13 ceiling check.

Live workspace:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_02/hermes/base
```

Prompt draft:

```text
experiments/exp_02/prompts/base_prompt_draft.md
```

## Runs

```text
pass_1_p2f3_continuation
pass_2_ceiling_continuation
pass_3_loop13_ceiling_check
```

`pass_1_p2f3_continuation` records the first counted Hermes base continuation run that produced `ED-p2f3-seed2` / `p2f3_seed_current` as the accepted P2F3 model.

`pass_2_ceiling_continuation` records the Hermes `/goal` continuation that started from P2F3 and produced `ED-next-curing-hotwet-1` as the accepted balanced continuation model.

`pass_3_loop13_ceiling_check` records the Hermes `/goal` continuation that started from `ED-next-curing-hotwet-1`, found scalar improvements around 0.690, and rejected them because they damaged BONA/BOAS and did not produce a balanced global-plus-regional improvement.
