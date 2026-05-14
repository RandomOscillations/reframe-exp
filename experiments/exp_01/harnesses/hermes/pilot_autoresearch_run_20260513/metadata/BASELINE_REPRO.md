# Baseline Reproduction

The workspace was rebuilt from clean tracked ED source at commit `1bac731`.

Generated baseline artifacts were recreated locally:

```bash
.venv/bin/python scripts/reproduce_modelC.py
.venv/bin/python scripts/dump_modelC_terms.py
```

Current baseline hashes:

```text
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
306b833a4aeed362d67cd510793e75e1ca9a5e2735b2ebdd0c57175bcaae1883  out_terms/modelC_terms.nc
```

Before starting the research loop, verify the baseline:

```bash
.venv/bin/python scripts/verify.py
```

Expected result: `PASS`.

Use original Model C as the starting point. The current model performs well offline and ranks strongly on the public benchmark, but regional/fire-regime caveats remain.

