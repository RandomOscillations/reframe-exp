# Hermes Harness

Profile:

- structural reframe pass 1 and continuation pass 2: `adireframe1`
- completed pilot profile: `adifire1`

Fresh local workspaces:

```text
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/base
/Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/reframe
```

Run command pattern:

```bash
cd /Users/adithyasrinivasan/Projects/creativity-docs/exp-workspaces/exp_01/hermes/<condition>
hermes -p <profile> chat
```

Base prompt reference:

```text
reframe-exps/experiments/exp_01/prompts/base_fresh_run_prompt.md
```

Structural reframe prompt reference:

```text
reframe-exps/experiments/exp_01/prompts/reframe_fresh_run_prompt.md
```

The intervention-only excerpt is stored separately at:

```text
reframe-exps/experiments/exp_01/prompts/structural_reframe_addendum.md
```

Pilot run record:

```text
experiments/exp_01/harnesses/hermes/pilot_autoresearch_run_20260513
```

The pilot is useful for prompt calibration only. Formal comparison conditions should start from the same original Model C workspace state.

Completed formal-ish run records:

```text
experiments/exp_01/harnesses/hermes/base_run
experiments/exp_01/harnesses/hermes/reframe_pass_1
experiments/exp_01/harnesses/hermes/reframe_pass_2_continuation
```

`reframe_pass_2_continuation` starts from the accepted pass-1 `F3b` state, so it is within-condition continuation evidence rather than a fresh equal-start condition.
