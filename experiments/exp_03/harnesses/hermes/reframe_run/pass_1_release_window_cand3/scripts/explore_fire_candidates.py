"""Explore constrained global mechanistic burned-area formula variants.

This script intentionally stays inside the fixed input contract. Candidate formulas
use only transforms of Model C inputs: dbar, p_ann, p_month, t_air, monthly GPP.
No latitude/longitude, region identifiers, cell lookup tables, residual maps, or
external data enter the formulas.

The fast objective is an ILAMB-inspired proxy for screening. Serious candidates
must still be regenerated and run through official ILAMB.
"""
from __future__ import annotations

import argparse, json, math, os, time
from pathlib import Path

import cftime
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
import pandas as pd
import xarray as xr

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import load_drivers, load_gfed_1deg, add_cf_bounds, uncoarsen, sig, supp, hump

REPO = Path(__file__).resolve().parents[1]
YEARS = list(range(2001, 2017))
N_MONTHS = 192
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", 5.0))
DT_YEARS = 1.0
REGIONS = {
    "bona": ((49.75,79.75),(-170.25,-60.25)),
    "tena": ((30.25,49.75),(-125.25,-66.25)),
    "ceam": ((9.75,30.25),(-115.25,-80.25)),
    "nhsa": ((0.25,12.75),(-80.25,-50.25)),
    "shsa": ((-59.75,0.25),(-80.25,-33.25)),
    "euro": ((35.25,70.25),(-10.25,30.25)),
    "mide": ((20.25,40.25),(-10.25,60.25)),
    "nhaf": ((0.25,20.25),(-20.25,45.25)),
    "shaf": ((-34.75,0.25),(10.25,45.25)),
    "boas": ((54.75,70.25),(30.25,179.75)),
    "ceas": ((30.25,54.75),(30.25,142.58)),
    "seas": ((5.25,30.25),(65.25,120.25)),
    "eqas": ((-10.25,10.25),(99.75,150.25)),
    "aust": ((-41.25,-10.50),(112.00,154.00)),
}
WEAK_REGIONS = ["ceam","euro","tena","mide","seas","shsa","eqas"]


