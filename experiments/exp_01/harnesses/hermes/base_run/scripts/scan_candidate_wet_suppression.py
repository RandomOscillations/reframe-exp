#!/usr/bin/env python3
"""Deterministic scan for a unified annual-wetness suppression extension to Model C.

Hypothesis: In very wet climates, annual precipitation is not only fuel-enabling; it
also keeps fuels and boundary layers too moist to burn. Original Model C has a low-
precipitation floor and monthly rain dampener, but no smooth annual wetness ceiling.
This script scans two physically interpretable parameters for:

    wet_supp(P_ann) = 1 / (1 + (P_ann / P_wet_half) ** P_wet_pow)

and multiplies the existing Model C product by this factor before fire_exp.
The form is global, smooth, and uses only the existing annual precipitation driver.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import fire_C, load_drivers, load_gfed_1deg
from optimize_modelC_ilamb_aligned import score_BA_ilamb, ed_transform, land_mask, drivers, WARM_START

P_WET_HALVES = [400, 600, 800, 1000, 1250, 1500, 2000, 3000, 5000]
P_WET_POWS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

BASE_PARAMS = WARM_START.copy()

# Reuse already-loaded drivers/land_mask from optimize_modelC_ilamb_aligned import.
def fire_C_wet(p):
    rate_base = fire_C(drivers, p)
    half = p["P_wet_half"]
    pow_ = p["P_wet_pow"]
    p_ann = np.clip(drivers["p_ann"], 0, None)
    wet_supp = 1.0 / (1.0 + np.power(p_ann / (half + 1e-12), pow_))
    return (rate_base * np.power(wet_supp, p["fire_exp"])).astype(np.float32)

# Note: fire_C already applies product^fire_exp. Multiplying by wet_supp^fire_exp
# is algebraically equivalent to multiplying the pre-exponent product by wet_supp.

def predict(p):
    with np.errstate(over="ignore", invalid="ignore"):
        rate = fire_C_wet(p)
    rate = rate * land_mask[None, :, :]
    return ed_transform(rate)


def main():
    rows = []
    t0 = time.time()
    base_pred = ed_transform(fire_C(drivers, BASE_PARAMS) * land_mask[None,:,:])
    base_score, base_break = score_BA_ilamb(base_pred)
    print(f"BASE proxy overall={base_score:.6f} {base_break}")
    best = None
    for half in P_WET_HALVES:
        for pow_ in P_WET_POWS:
            p = BASE_PARAMS.copy()
            p.update(P_wet_half=float(half), P_wet_pow=float(pow_))
            pred = predict(p)
            overall, b = score_BA_ilamb(pred)
            row = {"P_wet_half": half, "P_wet_pow": pow_, **b}
            rows.append(row)
            print(f"scan half={half:6g} pow={pow_:4g} overall={overall:.6f} bias={b['bias']:.4f} rmse={b['rmse']:.4f} seas={b['seas']:.4f} spatial={b['spatial']:.4f}")
            if best is None or overall > best[0]:
                best = (overall, p, b)
    out = {"hypothesis":"annual wetness suppresses fire in perhumid regimes", "functional_form":"Model C product multiplied by 1/(1+(P_ann/P_wet_half)^P_wet_pow)", "scan_space":{"P_wet_half":P_WET_HALVES,"P_wet_pow":P_WET_POWS}, "base_proxy":base_break, "best_proxy":best[2], "best_params":best[1], "rows":rows, "runtime_sec":time.time()-t0}
    Path("out_candidate_wet_suppression.json").write_text(json.dumps(out, indent=2))
    print("BEST", best[0], best[2], {k: best[1][k] for k in ['P_wet_half','P_wet_pow']})
    print("wrote out_candidate_wet_suppression.json")
if __name__ == "__main__":
    main()
