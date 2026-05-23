#!/usr/bin/env python3
"""Mechanistic candidate search for the constrained Model C workspace.

This script is intentionally self-contained and uses only the fixed workspace
inputs allowed by program.md. It searches global formula families, writes
candidate params, candidate NetCDFs, and CSV diagnostics. It does not use
latitude/longitude or region identity inside any formula; region masks are used
only for evaluation and triage.
"""
from __future__ import annotations

import argparse, json, os, shutil, sys, time
from pathlib import Path

import cftime
import h5py
import numpy as np
import optuna
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import add_cf_bounds, coarsen, load_drivers, load_gfed_1deg, sig, supp, uncoarsen

REPO = Path(__file__).resolve().parents[1]
MODELS_ROOT = REPO / "ilamb" / "MODELS"
OUT_ROOT = REPO / "experiments"
YEARS = list(range(2001, 2017))
N_MONTHS = 192
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", 5.0))
REGION_KEYS = ["bona","tena","ceam","nhsa","shsa","euro","mide","nhaf","shaf","boas","ceas","seas","eqas","aust"]
WEAK_REGIONS = ["ceam","euro","mide","tena","eqas","seas","shsa"]

BASE = json.load(open(REPO / "models" / "C" / "params.json"))["params"]


def logistic_up(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(-k * (x - c), -50, 50)))


def logistic_down(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(k * (x - c), -50, 50)))


def hump_asym(x, low, high, q):
    # Low-fuel onset times high-productivity/humid closure suppression.
    low = max(low, 1e-12); high = max(high, 1e-12); q = max(q, 1e-6)
    return (1.0 - np.exp(-np.clip(x / low, 0, 500))) / (1.0 + np.power(np.clip(x / high, 0, 1e6), q))


def model_base(d, p):
    onset    = sig(d["dbar"],    p["k1"],  p["D_low"])
    suppress = supp(d["dbar"],   p["k2"],  p["D_high"])
    p_floor  = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    p_damp   = 1.0 / (1.0 + d["p_month"] / (p["pre_dampen_half"] + 1e-12))
    g = p["gpp_af"] * d["gpp_monthly"]
    gpp_mod  = (1.0 - np.exp(-np.clip(g / max(p["gpp_b"], 1e-9), 0, 500))) * np.exp(-np.clip(g / max(p["gpp_d"], 1e-9), 0, 500))
    ign_mod  = sig(d["t_air"], p["ign_k"], p["ign_c"])
    product  = onset * suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)


def model_wet_firebreak(d, p):
    # Analogy: a fuse in an electrical circuit. Once annual wetness/fuel closure
    # exceeds a threshold, fires become discontinuous even if ignition timing is good.
    base = model_base(d, p)
    wet = 1.0 / (1.0 + np.power(np.clip(d["p_ann"] / max(p["wet_P50"], 1e-6), 0, 1e6), p["wet_q"]))
    return (base * np.power(np.clip(wet, 0, 1), p["wet_exp"])).astype(np.float32)


def model_gpp_asym(d, p):
    # Replace Model C's exponential GPP hump with a separately tunable onset and
    # saturation/closure term, analogous to a dose-response with toxicity at high dose.
    onset    = sig(d["dbar"],    p["k1"],  p["D_low"])
    suppress = supp(d["dbar"],   p["k2"],  p["D_high"])
    p_floor  = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    p_damp   = 1.0 / (1.0 + d["p_month"] / (p["pre_dampen_half"] + 1e-12))
    g = p["gpp_af"] * d["gpp_monthly"]
    gpp_mod = hump_asym(g, p["gpp_low"], p["gpp_high"], p["gpp_high_q"])
    ign_mod  = sig(d["t_air"], p["ign_k"], p["ign_c"])
    product = onset * suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)


def model_curing_ratio(d, p):
    # Fire as a queuing/bottleneck process: monthly rain is not just an absolute
    # dampener, it competes with accumulated seasonal deficit. A wet month after a
    # long dry buildup should not extinguish as much as the same rain in a wet regime.
    onset    = sig(d["dbar"],    p["k1"],  p["D_low"])
    suppress = supp(d["dbar"],   p["k2"],  p["D_high"])
    p_floor  = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    effective_rain = d["p_month"] / np.power(1.0 + d["dbar"] / max(p["dry_buffer"], 1e-6), p["dry_buffer_q"])
    p_damp = 1.0 / (1.0 + effective_rain / (p["pre_dampen_half"] + 1e-12))
    g = p["gpp_af"] * d["gpp_monthly"]
    gpp_mod  = (1.0 - np.exp(-np.clip(g / max(p["gpp_b"], 1e-9), 0, 500))) * np.exp(-np.clip(g / max(p["gpp_d"], 1e-9), 0, 500))
    ign_mod  = sig(d["t_air"], p["ign_k"], p["ign_c"])
    product = onset * suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)


