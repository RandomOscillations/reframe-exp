"""Search unified mechanistic extensions to Model C under the fixed input contract.

This is an internal/proxy Optuna search used to propose serious candidates for
official ILAMB. It does not introduce any new model inputs: only Dbar, annual
precipitation, monthly precipitation, monthly GPP, and monthly air temperature
are used. GFED is used only as evaluation/reference data, matching the baseline
workflow.
"""
from __future__ import annotations

import json, os, time
from pathlib import Path

import numpy as np
import optuna

from reproduce_modelC import fire_C, load_drivers, load_gfed_1deg

REPO = Path(__file__).resolve().parents[1]
OUTDIR = REPO / "models" / "C" / "candidate_search"
OUTDIR.mkdir(parents=True, exist_ok=True)
N_TRIALS = int(os.environ.get("N_TRIALS", "500"))
SEED = int(os.environ.get("SEED", "13"))
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", "5.0"))

print("[setup] loading baseline params/drivers/reference")
BASE = json.loads((REPO / "models" / "C" / "params.json").read_text())["params"]
drivers = load_drivers()
obs = load_gfed_1deg().astype(np.float32)
N_MONTHS = obs.shape[0]
land_mask = (obs > 0).any(axis=0)
lat_1 = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
cos_lat = np.cos(np.deg2rad(lat_1)).astype(np.float64)
w2 = np.broadcast_to(cos_lat[:, None], (180, 360)).astype(np.float64)
w3 = np.broadcast_to(cos_lat[None, :, None], (N_MONTHS, 180, 360)).astype(np.float64)
w3_land = w3 * land_mask[None,:,:]
gfed_tm = obs.mean(axis=0).astype(np.float64)
gfed_std = obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc = obs.reshape(16, 12, 180, 360).mean(axis=0)
gfed_peak_month = np.argmax(gfed_cyc, axis=0).astype(np.float32)
mass_w = (w2 * gfed_tm).astype(np.float64)
mass_w_burn = mass_w * land_mask
w2_burn = w2 * land_mask

# Precompute lag means for allowed monthly drivers. The lagged forms are global,
# smooth antecedent fuel/moisture hypotheses, not regional routing.
def lag_mean(arr: np.ndarray, window: int) -> np.ndarray:
    pieces = []
    for lag in range(1, window + 1):
        pieces.append(np.roll(arr, lag, axis=0))
    return np.mean(pieces, axis=0).astype(np.float32)

LAG_WINDOWS_GPP = [1,2,3,4,6,9,12]
LAG_WINDOWS_P = [1,2,3,4,6]
gpp_lags = {w: lag_mean(drivers["gpp_monthly"], w) for w in LAG_WINDOWS_GPP}
p_lags = {w: lag_mean(drivers["p_month"], w) for w in LAG_WINDOWS_P}


def ed_transform(rate_yr: np.ndarray) -> np.ndarray:
    return ((1.0 - np.exp(-np.minimum(rate_yr, FIRE_MAX_RATE))) / 12.0).astype(np.float32)


def sig(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(-k * (x - c), -50, 50)))


def supp(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(k * (x - c), -50, 50)))


def hump(x, b, dec):
    b = max(float(b), 1e-9); dec = max(float(dec), 1e-9)
    return (1.0 - np.exp(-np.clip(x / b, 0, 500))) * np.exp(-np.clip(x / dec, 0, 500))


