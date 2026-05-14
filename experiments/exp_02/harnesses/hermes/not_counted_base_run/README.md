# Exp 02 Hermes Base Run - Not Counted

Status: not counted.

Reason: this run stopped after a small third-decimal global Overall improvement and treated that as a defensible final result. That does not satisfy the stricter experiment intent for `exp_02`, which was to keep grinding until the local search genuinely reached a standstill or produced a meaningful global + regional delta.

Full workspace archive:

`/Users/adithyasrinivasan/Projects/creativity-docs/_archive/2026-05-14_145657__ed_fire_exp02_hermes_base_not_counted_third_decimal_run/full_workspace/base`

Agent-selected final model:

- `C7_humid_dryrate_added_only`
- Original Model C plus active dry-down / curing and humid-regime suppression terms.

Key result:

- Official global Overall: `0.673264` vs baseline `0.671529`, delta `+0.001735`.
- Official global Spatial fell from `0.772351` to `0.767279`.
- Public TRENDY/firepipe Overall: `0.673022` vs public baseline-current `0.671274`.
- Useful regional signal: humid suppression improved EQAS strongly, especially `C6b` from `0.507395` to `0.589676`.

Why it is archived instead of counted:

- The final global delta is too small for the intended evidence standard.
- The run still contains useful mechanistic and regional diagnostics, but it ended too early relative to the requested long-horizon search behavior.
- It should be used as audit/context only, not as a counted baseline or reframe result.

Included here:

- `logs/`: final report and required research logs.
- `prompts/`: program file used by the run.
- `candidate_metadata/`: JSON metadata for candidate mechanisms.
- `eval_logs/`: ILAMB and TRENDY/firepipe command logs.
- `eval_tables/`: copied scalar score tables from official global/regional evaluations.
- `final_model/`: final formula and parameter metadata from the not-counted run.