FAMILIES = {
    "wet_firebreak": {
        "func": model_wet_firebreak,
        "extra": {"wet_P50": (100.0, 5000.0, True), "wet_q": (0.1, 8.0, True), "wet_exp": (0.1, 4.0, True)},
        "description": "Model C plus annual-wetness fuel-continuity/firebreak suppression."
    },
    "gpp_asym": {
        "func": model_gpp_asym,
        "extra": {"gpp_low": (1e-5, 50.0, True), "gpp_high": (1e-3, 1000.0, True), "gpp_high_q": (0.1, 8.0, True)},
        "drop": ["gpp_b", "gpp_d"],
        "description": "Model C with asymmetric GPP onset and high-productivity closure."
    },
    "curing_ratio": {
        "func": model_curing_ratio,
        "extra": {"dry_buffer": (10.0, 5000.0, True), "dry_buffer_q": (0.05, 4.0, True)},
        "description": "Model C with monthly rain dampening buffered by accumulated dry deficit."
    },
}

BASE_BOUNDS = {
    "k1": (1e-5, 1e-1, True), "D_low": (1.0, 1e4, True),
    "k2": (1e-5, 1e-1, True), "D_high": (10.0, 1e5, True),
    "fire_exp": (0.3, 10.0, True), "P_half": (1.0, 1e4, True),
    "pre_dampen_half": (1e-2, 1e3, True), "gpp_af": (1e-3, 1e2, True),
    "gpp_b": (1e-5, 1e1, True), "gpp_d": (1e-2, 1e3, True),
    "ign_k": (1e-3, 1e1, True), "ign_c": (0.1, 1e3, True),
}


def load_region_masks():
    # Evaluation-only masks using ILAMB's built-in region bounding boxes. The
    # model formula never sees these masks; official regional ILAMB is still run
    # separately for serious candidates. The built-in GFED/TRENDY regions are
    # rectangles in this ILAMB install, so this is sufficient for search triage.
    from ILAMB.Regions import Regions
    r = Regions()
    lat = np.arange(-89.5, 90.0, 1.0)
    lon = np.arange(-179.5, 180.0, 1.0)
    lat2, lon2 = np.meshgrid(lat, lon, indexing="ij")
    masks = {"global": np.ones((180, 360), dtype=bool)}
    for key in REGION_KEYS:
        entry = r._regions[key]
        lat_min, lat_max = float(entry[1][1]), float(entry[1][2])
        lon_min, lon_max = float(entry[2][1]), float(entry[2][2])
        masks[key] = (lat2 >= lat_min) & (lat2 <= lat_max) & (lon2 >= lon_min) & (lon2 <= lon_max)
    return masks