def predict_extra(extra: dict) -> np.ndarray:
    p = BASE
    gpp = drivers["gpp_monthly"]
    if extra.get("gpp_lag_alpha", 0.0) > 0:
        a = extra["gpp_lag_alpha"]; w = int(extra["gpp_lag_window"])
        gpp = (1.0 - a) * gpp + a * gpp_lags[w]
    p_month = drivers["p_month"]
    if extra.get("precip_memory_alpha", 0.0) > 0:
        a = extra["precip_memory_alpha"]; w = int(extra["precip_memory_window"])
        p_month = (1.0 - a) * p_month + a * p_lags[w]

    onset = sig(drivers["dbar"], p["k1"], p["D_low"])
    dry_suppress = supp(drivers["dbar"], p["k2"], p["D_high"])
    p_floor = drivers["p_ann"] / (drivers["p_ann"] + p["P_half"] + 1e-12)
    p_damp = 1.0 / (1.0 + p_month / (p["pre_dampen_half"] + 1e-12))
    gpp_mod = hump(p["gpp_af"] * gpp, p["gpp_b"], p["gpp_d"])
    ign_mod = sig(drivers["t_air"], p["ign_k"], p["ign_c"])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod

    if extra.get("wet_strength", 0.0) > 0:
        # Perhumid wet-canopy/fuel-moisture ceiling. Strength allows ablation to 0.
        half = extra["P_wet_half"]; pow_ = extra["P_wet_pow"]; s = extra["wet_strength"]
        wet = 1.0 / (1.0 + np.power(np.clip(drivers["p_ann"] / (half + 1e-12), 0, 1e6), pow_))
        product = product * ((1.0 - s) + s * wet)

    if extra.get("drydown_strength", 0.0) > 0:
        # Recent drying pulse: month-to-month Dbar increase as a smooth ignition/fuel curing amplifier.
        prev_d = np.roll(drivers["dbar"], 1, axis=0)
        dd = np.maximum(drivers["dbar"] - prev_d, 0.0)
        amp = extra["drydown_amp"]; half = extra["drydown_half"]; s = extra["drydown_strength"]
        drypulse = 1.0 + amp * (dd / (dd + half + 1e-12))
        product = product * ((1.0 - s) + s * drypulse)

    rate = np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)
    rate *= land_mask[None,:,:]
    return ed_transform(rate)


