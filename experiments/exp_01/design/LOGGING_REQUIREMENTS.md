# Logging Requirements

The agent must write live logs in its local workspace during the run. After the phase completes, lightweight records are copied into this repo under the relevant harness/run directory.

## Required Live Logs

`research_log.md`:
- chronological loop-by-loop record,
- hypothesis,
- functional form,
- search strategy,
- commands,
- results,
- decision.

`candidate_registry.md`:
- every candidate,
- status,
- parameters,
- score summary,
- verdict.

`eval_log.md`:
- exact evaluation commands,
- output directories,
- official scores,
- errors/warnings.

`regional_analysis.md`:
- official regional ILAMB tables,
- weak regions,
- regressions,
- interpretation.

`constraint_checks.md`:
- allowed inputs,
- no external data,
- no lookup tables,
- no coordinate hacks,
- no region routing,
- no arbitrary residual coefficients,
- mechanism explanation.

`final_report.md` or condition-specific terminal report:
- written at the declared stopping point,
- includes best-so-far global/regional/firepipe results,
- explains why more search is unlikely to help under the run's constraints.

## Permanent Repo Artifacts

After the run completes, copy into this repo:

- all live markdown logs,
- official global ILAMB `scalar_database.csv`,
- official regional ILAMB `scalar_database.csv`,
- public TRENDY/firepipe `scores.csv` and `scalar_database.csv`,
- candidate JSONs,
- candidate search/generation scripts needed to understand the run,
- relevant `params.json`, `formula.md`, `CHECKSUMS.txt`,
- terminal report (`final_report.md`, `local_exhaustion_report.md`, or equivalent),
- short paper-facing summaries.

Large runnable artifacts stay local unless explicitly needed:

- NetCDF outputs,
- ILAMB HTML dashboards,
- ILAMB pickle files,
- raw data bundles,
- virtual environments.
