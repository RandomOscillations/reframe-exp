"""Round 2 search: dry-season-relieved wetness suppression.

Physical hypothesis:
OPT-WET-v1 showed annual wetness suppression helps humid/perhumid weak regions
but harms seasonal savannas/Australia and Spatial Distribution. Annual rainfall
alone is too blunt. A unified global formula should suppress high-P_ann cells
only when they lack current dry-season relief; high Dbar and/or low current-month
precipitation should relieve the wetness ceiling.

Allowed inputs only: Dbar, P_ann, P_month, monthly GPP, T_air. GFED is scoring
reference only.
"""
from __future__ import annotations

import json, os, time
from pathlib import Path

import numpy as np
import optuna

from reproduce_modelC import load_drivers, load_gfed_1deg

REPO = Path(__file__).resolve().parents[1]
OUTDIR = REPO / "models" / "C" / "candidate_search"
OUTDIR.mkdir(parents=True, exist_ok=True)
N_TRIALS = int(os.environ.get("N_TRIALS", "500"))
SEED = int(os.environ.get("SEED", "23"))
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", "5.0"))

BASE = json.loads((REPO / "models" / "C" / "params.json").read_text())["params"]
drivers = load_drivers()
obs = load_gfed_1deg().astype(np.float32)
N_MONTHS = obs.shape[0]
land_mask = (obs > 0).any(axis=0)
lat_1 = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
cos_lat = np.cos(np.deg2rad(lat_1)).astype(np.float64)
w2 = np.broadcast_to(cos_lat[:, None], (180, 360)).astype(np.float64)
gfed_tm = obs.mean(axis=0).astype(np.float64)
gfed_std = obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc = obs.reshape(16, 12, 180, 360).mean(axis=0)
gfed_peak_month = np.argmax(gfed_cyc, axis=0).astype(np.float32)
mass_w = (w2 * gfed_tm).astype(np.float64)
mass_w_burn = mass_w * land_mask
w2_burn = w2 * land_mask

# A small regional proxy is used only to keep the search pointed at the known
# failure pattern. It uses broad bounding boxes for diagnostics, not in the model
# formula. Official regional ILAMB remains decisive.
REGION_SLICES = {
    # rough 1-degree index boxes, diagnostic only
    "nhaf": (90, 120, 160, 220),
    "shaf": (60, 90, 160, 220),
    "aust": (45, 75, 290, 335),
}

def sig(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(-k * (x - c), -50, 50)))

def supp(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(k * (x - c), -50, 50)))

def hump(x, b, dec):
    b = max(float(b), 1e-9); dec = max(float(dec), 1e-9)
    return (1.0 - np.exp(-np.clip(x / b, 0, 500))) * np.exp(-np.clip(x / dec, 0, 500))

def model_product(extra: dict) -> np.ndarray:
    p = BASE
    onset = sig(drivers["dbar"], p["k1"], p["D_low"])
    dry_suppress = supp(drivers["dbar"], p["k2"], p["D_high"])
    p_floor = drivers["p_ann"] / (drivers["p_ann"] + p["P_half"] + 1e-12)
    p_damp = 1.0 / (1.0 + drivers["p_month"] / (p["pre_dampen_half"] + 1e-12))
    gpp_mod = hump(p["gpp_af"] * drivers["gpp_monthly"], p["gpp_b"], p["gpp_d"])
    ign_mod = sig(drivers["t_air"], p["ign_k"], p["ign_c"])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod

    # Annual wetness ceiling.
    wet = 1.0 / (1.0 + np.power(np.clip(drivers["p_ann"] / (extra["P_wet_half"] + 1e-12), 0, 1e6), extra["P_wet_pow"]))
    # Relief when dry-season physics are present. High Dbar and/or very low
    # current P_month can cancel wetness suppression in seasonal savanna months.
    d_relief = sig(drivers["dbar"], extra["D_relief_k"], extra["D_relief_c"])
    p_relief = 1.0 / (1.0 + np.power(np.clip(drivers["p_month"] / (extra["P_relief_half"] + 1e-12), 0, 1e6), extra["P_relief_pow"]))
    dry_relief = 1.0 - (1.0 - d_relief) * (1.0 - p_relief)
    wet_mult = 1.0 - extra["wet_strength"] * (1.0 - wet) * (1.0 - extra["relief_strength"] * dry_relief)
    wet_mult = np.clip(wet_mult, 0.0, 2.0)
    return product * wet_mult

def predict(extra: dict) -> np.ndarray:
    rate = np.power(np.clip(model_product(extra), 0, None), BASE["fire_exp"]).astype(np.float32)
    rate *= land_mask[None,:,:]
    return ((1.0 - np.exp(-np.minimum(rate, FIRE_MAX_RATE))) / 12.0).astype(np.float32)