def score(pred_monthly: np.ndarray) -> tuple[float, dict]:
    pred_tm = pred_monthly.mean(axis=0).astype(np.float64)
    bias_per_cell = pred_tm - gfed_tm
    bias = float((np.exp(-np.abs(bias_per_cell) / gfed_std) * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_anom = pred_monthly - pred_tm[None,:,:]
    obs_anom = obs - gfed_tm[None,:,:]
    crmse_per_cell = np.sqrt(((pred_anom - obs_anom) ** 2).mean(axis=0))
    rmse = float((np.exp(-crmse_per_cell / gfed_std) * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_cyc = pred_monthly.reshape(16,12,180,360).mean(axis=0)
    pred_peak = np.argmax(pred_cyc, axis=0).astype(np.float32)
    shift = pred_peak - gfed_peak_month
    shift = np.where(shift > 6, shift - 12, shift)
    shift = np.where(shift < -6, shift + 12, shift)
    seas_per_cell = (1.0 + np.cos(np.abs(shift) / 12.0 * 2.0 * np.pi)) * 0.5
    seas = float((seas_per_cell * mass_w_burn).sum() / (mass_w_burn.sum() + 1e-12))
    obs_flat = gfed_tm[land_mask]; pred_flat = pred_tm[land_mask]; pw = w2_burn[land_mask]
    ow = (obs_flat * pw).sum() / pw.sum(); pm = (pred_flat * pw).sum() / pw.sum()
    oa = obs_flat - ow; pa = pred_flat - pm
    std0 = max(float(np.sqrt(((oa**2) * pw).sum() / pw.sum())), 1e-12)
    std = max(float(np.sqrt(((pa**2) * pw).sum() / pw.sum())), 1e-12)
    rho = float((pa * oa * pw).sum() / (np.sqrt(((pa**2)*pw).sum() * ((oa**2)*pw).sum()) + 1e-12))
    sigma = std / std0
    spatial = float(2.0 * (1.0 + rho) / ((sigma + 1.0 / max(sigma, 1e-12)) ** 2))
    # Proxy objective follows official tier-2 weighting.
    overall = float((2*bias + 2*rmse + seas + spatial) / 6.0)
    return overall, {"bias": bias, "rmse": rmse, "seasonal": seas, "spatial": spatial, "overall": overall}


def suggest_extra(trial: optuna.Trial) -> dict:
    family = trial.suggest_categorical("family", ["lag_fuel", "wet_supp", "precip_memory", "lag_wet", "hybrid", "drydown"])
    e = {"family": family, "gpp_lag_alpha": 0.0, "precip_memory_alpha": 0.0, "wet_strength": 0.0, "drydown_strength": 0.0}
    if family in ("lag_fuel", "lag_wet", "hybrid"):
        e["gpp_lag_window"] = trial.suggest_categorical("gpp_lag_window", LAG_WINDOWS_GPP)
        e["gpp_lag_alpha"] = trial.suggest_float("gpp_lag_alpha", 0.0, 1.0)
    if family in ("precip_memory", "hybrid"):
        e["precip_memory_window"] = trial.suggest_categorical("precip_memory_window", LAG_WINDOWS_P)
        e["precip_memory_alpha"] = trial.suggest_float("precip_memory_alpha", 0.0, 1.0)
    if family in ("wet_supp", "lag_wet", "hybrid"):
        e["wet_strength"] = trial.suggest_float("wet_strength", 0.0, 1.0)
        e["P_wet_half"] = trial.suggest_float("P_wet_half", 400.0, 5000.0, log=True)
        e["P_wet_pow"] = trial.suggest_float("P_wet_pow", 0.5, 4.0)
    if family in ("drydown", "hybrid"):
        e["drydown_strength"] = trial.suggest_float("drydown_strength", 0.0, 1.0)
        e["drydown_amp"] = trial.suggest_float("drydown_amp", 0.0, 2.0)
        e["drydown_half"] = trial.suggest_float("drydown_half", 1.0, 1000.0, log=True)
    return e


def objective(trial: optuna.Trial) -> float:
    e = suggest_extra(trial)
    pred = predict_extra(e)
    overall, breakdown = score(pred)
    # soft complexity penalty so tiny proxy ties favor simpler mechanisms
    active = sum(float(e.get(k, 0.0) > 0.02) for k in ["gpp_lag_alpha","precip_memory_alpha","wet_strength","drydown_strength"])
    val = overall - 0.00015 * max(0, active - 1)
    for k, v in breakdown.items(): trial.set_user_attr(k, v)
    trial.set_user_attr("extra", e)
    return val


def main():
    baseline_pred = ed_transform(fire_C(drivers, BASE) * land_mask[None,:,:])
    base_overall, base_break = score(baseline_pred)
    print(f"[baseline proxy] {base_break}")
    sampler = optuna.samplers.TPESampler(seed=SEED, multivariate=True, group=True)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    # enqueue known simple ablations to ensure the search tests interpretable corners.
    study.enqueue_trial({"family":"lag_fuel", "gpp_lag_window":12, "gpp_lag_alpha":1.0})
    study.enqueue_trial({"family":"wet_supp", "wet_strength":1.0, "P_wet_half":3000.0, "P_wet_pow":3.0})
    study.enqueue_trial({"family":"precip_memory", "precip_memory_window":1, "precip_memory_alpha":0.25})
    t0 = time.time(); last=t0
    def cb(st, tr):
        nonlocal last
        if time.time()-last > 30:
            print(f"[progress] {len(st.trials)}/{N_TRIALS}, best={st.best_value:.6f}, elapsed={(time.time()-t0)/60:.1f} min")
            last = time.time()
    study.optimize(objective, n_trials=N_TRIALS, callbacks=[cb])
    best = study.best_trial
    result = {
        "n_trials": len(study.trials),
        "seed": SEED,
        "baseline_proxy": base_break,
        "best_proxy_value_penalized": best.value,
        "best_proxy_scores": {k: best.user_attrs[k] for k in ["bias","rmse","seasonal","spatial","overall"]},
        "best_extra": best.user_attrs["extra"],
        "best_params": best.params,
        "runtime_min": round((time.time()-t0)/60, 3),
        "constraint_note": "Uses only allowed Model C drivers; GFED used only for scoring/reference diagnostics."
    }
    out = OUTDIR / f"optuna_extension_search_{N_TRIALS}_trials.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"[write] {out}")

if __name__ == "__main__":
    main()