def region_scores(pred, obs, land_mask, w2, region_masks):
    gfed_tm = obs.mean(axis=0).astype(np.float64)
    gfed_std = obs.std(axis=0).clip(1e-12).astype(np.float64)
    gfed_cyc = obs.reshape(16, 12, 180, 360).mean(axis=0)
    gfed_peak = np.argmax(gfed_cyc, axis=0).astype(np.float32)
    pred_tm = pred.mean(axis=0).astype(np.float64)
    pred_cyc = pred.reshape(16, 12, 180, 360).mean(axis=0)
    pred_peak = np.argmax(pred_cyc, axis=0).astype(np.float32)
    pred_anom = pred - pred_tm[None,:,:]
    obs_anom = obs - gfed_tm[None,:,:]
    crmse = np.sqrt(((pred_anom - obs_anom) ** 2).mean(axis=0))
    shift = pred_peak - gfed_peak
    shift = np.where(shift > 6, shift - 12, shift)
    shift = np.where(shift < -6, shift + 12, shift)
    seas_per = (1.0 + np.cos(np.abs(shift) / 12.0 * 2*np.pi)) * 0.5
    rows = []
    for key, regmask in region_masks.items():
        mask = land_mask & regmask
        if not mask.any():
            continue
        mass_w = (w2 * gfed_tm) * mask
        area_w = w2 * mask
        bias_per = np.exp(-np.abs(pred_tm - gfed_tm) / gfed_std)
        rmse_per = np.exp(-crmse / gfed_std)
        denom_mass = mass_w.sum() + 1e-12
        bias = float((bias_per * mass_w).sum() / denom_mass)
        rmse = float((rmse_per * mass_w).sum() / denom_mass)
        seas = float((seas_per * mass_w).sum() / denom_mass)
        ow = float((gfed_tm * area_w).sum() / (area_w.sum() + 1e-12))
        pw = float((pred_tm * area_w).sum() / (area_w.sum() + 1e-12))
        oa = (gfed_tm - ow)[mask]
        pa = (pred_tm - pw)[mask]
        aw = area_w[mask]
        std0 = max(float(np.sqrt(((oa**2) * aw).sum() / (aw.sum()+1e-12))), 1e-12)
        std = max(float(np.sqrt(((pa**2) * aw).sum() / (aw.sum()+1e-12))), 1e-12)
        rho = float((pa*oa*aw).sum() / (np.sqrt(((pa**2)*aw).sum()*((oa**2)*aw).sum()) + 1e-12))
        sigma = std/std0
        spatial = float(2*(1+rho)/((sigma + 1/max(sigma,1e-12))**2))
        comp_mean = (bias + rmse + seas + spatial)/4.0
        pred_mean = float((pred_tm*area_w).sum()/(area_w.sum()+1e-12))
        obs_mean = float((gfed_tm*area_w).sum()/(area_w.sum()+1e-12))
        rows.append(dict(region=key, bias=bias, rmse=rmse, seasonal=seas, spatial=spatial,
                         component_mean=comp_mean, pred_mean=pred_mean, obs_mean=obs_mean,
                         ratio=pred_mean/(obs_mean+1e-12)))
    return pd.DataFrame(rows)


def ed_transform(rate):
    return ((1.0 - np.exp(-np.minimum(rate, FIRE_MAX_RATE))) / 12.0).astype(np.float32)


def write_nc(pred, model_name):
    dst_dir = MODELS_ROOT / model_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "burntArea.nc"
    pred_hd = uncoarsen(pred.astype(np.float32))
    times = [cftime.DatetimeNoLeap(y, m, 15) for y in YEARS for m in range(1, 13)]
    lat = np.arange(-89.75, 90.0, 0.5)
    lon = np.arange(-179.75, 180.0, 0.5)
    ds = xr.Dataset({"burntArea": (("time","lat","lon"), pred_hd,
                    {"units":"1", "standard_name":"burnt_area_fraction", "long_name":"Burnt Area Fraction"})},
                    coords={"time": ("time", times), "lat": ("lat", lat), "lon": ("lon", lon)},
                    attrs={"title": model_name, "Conventions":"CF-1.7",
                           "transform": f"monthly_frac = (1 - exp(-min(rate_yr, {FIRE_MAX_RATE}) * 1yr)) / 12"})
    ds = add_cf_bounds(ds)
    enc = {"burntArea": {"zlib": True, "complevel": 4, "_FillValue": 1e20},
           "time": {"units": "days since 2001-01-01 00:00:00", "calendar": "noleap", "dtype": "float64"},
           "time_bounds": {"units": "days since 2001-01-01 00:00:00", "calendar": "noleap", "dtype": "float64"}}
    tmp = dst.with_suffix(".nc.tmp")
    ds.to_netcdf(tmp, encoding=enc, format="NETCDF4_CLASSIC")
    os.replace(tmp, dst)
    return dst


def suggest_params(trial, family):
    spec = FAMILIES[family]
    drop = set(spec.get("drop", []))
    p = {}
    for name, (lo, hi, log) in BASE_BOUNDS.items():
        if name in drop:
            continue
        p[name] = trial.suggest_float(name, lo, hi, log=log)
    for name, (lo, hi, log) in spec["extra"].items():
        p[name] = trial.suggest_float(name, lo, hi, log=log)
    return p


