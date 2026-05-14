# Baseline Reproduction Note

This formal workspace starts from clean `ed-autoresearch` commit `1bac731`.

The checked-out repository checksum for `ilamb/MODELS/ED-ModelC-final/burntArea.nc` was stale relative to the current checked-out reproduction code and parameters. The setup regenerated the baseline artifacts in this workspace with:

```bash
.venv/bin/python scripts/reproduce_modelC.py
.venv/bin/python scripts/dump_modelC_terms.py
```

The reproducible baseline artifacts for this workspace are:

```text
5115a73698ad0a8cc5a00056493227866517387a7c72d28f04ad32d0d4b4e862  ilamb/MODELS/ED-ModelC-final/burntArea.nc
306b833a4aeed362d67cd510793e75e1ca9a5e2735b2ebdd0c57175bcaae1883  out_terms/modelC_terms.nc
3afbd924394ac557b7cc08413c43cfb3e1ffb9f1f84d599d25bc8ddfd9a2764b  models/C/params.json
```

This checksum repair is an environment/setup fix, not a scientific model change. The formal starting model is still original Model C with the 12 checked-out parameters in `models/C/params.json`.