def score(pred_monthly: np.ndarray) -> tuple[float, dict]:
    pred_tm = pred_monthly.mean(axis=0).astype(np.float64)
    bias = float((np.exp(-np.abs(pred_tm - gfed_tm) / gfed_std) * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_anom = pred_monthly - pred_tm[None,:,:]
    obs_anom = obs - gfed_tm[None,:,:]
    crmse = np.sqrt(((pred_anom - obs_anom) ** 2).mean(axis=0))
    rmse = float((np.exp(-crmse / gfed_std) * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_cyc = pred_monthly.reshape(16,12,180,360).mean(axis=0)
    shift = np.argmax(pred_cyc, axis=0).astype(np.float32) - gfed_peak_month
    shift = np.where(shift > 6, shift - 12, shift)
    shift = np.where(shift < -6, shift + 12, shift)
    seas = float((((1.0 + np.cos(np.abs(shift)/12.0*2*np.pi))*0.5) * mass_w_burn).sum() / (mass_w_burn.sum()+1e-12))
    obs_flat = gfed_tm[land_mask]; pred_flat = pred_tm[land_mask]; pw = w2_burn[land_mask]
    ow = (obs_flat*pw).sum()/pw.sum(); pm = (pred_flat*pw).sum()/pw.sum()
    oa = obs_flat-ow; pa = pred_flat-pm
    std0 = max(float(np.sqrt(((oa**2)*pw).sum()/pw.sum())), 1e-12)
    std = max(float(np.sqrt(((pa**2)*pw).sum()/pw.sum())), 1e-12)
    rho = float((pa*oa*pw).sum()/(np.sqrt(((pa**2)*pw).sum()*((oa**2)*pw).sum())+1e-12))
    sigma = std/std0
    spatial = float(2*(1+rho)/((sigma + 1/max(sigma,1e-12))**2))
    overall = float((2*bias+2*rmse+seas+spatial)/6)
    # diagnostic penalty if rough savanna/Australia period means are strongly suppressed vs baseline
    return overall, {"bias":bias,"rmse":rmse,"seasonal":seas,"spatial":spatial,"overall":overall}

def objective(trial: optuna.Trial) -> float:
    e = {
        "family": "dryseason_wet_relief",
        "wet_strength": trial.suggest_float("wet_strength", 0.3, 1.0),
        "P_wet_half": trial.suggest_float("P_wet_half", 1000.0, 5000.0, log=True),
        "P_wet_pow": trial.suggest_float("P_wet_pow", 1.0, 5.0),
        "relief_strength": trial.suggest_float("relief_strength", 0.0, 1.0),
        "D_relief_k": trial.suggest_float("D_relief_k", 1e-4, 1e-1, log=True),
        "D_relief_c": trial.suggest_float("D_relief_c", 10.0, 2000.0, log=True),
        "P_relief_half": trial.suggest_float("P_relief_half", 0.1, 50.0, log=True),
        "P_relief_pow": trial.suggest_float("P_relief_pow", 0.5, 5.0),
    }
    pred = predict(e)
    overall, br = score(pred)
    for k,v in br.items(): trial.set_user_attr(k,v)
    trial.set_user_attr("extra", e)
    return overall

def main():
    # Baseline and Round-1 wet candidate proxy for context.
    base_extra = {"family":"dryseason_wet_relief","wet_strength":0.0,"P_wet_half":2253.5,"P_wet_pow":4.0,"relief_strength":0.0,"D_relief_k":0.01,"D_relief_c":100,"P_relief_half":5,"P_relief_pow":2}
    # compute baseline by using effectively no wet suppression
    pred_base = predict(base_extra)
    base_overall, base_br = score(pred_base)
    print("[baseline proxy]", base_br)
    sampler = optuna.samplers.TPESampler(seed=SEED, multivariate=True, group=True)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    # enqueue OPT-WET-like no-relief and moderate relief variants
    study.enqueue_trial({"wet_strength":0.9901726411855946,"P_wet_half":2253.544627972052,"P_wet_pow":3.9777542158515304,"relief_strength":0.0,"D_relief_k":0.01,"D_relief_c":100.0,"P_relief_half":5.0,"P_relief_pow":2.0})
    study.enqueue_trial({"wet_strength":0.95,"P_wet_half":2250.0,"P_wet_pow":4.0,"relief_strength":0.75,"D_relief_k":0.01,"D_relief_c":100.0,"P_relief_half":5.0,"P_relief_pow":2.0})
    t0=time.time(); last=t0
    def cb(st,tr):
        nonlocal last
        if time.time()-last>30:
            print(f"[progress] {len(st.trials)}/{N_TRIALS} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f} min")
            last=time.time()
    study.optimize(objective, n_trials=N_TRIALS, callbacks=[cb])
    best=study.best_trial
    result={
        "name":"DRYSEASON-WET-v1",
        "n_trials":len(study.trials),
        "seed":SEED,
        "baseline_proxy":base_br,
        "best_proxy_scores":{k:best.user_attrs[k] for k in ["bias","rmse","seasonal","spatial","overall"]},
        "best_extra":best.user_attrs["extra"],
        "best_params":best.params,
        "runtime_min":round((time.time()-t0)/60,3),
        "physical_hypothesis":"Annual wetness suppression should be relieved in cell-months with high accumulated dryness and/or low current precipitation, distinguishing seasonal savannas from perhumid wet forests using only allowed inputs.",
        "constraint_note":"Model formula uses only Dbar, P_ann, P_month, GPP_monthly, T_air. Rough regional diagnostics are not used in the formula; official ILAMB regions are decisive."
    }
    out=OUTDIR/f"dryseason_wet_search_{N_TRIALS}_trials.json"
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    print(f"[write] {out}")

if __name__ == "__main__":
    main()
