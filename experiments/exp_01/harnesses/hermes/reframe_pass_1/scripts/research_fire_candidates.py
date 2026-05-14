"""Research candidate fire formula families under the fixed Model C input contract.

This script is intentionally local to the research workspace. It does not add new
model inputs: all candidate terms are smooth transformations of Model C's allowed
monthly drivers (dbar, annual/monthly precip, air temperature, monthly GPP) and
existing GFED masks for training/evaluation.

Usage examples:
  .venv/bin/python scripts/research_fire_candidates.py score-baseline
  N_TRIALS=500 .venv/bin/python scripts/research_fire_candidates.py optimize --family f1_wetdry --candidate F1a
  .venv/bin/python scripts/research_fire_candidates.py emit --candidate F1a
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import cftime
import h5py
import numpy as np
import optuna
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import add_cf_bounds, coarsen, fire_C, load_drivers, load_gfed_1deg, uncoarsen

REPO = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO / "models" / "C"
RESEARCH_DIR = REPO / "research_candidates"
RESEARCH_DIR.mkdir(exist_ok=True)
OUT_NC = REPO / "ilamb" / "MODELS" / "ED-ModelC-final" / "burntArea.nc"
YEARS = list(range(2001, 2017))
N_MONTHS = 192
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", 5.0))
N_TRIALS = int(os.environ.get("N_TRIALS", 500))
SEED = int(os.environ.get("SEED", 123))

print("[setup] loading drivers + GFED ...")
drivers = load_drivers()
obs = load_gfed_1deg()
lat_1 = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
cos_lat = np.cos(np.deg2rad(lat_1)).astype(np.float32)
w2 = np.broadcast_to(cos_lat[:, None], (180, 360)).astype(np.float64)
w3 = np.broadcast_to(cos_lat[None, :, None], (N_MONTHS, 180, 360)).astype(np.float64)
land_mask = (obs > 0).any(axis=0)
w2_burn = (w2 * land_mask).astype(np.float64)
w3_land = (w3 * land_mask[None, :, :]).astype(np.float64)
print(f"[setup] land cells: {int(land_mask.sum())} / {land_mask.size}")

gfed_tm = obs.mean(axis=0).astype(np.float64)
gfed_std = obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc = obs.reshape(16, 12, 180, 360).mean(axis=0)
gfed_peak_month = np.argmax(gfed_cyc, axis=0).astype(np.float32)
mass_w = (w2 * gfed_tm).astype(np.float64)
mass_w_burn = (mass_w * land_mask).astype(np.float64)

def _load_base_params():
    """Load original Model C parameters even after candidate emit overwrites params.json."""
    for path in [MODELS_DIR / "params.BASELINE-before-research.json", MODELS_DIR / "params.json"]:
        obj = json.load(open(path))
        params = obj.get("params", obj)
        if all(k in params for k in ["k1", "D_low", "k2", "D_high", "fire_exp"]):
            return params
    raise RuntimeError("Could not locate original Model C base parameters")


BASE = _load_base_params()


def sig(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(-k * (x - c), -50, 50)))


def supp(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(k * (x - c), -50, 50)))


def hump(x, b, dec):
    b = max(float(b), 1e-12)
    dec = max(float(dec), 1e-12)
    return (1.0 - np.exp(-np.clip(x / b, 0, 500))) * np.exp(-np.clip(x / dec, 0, 500))


def lag_mean(arr, months=3):
    """Causal-ish antecedent mean. First months use available history only."""
    out = np.zeros_like(arr, dtype=np.float32)
    for i in range(arr.shape[0]):
        lo = max(0, i - months)
        hi = i  # previous complete months
        if hi <= lo:
            out[i] = arr[i]
        else:
            out[i] = arr[lo:hi].mean(axis=0)
    return out


print("[setup] precomputing temporal summaries ...")
gpp_mem3 = lag_mean(drivers["gpp_monthly"], 3)
gpp_mem6 = lag_mean(drivers["gpp_monthly"], 6)
dbar_prev = np.concatenate([drivers["dbar"][:1], drivers["dbar"][:-1]], axis=0)
drying_rate = np.maximum(drivers["dbar"] - dbar_prev, 0).astype(np.float32)
p_rel = drivers["p_month"] / (drivers["p_ann"] / 12.0 + 1e-6)


def ed_transform(rate_yr):
    annual_frac = 1.0 - np.exp(-np.minimum(rate_yr, FIRE_MAX_RATE))
    return (annual_frac / 12.0).astype(np.float32)


def fire_f1_wetdry(d, p):
    """Model C plus a global antecedent-fuel/wet-dry pulse term.

    Mechanism: previous-season productivity creates continuous fine fuel; fire is
    boosted only when that fuel is exposed to current drying and not quenched by
    anomalously wet current-month precipitation. This is a single smooth global
    mechanism, not a region route.
    """
    base_rate = fire_C(d, p)
    mem = gpp_mem3 if p.get("mem_months", 3) < 4.5 else gpp_mem6
    fuel_ready = hump(p["mem_af"] * mem, p["mem_b"], p["mem_d"])
    dry_release = sig(d["dbar"], p["rel_k"], p["rel_d"]) * sig(drying_rate, p["dr_k"], p["dr_c"])
    wet_quench = supp(p_rel, p["relp_k"], p["relp_c"])
    pulse = fuel_ready * dry_release * wet_quench
    mult = np.power(np.clip(1.0 + p["pulse_amp"] * pulse, 1e-12, 50.0), p["pulse_exp"])
    return (base_rate * mult).astype(np.float32)


def fire_f1_replace_gpp(d, p):
    """Model C variant replacing instantaneous GPP hump with antecedent GPP hump.

    Ablation/pruning test for F1: asks if memory should replace instantaneous
    productivity rather than add another multiplicative boost.
    """
    onset = sig(d["dbar"], p["k1"], p["D_low"])
    suppress0 = supp(d["dbar"], p["k2"], p["D_high"])
    p_floor = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    p_damp = 1.0 / (1.0 + d["p_month"] / (p["pre_dampen_half"] + 1e-12))
    mem = gpp_mem3 if p.get("mem_months", 3) < 4.5 else gpp_mem6
    gpp_mod = hump(p["gpp_af"] * mem, p["gpp_b"], p["gpp_d"])
    ign_mod = sig(d["t_air"], p["ign_k"], p["ign_c"])
    product = onset * suppress0 * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)


def fire_f2_precip_window(d, p):
    """Model C plus a high-annual-precipitation combustion-window suppressor.

    Mechanism: the original annual precipitation term is only a fuel floor. In
    very wet regimes precipitation also indicates persistent canopy/fuel moisture
    and low curing, so burnability should occupy a window: enough rain to grow
    fuel, not so much that fuel stays wet. This is analogous to a chemical
    reactor with both substrate supply and product inhibition.
    """
    onset = sig(d["dbar"], p["k1"], p["D_low"])
    suppress0 = supp(d["dbar"], p["k2"], p["D_high"])
    p_floor = d["p_ann"] / (d["p_ann"] + p["P_half"] + 1e-12)
    wet_suppress = supp(d["p_ann"], p["Pwet_k"], p["Pwet_c"])
    p_damp = 1.0 / (1.0 + d["p_month"] / (p["pre_dampen_half"] + 1e-12))
    gpp_mod = hump(p["gpp_af"] * d["gpp_monthly"], p["gpp_b"], p["gpp_d"])
    ign_mod = sig(d["t_air"], p["ign_k"], p["ign_c"])
    product = onset * suppress0 * p_floor * wet_suppress * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p["fire_exp"]).astype(np.float32)


def fire_f3_suppressors_fixed(d, p):
    """Baseline Model C times three smooth global missing-limiter suppressors.

    Mechanisms:
    - wet forest/canopy-moisture inhibition at high annual precipitation;
    - hyperarid fuel-discontinuity inhibition by dryness-to-rainfall ratio;
    - extra cool-season thermal ignition inhibition.

    All amplitudes can go to zero, so the family can ablate itself back to C0.
    """
    base = fire_C(d, BASE)
    wet = 1.0 - p["wet_amp"] * sig(d["p_ann"], p["wet_k"], p["wet_c"])
    deficit = d["dbar"] / (d["p_ann"] + p["ratio_p0"])
    arid = 1.0 - p["arid_amp"] * sig(deficit, p["arid_k"], p["arid_c"])
    cool = 1.0 - p["cool_amp"] * supp(d["t_air"], p["cool_k"], p["cool_c"])
    mult = np.clip(wet * arid * cool, 0.0, 1.0)
    return (base * mult).astype(np.float32)


def fire_f3_suppressors_full(d, p):
    """Retuned Model C core plus the same global wet/arid/cool suppressors."""
    base = fire_C(d, p)
    wet = 1.0 - p["wet_amp"] * sig(d["p_ann"], p["wet_k"], p["wet_c"])
    deficit = d["dbar"] / (d["p_ann"] + p["ratio_p0"])
    arid = 1.0 - p["arid_amp"] * sig(deficit, p["arid_k"], p["arid_c"])
    cool = 1.0 - p["cool_amp"] * supp(d["t_air"], p["cool_k"], p["cool_c"])
    mult = np.clip(wet * arid * cool, 0.0, 1.0)
    return (base * mult).astype(np.float32)


FAMILIES = {
    "f1_wetdry": fire_f1_wetdry,
    "f1_replace_gpp": fire_f1_replace_gpp,
    "f2_precip_window": fire_f2_precip_window,
    "f3_suppressors_fixed": fire_f3_suppressors_fixed,
    "f3_suppressors_full": fire_f3_suppressors_full,
}


def predict(family, params):
    fn = FAMILIES[family]
    with np.errstate(over="ignore", invalid="ignore"):
        rate = fn(drivers, params)
    rate = rate * land_mask[None, :, :]
    return ed_transform(rate), rate


def score_BA_ilamb(pred_monthly):
    pred_tm = pred_monthly.mean(axis=0)
    bias_score_per_cell = np.exp(-np.abs(pred_tm - gfed_tm) / gfed_std)
    bias = float((bias_score_per_cell * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_anom = pred_monthly - pred_tm[None, :, :]
    obs_anom = obs - gfed_tm[None, :, :]
    crmse_per_cell = np.sqrt(((pred_anom - obs_anom) ** 2).mean(axis=0))
    rmse_per_cell = np.exp(-crmse_per_cell / gfed_std)
    rmse_s = float((rmse_per_cell * mass_w).sum() / (mass_w.sum() + 1e-12))
    pred_cyc = pred_monthly.reshape(16, 12, 180, 360).mean(axis=0)
    pred_peak = np.argmax(pred_cyc, axis=0).astype(np.float32)
    shift = pred_peak - gfed_peak_month
    shift = np.where(shift > 6, shift - 12, shift)
    shift = np.where(shift < -6, shift + 12, shift)
    seas_per_cell = (1.0 + np.cos(np.abs(shift) / 12.0 * 2.0 * np.pi)) * 0.5
    seas = float((seas_per_cell * mass_w_burn).sum() / (mass_w_burn.sum() + 1e-12))
    obs_flat = gfed_tm[land_mask]
    pred_flat = pred_tm[land_mask]
    pw_flat = w2_burn[land_mask]
    ow = (obs_flat * pw_flat).sum() / pw_flat.sum()
    pw = (pred_flat * pw_flat).sum() / pw_flat.sum()
    oa = obs_flat - ow
    pa = pred_flat - pw
    std0 = max(float(np.sqrt(((oa**2) * pw_flat).sum() / pw_flat.sum())), 1e-12)
    std = max(float(np.sqrt(((pa**2) * pw_flat).sum() / pw_flat.sum())), 1e-12)
    denom = float(np.sqrt(((pa**2) * pw_flat).sum() * ((oa**2) * pw_flat).sum()))
    rho = float((pa * oa * pw_flat).sum() / (denom + 1e-12))
    sigma = std / std0
    spatial = 2.0 * (1.0 + rho) / ((sigma + 1.0 / max(sigma, 1e-12)) ** 2)
    ilamb_tier2 = float((2*bias + 2*rmse_s + seas + spatial) / 6.0)
    simple = float(np.mean([bias, rmse_s, seas, spatial]))
    return {"bias": bias, "rmse": rmse_s, "seas": seas, "spatial": float(spatial), "overall_tier2": ilamb_tier2, "overall_simple": simple}


def suggest_base(trial):
    ranges = {
        "k1": (1e-5, 1e-1), "D_low": (1e0, 1e4),
        "k2": (1e-5, 1e-1), "D_high": (1e1, 1e5),
        "fire_exp": (0.35, 6.0), "P_half": (1e0, 1e4),
        "pre_dampen_half": (1e-2, 1e3), "gpp_af": (1e-3, 1e2),
        "gpp_b": (1e-5, 1e1), "gpp_d": (1e-2, 1e3),
        "ign_k": (1e-3, 1e1), "ign_c": (1e-1, 1e3),
    }
    return {name: trial.suggest_float(name, lo, hi, log=True) for name, (lo, hi) in ranges.items()}


def suggest_suppressors(trial):
    return {
        "wet_amp": trial.suggest_float("wet_amp", 0.0, 0.95),
        "wet_k": trial.suggest_float("wet_k", 1e-5, 5e-2, log=True),
        "wet_c": trial.suggest_float("wet_c", 300.0, 5000.0, log=True),
        "ratio_p0": trial.suggest_float("ratio_p0", 1.0, 500.0, log=True),
        "arid_amp": trial.suggest_float("arid_amp", 0.0, 0.95),
        "arid_k": trial.suggest_float("arid_k", 1e-3, 10.0, log=True),
        "arid_c": trial.suggest_float("arid_c", 1.0, 80.0, log=True),
        "cool_amp": trial.suggest_float("cool_amp", 0.0, 0.95),
        "cool_k": trial.suggest_float("cool_k", 1e-3, 10.0, log=True),
        "cool_c": trial.suggest_float("cool_c", -5.0, 25.0),
    }


def suggest_f1(trial, family):
    if family == "f3_suppressors_fixed":
        return suggest_suppressors(trial)
    p = suggest_base(trial)
    if family == "f3_suppressors_full":
        p.update(suggest_suppressors(trial))
        return p
    if family == "f1_wetdry":
        p.update({
            "mem_months": trial.suggest_categorical("mem_months", [3.0, 6.0]),
            "mem_af": trial.suggest_float("mem_af", 1e-3, 1e2, log=True),
            "mem_b": trial.suggest_float("mem_b", 1e-5, 1e1, log=True),
            "mem_d": trial.suggest_float("mem_d", 1e-2, 1e3, log=True),
            "rel_k": trial.suggest_float("rel_k", 1e-5, 1e-1, log=True),
            "rel_d": trial.suggest_float("rel_d", 1e0, 1e4, log=True),
            "dr_k": trial.suggest_float("dr_k", 1e-4, 1e0, log=True),
            "dr_c": trial.suggest_float("dr_c", 1e-3, 1e3, log=True),
            "relp_k": trial.suggest_float("relp_k", 1e-2, 1e2, log=True),
            "relp_c": trial.suggest_float("relp_c", 0.05, 10.0, log=True),
            "pulse_amp": trial.suggest_float("pulse_amp", 0.0, 10.0),
            "pulse_exp": trial.suggest_float("pulse_exp", 0.25, 3.0),
        })
    elif family == "f1_replace_gpp":
        p.update({"mem_months": trial.suggest_categorical("mem_months", [3.0, 6.0])})
    elif family == "f2_precip_window":
        p.update({
            "Pwet_k": trial.suggest_float("Pwet_k", 1e-5, 5e-2, log=True),
            "Pwet_c": trial.suggest_float("Pwet_c", 200.0, 6000.0, log=True),
        })
    return p


def warm_for_family(family):
    if family == "f3_suppressors_fixed":
        return {
            "wet_amp": 0.0, "wet_k": 1e-4, "wet_c": 2000.0,
            "ratio_p0": 50.0, "arid_amp": 0.0, "arid_k": 0.1, "arid_c": 20.0,
            "cool_amp": 0.0, "cool_k": 0.1, "cool_c": 10.0,
        }
    p = dict(BASE)
    if family == "f3_suppressors_full":
        p.update({
            "wet_amp": 0.0, "wet_k": 1e-4, "wet_c": 2000.0,
            "ratio_p0": 50.0, "arid_amp": 0.0, "arid_k": 0.1, "arid_c": 20.0,
            "cool_amp": 0.0, "cool_k": 0.1, "cool_c": 10.0,
        })
        return p
    if family == "f1_wetdry":
        p.update({
            "mem_months": 3.0, "mem_af": p["gpp_af"], "mem_b": p["gpp_b"], "mem_d": p["gpp_d"],
            "rel_k": p["k1"], "rel_d": p["D_low"], "dr_k": 0.01, "dr_c": 1.0,
            "relp_k": 1.0, "relp_c": 1.0, "pulse_amp": 0.0, "pulse_exp": 1.0,
        })
    elif family == "f1_replace_gpp":
        p.update({"mem_months": 3.0})
    elif family == "f2_precip_window":
        # Nearly inactive high-rainfall suppressor as baseline-equivalent warm start.
        p.update({"Pwet_k": 1e-5, "Pwet_c": 6000.0})
    return p


def objective_factory(family):
    def objective(trial):
        p = suggest_f1(trial, family)
        pred, _ = predict(family, p)
        s = score_BA_ilamb(pred)
        # The fast scorer's simple mean reproduces the historical Model C
        # internal objective scale better than its tier-2 reconstruction; final
        # acceptance still uses official ILAMB. Tiny complexity/instability guard
        # discourages pathological pulse boosts without preventing discovery.
        penalty = 0.0
        if family == "f1_wetdry":
            penalty += 0.001 * math.log1p(max(p.get("pulse_amp", 0.0), 0.0))
        return -(s["overall_simple"] - penalty)
    return objective


def save_candidate(candidate, family, params, scores, runtime_min, n_trials, rate=None):
    out = {
        "candidate": candidate,
        "family": family,
        "n_trials": n_trials,
        "runtime_min": runtime_min,
        "fire_max_rate": FIRE_MAX_RATE,
        "scores_internal": scores,
        "mechanistic_summary": (
            "Global antecedent-fuel/wet-dry pulse: previous GPP represents fuel continuity; "
            "dryness/drying releases burnability; anomalously wet current months quench combustion."
            if family == "f1_wetdry" else
            "Ablation: replace instantaneous GPP hump with antecedent GPP memory hump."
            if family == "f1_replace_gpp" else
            "Global annual precipitation combustion window: rainfall grows fuel at low-mid values but persistent high precipitation suppresses curing/flammability."
            if family == "f2_precip_window" else
            "Fixed-baseline global suppressors for wet canopy moisture, hyperarid fuel discontinuity, and cool-season ignition limitation."
        ),
        "params": params,
    }
    if rate is not None:
        out["raw_rate_diag"] = {
            "land_mean_yr-1": float((rate * w3_land).sum() / (w3_land.sum() + 1e-12)),
            "max_yr-1": float(np.nanmax(rate)),
            "cap_binding_count": int(((rate > FIRE_MAX_RATE) & land_mask[None, :, :]).sum()),
        }
    path = RESEARCH_DIR / f"{candidate}.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"[write] {path}")


def optimize(args):
    family = args.family
    candidate = args.candidate
    sampler = optuna.samplers.TPESampler(seed=SEED, multivariate=True, warn_independent_sampling=False)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.enqueue_trial(warm_for_family(family))
    t0 = time.time()
    last = t0
    print(f"[opt] family={family} candidate={candidate} trials={N_TRIALS}")

    def cb(st, tr):
        nonlocal last
        if time.time() - last > 30:
            print(f"  trial {len(st.trials):4d}/{N_TRIALS} best={-st.best_value:.5f}")
            last = time.time()

    study.optimize(objective_factory(family), n_trials=N_TRIALS, callbacks=[cb])
    runtime = (time.time() - t0) / 60.0
    best = study.best_params
    pred, rate = predict(family, best)
    scores = score_BA_ilamb(pred)
    print(f"[done] best internal tier2={scores['overall_tier2']:.6f} scores={scores}")
    save_candidate(candidate, family, best, scores, runtime, len(study.trials), rate=rate)


def emit(args):
    cand = json.load(open(RESEARCH_DIR / f"{args.candidate}.json"))
    family = cand["family"]
    p = cand["params"]
    pred, rate = predict(family, p)
    pred_hd = uncoarsen(np.where(land_mask[None, :, :], pred, np.nan).astype(np.float32))
    times = [cftime.DatetimeNoLeap(y, m, 15) for y in YEARS for m in range(1, 13)]
    lat = np.arange(-89.75, 90.0, 0.5)
    lon = np.arange(-179.75, 180.0, 0.5)
    ds = xr.Dataset(
        {"burntArea": (("time", "lat", "lon"), pred_hd,
                       {"units": "1", "standard_name": "burnt_area_fraction",
                        "long_name": "Burnt Area Fraction"})},
        coords={"time": ("time", times), "lat": ("lat", lat), "lon": ("lon", lon)},
        attrs={"title": f"ED fire research candidate {args.candidate} ({family})",
               "Conventions": "CF-1.7",
               "transform": f"monthly_frac = (1 - exp(-min(rate_yr, {FIRE_MAX_RATE}) * 1yr)) / 12"})
    ds = add_cf_bounds(ds)
    enc = {"burntArea": {"zlib": True, "complevel": 4, "_FillValue": 1e20},
           "time": {"units": "days since 2001-01-01 00:00:00", "calendar": "noleap", "dtype": "float64"},
           "time_bounds": {"units": "days since 2001-01-01 00:00:00", "calendar": "noleap", "dtype": "float64"}}
    OUT_NC.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_NC.with_suffix(".nc.tmp")
    ds.to_netcdf(tmp, encoding=enc, format="NETCDF4_CLASSIC")
    os.replace(tmp, OUT_NC)
    # Save params.json too so reproduce_modelC remains transparent only if manually restored.
    backup = MODELS_DIR / "params.BASELINE-before-research.json"
    if not backup.exists():
        shutil.copy(MODELS_DIR / "params.json", backup)
    research_params = {
        "model": f"Research candidate {args.candidate}: {family}",
        "candidate_json": str((RESEARCH_DIR / f"{args.candidate}.json").relative_to(REPO)),
        "params": p,
    }
    (MODELS_DIR / "params.json").write_text(json.dumps(research_params, indent=2))
    print(f"[write] {OUT_NC} ({OUT_NC.stat().st_size/1e6:.1f} MB)")
    print(f"[write] {MODELS_DIR / 'params.json'}")
    print(f"[diag] raw land mean={float((rate*w3_land).sum()/(w3_land.sum()+1e-12)):.6g} max={float(rate.max()):.6g}")


def score_baseline(args):
    pred = ed_transform(fire_C(drivers, BASE) * land_mask[None, :, :])
    print(json.dumps(score_BA_ilamb(pred), indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("score-baseline")
    op = sub.add_parser("optimize")
    op.add_argument("--family", choices=sorted(FAMILIES), required=True)
    op.add_argument("--candidate", required=True)
    em = sub.add_parser("emit")
    em.add_argument("--candidate", required=True)
    args = ap.parse_args()
    if args.cmd == "score-baseline":
        score_baseline(args)
    elif args.cmd == "optimize":
        optimize(args)
    elif args.cmd == "emit":
        emit(args)


if __name__ == "__main__":
    main()