def roll_mean(x, n):
    out = np.empty_like(x)
    for i in range(x.shape[0]):
        idx = [(i - k) % 12 + 12 * (i // 12) for k in range(n)]
        # keep within each year; for Jan/Feb use available previous months cyclically in same climatological year
        vals = []
        y0 = (i // 12) * 12
        for k in range(n):
            j = i - k
            if j < y0: j += 12
            vals.append(x[j])
        out[i] = np.mean(vals, axis=0)
    return out.astype(np.float32)


def prev_month(x):
    out = np.empty_like(x)
    for i in range(x.shape[0]):
        y0 = (i // 12) * 12
        j = i - 1 if i > y0 else y0 + 11
        out[i] = x[j]
    return out.astype(np.float32)


class Context:
    def __init__(self):
        print("[setup] loading drivers/GFED")
        self.d = load_drivers()
        self.obs = load_gfed_1deg().astype(np.float32)
        lat = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
        lon = np.arange(-179.5, 180.0, 1.0).astype(np.float32)
        self.lat = lat; self.lon = lon
        cos = np.cos(np.deg2rad(lat)).astype(np.float64)
        self.w2 = np.broadcast_to(cos[:,None], (180,360)).astype(np.float64)
        self.w3 = np.broadcast_to(cos[None,:,None], (N_MONTHS,180,360)).astype(np.float64)
        self.land = (self.obs > 0).any(axis=0)
        self.gfed_tm = self.obs.mean(axis=0).astype(np.float64)
        self.gfed_std = self.obs.std(axis=0).clip(1e-12).astype(np.float64)
        self.gfed_cyc = self.obs.reshape(16,12,180,360).mean(axis=0).astype(np.float64)
        self.gfed_peak = np.argmax(self.gfed_cyc, axis=0).astype(np.float32)
        self.mass_w = (self.w2 * self.gfed_tm * self.land).astype(np.float64)
        self.w2_land = (self.w2 * self.land).astype(np.float64)
        self.gpp3 = roll_mean(self.d["gpp_monthly"], 3)
        self.gpp6 = roll_mean(self.d["gpp_monthly"], 6)
        self.p3 = roll_mean(self.d["p_month"], 3)
        self.p6 = roll_mean(self.d["p_month"], 6)
        self.d_delta = (self.d["dbar"] - prev_month(self.d["dbar"])).astype(np.float32)
        self.region_masks = self._region_masks()
        print(f"[setup] burnable cells {int(self.land.sum())}/{self.land.size}")

    def _region_masks(self):
        masks = {"global": self.land.copy()}
        lat2 = self.lat[:,None]
        lon2 = self.lon[None,:]
        for r,(la,lo) in REGIONS.items():
            masks[r] = self.land & (lat2>=la[0]) & (lat2<=la[1]) & (lon2>=lo[0]) & (lon2<=lo[1])
        return masks


def ed_transform(rate):
    return ((1.0 - np.exp(-np.minimum(rate, FIRE_MAX_RATE))) / 12.0).astype(np.float32)


def base_product(ctx, p):
    d = ctx.d
    onset    = sig(d["dbar"], p["k1"], p["D_low"])
    suppress = supp(d["dbar"], p["k2"], p["D_high"])
    p_floor  = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    p_damp   = 1.0 / (1.0 + d["p_month"] / (p["pre_dampen_half"] + 1e-12))
    gpp_mod  = hump(p["gpp_af"] * d["gpp_monthly"], p["gpp_b"], p["gpp_d"])
    ign_mod  = sig(d["t_air"], p["ign_k"], p["ign_c"])
    return onset * suppress * p_floor * p_damp * gpp_mod * ign_mod


def rate_for_family(ctx, family, p):
    prod = base_product(ctx, p)
    d = ctx.d
    if family == "C_reopt":
        pass
    elif family == "annual_p_hump":
        # Pyrogeography corridor: too little annual precip lacks fuel; too much indicates wet closed canopy.
        wet_supp = 1.0 / (1.0 + np.power(np.clip(d["p_ann"] / (p["P_wet"] + 1e-12), 0, 1e6), p["P_wet_pow"]))
        prod = prod * wet_supp
    elif family == "antecedent_fuel":
        # Fine-fuel battery: previous productive/wet months charge fuels, current dry/hot months burn them.
        fuel = (1.0 - np.exp(-np.clip((ctx.gpp3 * p["gpp_charge_af"] + ctx.p3 * p["p_charge_af"]) / (p["charge_half"] + 1e-12), 0, 500)))
        prod = prod * fuel
    elif family == "drydown_curing":
        # Curing/front propagation: increasing water deficit is a transition-state gate, not a region switch.
        drydown = sig(ctx.d_delta, p["dd_k"], p["dd_c"])
        prod = prod * (p["dd_floor"] + (1.0 - p["dd_floor"]) * drydown)
    elif family == "wetforest_curing":
        wet_supp = 1.0 / (1.0 + np.power(np.clip(d["p_ann"] / (p["P_wet"] + 1e-12), 0, 1e6), p["P_wet_pow"]))
        drydown = sig(ctx.d_delta, p["dd_k"], p["dd_c"])
        prod = prod * wet_supp * (p["dd_floor"] + (1.0 - p["dd_floor"]) * drydown)
    elif family == "fuel_moisture_balance":
        # Structural analogy to combustion stoichiometry: fire peaks at balanced fuel and dryness.
        charge = (1.0 - np.exp(-np.clip(ctx.gpp6 * p["gpp_charge_af"] / (p["charge_half"] + 1e-12), 0, 500)))
        wet_supp = 1.0 / (1.0 + np.power(np.clip(ctx.p6 / (p["p6_supp"] + 1e-12), 0, 1e6), p["p6_pow"]))
        prod = prod * charge * wet_supp
    else:
        raise ValueError(family)
    rate = np.power(np.clip(prod, 0, None), p["fire_exp"]).astype(np.float32)
    return rate * ctx.land[None,:,:]


BASE_RANGES = {
    "k1": (1e-5, 1e-1), "D_low": (1e0, 1e4), "k2": (1e-5, 1e-1), "D_high": (1e1, 1e5),
    "fire_exp": (0.35, 3.0), "P_half": (1e0, 1e4), "pre_dampen_half": (1e-2, 1e3),
    "gpp_af": (1e-3, 1e2), "gpp_b": (1e-5, 1e1), "gpp_d": (1e-2, 1e3),
    "ign_k": (1e-3, 1e1), "ign_c": (1e-1, 1e3),
}
EXTRA = {
    "C_reopt": {},
    "annual_p_hump": {"P_wet": (50.0, 5000.0), "P_wet_pow": (0.25, 8.0)},
    "antecedent_fuel": {"gpp_charge_af": (1e-3, 1e2), "p_charge_af": (1e-4, 1e1), "charge_half": (1e-3, 1e3)},
    "drydown_curing": {"dd_k": (1e-4, 1e0), "dd_c": (-200.0, 500.0), "dd_floor": (0.05, 1.0)},
    "wetforest_curing": {"P_wet": (50.0, 5000.0), "P_wet_pow": (0.25, 8.0), "dd_k": (1e-4, 1e0), "dd_c": (-200.0, 500.0), "dd_floor": (0.05, 1.0)},
    "fuel_moisture_balance": {"gpp_charge_af": (1e-3, 1e2), "charge_half": (1e-3, 1e3), "p6_supp": (1.0, 1000.0), "p6_pow": (0.25, 8.0)},
}
LOG_PARAMS = {k for k,v in BASE_RANGES.items()} | {"P_wet","gpp_charge_af","p_charge_af","charge_half","dd_k","p6_supp"}


def suggest(trial, name, lo, hi):
    if name in LOG_PARAMS and lo > 0 and hi > 0:
        return trial.suggest_float(name, lo, hi, log=True)
    return trial.suggest_float(name, lo, hi)


def sample_params(trial, family, warm=None):
    p = {}
    for n,(lo,hi) in BASE_RANGES.items():
        p[n] = suggest(trial, n, lo, hi)
    for n,(lo,hi) in EXTRA[family].items():
        p[n] = suggest(trial, n, lo, hi)
    return p


def score(ctx, pred, mask=None):
    if mask is None: mask = ctx.land
    mass_w = ctx.mass_w * mask
    w2_land = ctx.w2 * mask
    pred_tm = pred.mean(axis=0).astype(np.float64)
    bias_score = np.exp(-np.abs(pred_tm - ctx.gfed_tm) / ctx.gfed_std)
    bias = float((bias_score * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_anom = pred - pred_tm[None,:,:]
    obs_anom = ctx.obs - ctx.gfed_tm[None,:,:]
    crmse = np.sqrt(((pred_anom - obs_anom) ** 2).mean(axis=0))
    rmse = float((np.exp(-crmse / ctx.gfed_std) * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_cyc = pred.reshape(16,12,180,360).mean(axis=0)
    pred_peak = np.argmax(pred_cyc, axis=0).astype(np.float32)
    shift = pred_peak - ctx.gfed_peak
    shift = np.where(shift > 6, shift - 12, shift)
    shift = np.where(shift < -6, shift + 12, shift)
    seas_cell = (1.0 + np.cos(np.abs(shift) / 12.0 * 2.0 * np.pi)) * 0.5
    seas = float((seas_cell * mass_w).sum() / (mass_w.sum() + 1e-12))
    keep = mask & np.isfinite(pred_tm) & np.isfinite(ctx.gfed_tm)
    if keep.sum() < 3:
        spatial = 0.0
    else:
        of = ctx.gfed_tm[keep]; pf = pred_tm[keep]; ww = w2_land[keep]
        ow = float((of*ww).sum()/(ww.sum()+1e-12)); pw = float((pf*ww).sum()/(ww.sum()+1e-12))
        oa = of-ow; pa = pf-pw
        std0 = max(float(np.sqrt(((oa**2)*ww).sum()/(ww.sum()+1e-12))), 1e-12)
        std = max(float(np.sqrt(((pa**2)*ww).sum()/(ww.sum()+1e-12))), 1e-12)
        rho = float((pa*oa*ww).sum()/(np.sqrt(((pa**2)*ww).sum()*((oa**2)*ww).sum())+1e-12))
        sigma = std/std0
        spatial = float(2.0*(1.0+rho)/((sigma+1.0/max(sigma,1e-12))**2))
        spatial = max(0.0, min(1.0, spatial))
    overall = float((2*bias + 2*rmse + seas + spatial)/6.0)
    return {"bias":bias,"rmse":rmse,"seasonal":seas,"spatial":spatial,"overall":overall}


def objective_score(ctx, pred):
    g = score(ctx, pred)
    weak = [score(ctx, pred, ctx.region_masks[r])["overall"] for r in WEAK_REGIONS]
    # Keep global primary but reward broad regional repair and penalize the weakest failure.
    return 0.80*g["overall"] + 0.15*float(np.mean(weak)) + 0.05*float(np.min(weak))


def write_nc(ctx, pred, dst, title):
    pred_hd = uncoarsen(np.where(ctx.land[None,:,:], pred, np.nan).astype(np.float32))
    times = [cftime.DatetimeNoLeap(y, m, 15) for y in YEARS for m in range(1, 13)]
    lat = np.arange(-89.75, 90.0, 0.5)
    lon = np.arange(-179.75, 180.0, 0.5)
    ds = xr.Dataset({"burntArea": (("time","lat","lon"), pred_hd, {"units":"1", "standard_name":"burnt_area_fraction", "long_name":"Burnt Area Fraction"})}, coords={"time": ("time", times), "lat": ("lat", lat), "lon": ("lon", lon)}, attrs={"title": title, "Conventions":"CF-1.7", "transform": f"monthly_frac=(1-exp(-min(rate,{FIRE_MAX_RATE})))/12"})
    ds = add_cf_bounds(ds)
    dst = Path(dst); dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".nc.tmp")
    enc = {"burntArea":{"zlib":True,"complevel":4,"_FillValue":1e20}, "time":{"units":"days since 2001-01-01 00:00:00","calendar":"noleap","dtype":"float64"}, "time_bounds":{"units":"days since 2001-01-01 00:00:00","calendar":"noleap","dtype":"float64"}}
    ds.to_netcdf(tmp, encoding=enc, format="NETCDF4_CLASSIC")
    os.replace(tmp, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=list(EXTRA))
    ap.add_argument("--trials", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20260518)
    ap.add_argument("--outdir", default="models/explore")
    ap.add_argument("--write-nc", action="store_true")
    args = ap.parse_args()
    ctx = Context()
    warm = json.load(open(REPO/"models/C/params.json"))["params"]
    sampler = optuna.samplers.TPESampler(seed=args.seed, multivariate=True, group=True)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    # Enqueue baseline-compatible params for comparable families.
    enq = dict(warm)
    defaults = {"P_wet": 2000.0, "P_wet_pow": 1.0, "gpp_charge_af":1.0, "p_charge_af":0.01, "charge_half":1.0, "dd_k":0.01, "dd_c":0.0, "dd_floor":1.0, "p6_supp":1000.0, "p6_pow":1.0}
    for k in EXTRA[args.family]: enq[k] = defaults[k]
    study.enqueue_trial(enq)
    t0 = time.time()
    def obj(trial):
        p = sample_params(trial, args.family)
        pred = ed_transform(rate_for_family(ctx, args.family, p))
        return objective_score(ctx, pred)
    def cb(st, tr):
        if len(st.trials) % 50 == 0:
            print(f"[opt] {args.family} trial {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m")
    study.optimize(obj, n_trials=args.trials, callbacks=[cb])
    p = study.best_params
    pred = ed_transform(rate_for_family(ctx, args.family, p))
    glob = score(ctx, pred)
    regs = {r: score(ctx, pred, m) for r,m in ctx.region_masks.items()}
    raw = rate_for_family(ctx, args.family, p)
    out = {
        "family": args.family, "n_trials": len(study.trials), "seed": args.seed,
        "fast_objective": study.best_value, "fast_global": glob, "fast_regions": regs,
        "params": p, "mechanism_note": __doc__,
        "diagnostics": {"raw_land_mean": float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)), "raw_max": float(raw.max()), "fire_max_rate": FIRE_MAX_RATE},
    }
    outdir = REPO / args.outdir / args.family
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"result.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"family":args.family,"best":study.best_value,"global":glob,"raw":out["diagnostics"],"out":str(outdir/"result.json")}, indent=2))
    if args.write_nc:
        write_nc(ctx, pred, outdir/"burntArea.nc", f"candidate {args.family}")
        print(f"wrote {outdir/'burntArea.nc'}")

if __name__ == "__main__":
    main()
