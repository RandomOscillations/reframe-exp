# ED Fire Agent Instructions

You are working in a local ED fire model-improvement workspace. Treat this as an autonomous research run, not a quick coding task.

Read these files before changing code:

- `program.md`
- `WORKSPACE_MANIFEST.md`
- `BASELINE_REPRO.md`
- `models/C/formula.md`
- `README.md`

Hard rules:

- Use only the allowed model inputs listed in `WORKSPACE_MANIFEST.md`.
- Do not use latitude/longitude hacks, named-region routing, per-cell lookup tables, or arbitrary residual correction coefficients.
- Use one global, interpretable formula.
- Do not use per-region formulas.
- Keep logs current throughout the run.
- Do not stop until `final_report.md` is written.