def initial_params(family):
    p = dict(BASE)
    if family == "wet_firebreak":
        p.update({"wet_P50": 2500.0, "wet_q": 2.0, "wet_exp": 1.0})
    elif family == "gpp_asym":
        p.pop("gpp_b", None); p.pop("gpp_d", None)
        p.update({"gpp_low": 1e-4, "gpp_high": 150.0, "gpp_high_q": 1.0})
    elif family == "curing_ratio":
        p.update({"dry_buffer": 300.0, "dry_buffer_q": 1.0})
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=sorted(FAMILIES), required=True)
    ap.add_argument("--trials", type=int, default=600)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--objective", choices=["global", "regional"], default="regional")
    ap.add_argument("--model-name", default=None)
    args = ap.parse_args()

    outdir = OUT_ROOT / args.family
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"[setup] family={args.family} trials={args.trials} objective={args.objective} fire_max={FIRE_MAX_RATE}")
    drivers = load_drivers()
    obs = load_gfed_1deg().astype(np.float32)
    land_mask = (obs > 0).any(axis=0)
    lat = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
    w2 = np.broadcast_to(np.cos(np.deg2rad(lat))[:,None], (180,360)).astype(np.float64)
    region_masks = load_region_masks()
    func = FAMILIES[args.family]["func"]

    def predict(p):
        with np.errstate(over="ignore", invalid="ignore"):
            rate = func(drivers, p) * land_mask[None,:,:]
        pred = ed_transform(rate)
        return np.where(land_mask[None,:,:], pred, np.nan).astype(np.float32)

    def score_for(p):
        pred = np.nan_to_num(predict(p), nan=0.0)
        df = region_scores(pred, obs, land_mask, w2, region_masks)
        g = df[df.region == "global"].iloc[0]
        # ILAMB global Overall is tier weighted: 2*Bias + 2*RMSE + Seasonal + Spatial over 6.
        global_tier = float((2*g.bias + 2*g.rmse + g.seasonal + g.spatial) / 6.0)
        weak = float(df[df.region.isin(WEAK_REGIONS)].component_mean.mean())
        # Defend global fit while encouraging regional behavior in known weak families.
        objective = global_tier if args.objective == "global" else 0.70*global_tier + 0.30*weak
        return objective, global_tier, weak, df

    sampler = optuna.samplers.TPESampler(seed=args.seed, multivariate=True)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.enqueue_trial(initial_params(args.family))
    t0 = time.time(); last = t0

    def objective(trial):
        p = suggest_params(trial, args.family)
        score, global_tier, weak, _ = score_for(p)
        trial.set_user_attr("global_tier", global_tier)
        trial.set_user_attr("weak_mean", weak)
        return score

    def cb(study, trial):
        nonlocal last
        if time.time() - last > 20:
            print(f"[opt] trial={len(study.trials)}/{args.trials} best={study.best_value:.5f} "
                  f"g={study.best_trial.user_attrs.get('global_tier',np.nan):.5f} "
                  f"weak={study.best_trial.user_attrs.get('weak_mean',np.nan):.5f}")
            last = time.time()

    study.optimize(objective, n_trials=args.trials, callbacks=[cb], gc_after_trial=True)
    best_p = study.best_params
    score, global_tier, weak, df = score_for(best_p)
    pred = predict(best_p)
    model_name = args.model_name or f"ED-ModelC-{args.family}"
    nc = write_nc(pred, model_name)

    result = {
        "model_name": model_name,
        "family": args.family,
        "description": FAMILIES[args.family]["description"],
        "n_trials": len(study.trials),
        "seed": args.seed,
        "objective": args.objective,
        "best_objective": score,
        "internal_global_tier": global_tier,
        "internal_weak_region_component_mean": weak,
        "fire_max_rate": FIRE_MAX_RATE,
        "params": best_p,
        "netcdf": str(nc),
        "constraints": "Formula uses only allowed dbar, annual/monthly precipitation, monthly GPP, monthly air temperature. No region/cell/lat/lon inputs."
    }
    (outdir / f"{model_name}.json").write_text(json.dumps(result, indent=2))
    df.to_csv(outdir / f"{model_name}_regional_internal.csv", index=False)
    print(json.dumps({k: result[k] for k in ["model_name","family","n_trials","best_objective","internal_global_tier","internal_weak_region_component_mean","netcdf"]}, indent=2))
    print(df.sort_values("component_mean").to_string(index=False))


if __name__ == "__main__":
    main()
