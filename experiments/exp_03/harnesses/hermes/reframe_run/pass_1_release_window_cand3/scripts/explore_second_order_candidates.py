"""Second-order constrained fire model mechanisms after first-cycle failures.

This continuation deliberately starts from fixed original Model C and adds only a small
number of global, physically interpretable interaction terms. The first cycle showed:
  * blunt high-annual-precipitation suppression repairs weak wet/temperate regions
    but loses global spatial skill, especially African/boreal fire belts;
  * antecedent fuel charging alone also damages spatial structure;
  * month-to-month drydown by itself is pruned/nearly neutral.

Therefore these families test conditional interactions that should activate only
when multiple physical gates agree (wet canopy + low deficit, charged fuel + dry
release, high productivity + moisture persistence, hyperarid fuel limit + heat).
No formula uses latitude/longitude, named regions, per-cell lookup, residual maps,
or external data. GFED appears only in the screening objective.
"""
from __future__ import annotations

import argparse, json, os, sys, time
from pathlib import Path
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context, base_product, ed_transform, score, write_nc, WEAK_REGIONS, sig, supp

REPO = Path(__file__).resolve().parents[1]
FAMILIES = [
    "wet_x_lowdef",          # wet suppression only when annual wetness and low current deficit coincide
    "wet_x_persist",         # wet suppression only when annual wetness and persistent recent rainfall coincide
    "wet_supp_fuel_release", # wet suppression plus boost for charged fuels released by dryness
    "gpp_wet_cap",           # high-productivity suppression conditional on wetness/persistent moisture
    "hyperarid_balance",     # sharper fuel floor in hyperarid cells plus hot-dry ignition compensation
    "curing_window",         # drydown/curing pulse conditioned on intermediate annual precip/productivity
]


def clip01(x):
    return np.clip(x, 0.0, 1.0)


def weighted_region_summary(ctx, pred):
    regs = {r: score(ctx, pred, ctx.region_masks[r]) for r in ctx.region_masks}
    weak_vals = [regs[r]["overall"] for r in WEAK_REGIONS]
    strong = ["nhaf", "shaf", "bona", "boas", "aust", "ceas"]
    strong_vals = [regs[r]["overall"] for r in strong]
    return regs, float(np.mean(weak_vals)), float(np.min(weak_vals)), float(np.mean(strong_vals)), float(np.min(strong_vals))


def family_factor(ctx: Context, family: str, p: dict):
    d = ctx.d
    gpp = d["gpp_monthly"]
    # Gates are shaped so 0 means inactive physical state, 1 means active.
    wet_ann = sig(d["p_ann"], p.get("wet_k", 0.004), p.get("wet_c", 1800.0))
    low_def = supp(d["dbar"], p.get("ld_k", 0.004), p.get("ld_c", 800.0))
    persist_rain = sig(ctx.p3, p.get("pr_k", 0.03), p.get("pr_c", 45.0))
    dry_now = sig(d["dbar"], p.get("dry_k", 0.004), p.get("dry_c", 300.0))
    drydown = sig(ctx.d_delta, p.get("dd_k", 0.01), p.get("dd_c", 0.0))
    warm = sig(d["t_air"], p.get("hot_k", 0.15), p.get("hot_c", 290.0))
    high_gpp = sig(gpp, p.get("gpp_hi_k", 3.0), p.get("gpp_hi_c", 1.0))
    mid_p = sig(d["p_ann"], p.get("p_low_k", 0.006), p.get("p_low_c", 250.0)) * supp(d["p_ann"], p.get("p_high_k", 0.002), p.get("p_high_c", 2600.0))

    if family == "wet_x_lowdef":
        # Analogy: a circuit breaker trips only if both overcurrent and heat are present.
        # Prior wet suppression was too blunt; this suppresses only wet cells that also lack current deficit.
        state = wet_ann * low_def
        return 1.0 - p["amp"] * state
    if family == "wet_x_persist":
        # Wet forest/canopy nonflammability requires not just high annual rain but recent persistent wetting.
        state = wet_ann * persist_rain
        return 1.0 - p["amp"] * state
    if family == "wet_supp_fuel_release":
        # Reservoir analogy: wet climate can suppress closed canopy, but charged fine fuels released into dry
        # months can compensate in savannas/monsoon margins. Both terms are global and cell-state driven.
        suppress_state = wet_ann * (p["mix_lowdef"] * low_def + (1 - p["mix_lowdef"]) * persist_rain)
        charge = 1.0 - np.exp(-np.clip((ctx.gpp3 * p["gpp_charge"] + ctx.p3 * p["p_charge"]) / (p["charge_half"] + 1e-12), 0, 80))
        release = charge * dry_now * (p["rel_drydown_mix"] * drydown + (1 - p["rel_drydown_mix"]))
        return (1.0 - p["amp"] * suppress_state) * (1.0 + p["boost"] * release)
    if family == "gpp_wet_cap":
        # Productive wet canopy/fragmentation cap: high GPP suppresses only when moisture persistence says
        # biomass is closed/wet rather than grass fuel. This avoids a naked high-GPP penalty.
        state = high_gpp * (p["mix_ann"] * wet_ann + (1 - p["mix_ann"]) * persist_rain)
        return 1.0 - p["amp"] * state
    if family == "hyperarid_balance":
        # Combustion triangle: deserts are fuel-limited, but hot dry semi-arid cells should not be over-killed.
        arid_lack = supp(d["p_ann"], p["arid_k"], p["arid_c"])
        hotdry = warm * dry_now
        return (1.0 - p["amp"] * arid_lack) * (1.0 + p["boost"] * hotdry * mid_p)
    if family == "curing_window":
        # Wildfire analogue to phase transition/nucleation: curing pulse matters only in intermediate-fuel
        # climates and productivity windows, explaining why first-cycle naked drydown was neutral.
        gpp_mid = sig(gpp, p["gpp_lo_k"], p["gpp_lo_c"]) * supp(gpp, p["gpp_hi2_k"], p["gpp_hi2_c"])
        pulse = drydown * dry_now * mid_p * gpp_mid
        return 1.0 + p["boost"] * pulse
    raise ValueError(family)


def rate_for(ctx, family, p, base_p):
    prod = base_product(ctx, base_p)
    fac = family_factor(ctx, family, p)
    prod2 = np.clip(prod * fac, 0, None)
    exp = base_p["fire_exp"] * p.get("exp_mult", 1.0)
    rate = np.power(prod2, exp).astype(np.float32) * ctx.land[None,:,:]
    return rate


def objective(ctx, pred):
    g = score(ctx, pred)
    regs, weak_mean, weak_min, strong_mean, strong_min = weighted_region_summary(ctx, pred)
    # Preserve global spatial and strong fire belts; first-cycle failures were spatial losses.
    spatial_floor_penalty = max(0.0, 0.752 - g["spatial"]) * 2.0
    strong_penalty = max(0.0, 0.660 - strong_min) * 0.5
    return 0.78*g["overall"] + 0.10*weak_mean + 0.04*weak_min + 0.04*g["spatial"] + 0.04*strong_mean - spatial_floor_penalty - strong_penalty


def suggest(trial, name, lo, hi, log=False):
    return trial.suggest_float(name, lo, hi, log=log)


def sample_params(trial, family):
    p = {"exp_mult": suggest(trial, "exp_mult", 0.92, 1.08)}
    if family in ("wet_x_lowdef", "wet_x_persist", "wet_supp_fuel_release", "gpp_wet_cap"):
        p.update({
            "amp": suggest(trial, "amp", 0.0, 0.45),
            "wet_k": suggest(trial, "wet_k", 5e-4, 2e-2, True),
            "wet_c": suggest(trial, "wet_c", 600.0, 5000.0, True),
        })
    if family in ("wet_x_lowdef", "wet_supp_fuel_release"):
        p.update({"ld_k": suggest(trial, "ld_k", 5e-4, 5e-2, True), "ld_c": suggest(trial, "ld_c", 50.0, 3000.0, True)})
    if family in ("wet_x_persist", "wet_supp_fuel_release", "gpp_wet_cap"):
        p.update({"pr_k": suggest(trial, "pr_k", 1e-3, 2e-1, True), "pr_c": suggest(trial, "pr_c", 3.0, 250.0, True)})
    if family == "wet_supp_fuel_release":
        p.update({
            "mix_lowdef": suggest(trial, "mix_lowdef", 0.0, 1.0),
            "gpp_charge": suggest(trial, "gpp_charge", 1e-3, 20.0, True),
            "p_charge": suggest(trial, "p_charge", 1e-4, 2.0, True),
            "charge_half": suggest(trial, "charge_half", 1e-3, 100.0, True),
            "dry_k": suggest(trial, "dry_k", 5e-4, 5e-2, True),
            "dry_c": suggest(trial, "dry_c", 20.0, 2500.0, True),
            "dd_k": suggest(trial, "dd_k", 5e-4, 2e-1, True),
            "dd_c": suggest(trial, "dd_c", -50.0, 300.0),
            "rel_drydown_mix": suggest(trial, "rel_drydown_mix", 0.0, 1.0),
            "boost": suggest(trial, "boost", 0.0, 0.80),
        })
    if family == "gpp_wet_cap":
        p.update({
            "gpp_hi_k": suggest(trial, "gpp_hi_k", 0.05, 20.0, True),
            "gpp_hi_c": suggest(trial, "gpp_hi_c", 0.01, 8.0, True),
            "mix_ann": suggest(trial, "mix_ann", 0.0, 1.0),
        })
    if family == "hyperarid_balance":
        p.update({
            "amp": suggest(trial, "amp", 0.0, 0.60),
            "boost": suggest(trial, "boost", 0.0, 0.80),
            "arid_k": suggest(trial, "arid_k", 5e-4, 5e-2, True),
            "arid_c": suggest(trial, "arid_c", 20.0, 1000.0, True),
            "hot_k": suggest(trial, "hot_k", 5e-3, 1.0, True),
            "hot_c": suggest(trial, "hot_c", 270.0, 315.0),
            "dry_k": suggest(trial, "dry_k", 5e-4, 5e-2, True),
            "dry_c": suggest(trial, "dry_c", 20.0, 2500.0, True),
            "p_low_k": suggest(trial, "p_low_k", 5e-4, 5e-2, True),
            "p_low_c": suggest(trial, "p_low_c", 50.0, 1200.0, True),
            "p_high_k": suggest(trial, "p_high_k", 5e-4, 2e-2, True),
            "p_high_c": suggest(trial, "p_high_c", 800.0, 5000.0, True),
        })
    if family == "curing_window":
        p.update({
            "boost": suggest(trial, "boost", 0.0, 1.2),
            "dd_k": suggest(trial, "dd_k", 5e-4, 2e-1, True),
            "dd_c": suggest(trial, "dd_c", -100.0, 400.0),
            "dry_k": suggest(trial, "dry_k", 5e-4, 5e-2, True),
            "dry_c": suggest(trial, "dry_c", 20.0, 2500.0, True),
            "p_low_k": suggest(trial, "p_low_k", 5e-4, 5e-2, True),
            "p_low_c": suggest(trial, "p_low_c", 50.0, 1200.0, True),
            "p_high_k": suggest(trial, "p_high_k", 5e-4, 2e-2, True),
            "p_high_c": suggest(trial, "p_high_c", 800.0, 5000.0, True),
            "gpp_lo_k": suggest(trial, "gpp_lo_k", 0.05, 20.0, True),
            "gpp_lo_c": suggest(trial, "gpp_lo_c", 0.001, 2.0, True),
            "gpp_hi2_k": suggest(trial, "gpp_hi2_k", 0.05, 20.0, True),
            "gpp_hi2_c": suggest(trial, "gpp_hi2_c", 0.05, 12.0, True),
        })
    return p


def neutral_params(family):
    p = {"exp_mult": 1.0}
    if family in ("wet_x_lowdef", "wet_x_persist", "wet_supp_fuel_release", "gpp_wet_cap", "hyperarid_balance"):
        p["amp"] = 0.0
    if family in ("wet_supp_fuel_release", "hyperarid_balance", "curing_window"):
        p["boost"] = 0.0
    # Fill defaults for calculations if enqueued trial lacks some? Optuna will suggest missing, so only neutral knobs needed.
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=FAMILIES)
    ap.add_argument("--trials", type=int, default=700)
    ap.add_argument("--seed", type=int, default=20260519)
    ap.add_argument("--outdir", default="models/explore2")
    ap.add_argument("--write-nc", action="store_true")
    args = ap.parse_args()
    ctx = Context()
    base_p = json.load(open(REPO/"models/C/params.json"))["params"]
    sampler = optuna.samplers.TPESampler(seed=args.seed, multivariate=True, group=True)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    # Enqueue a neutral-ish trial by letting objective use full default suggestions is brittle, so skip manual enqueue.
    t0 = time.time()
    def obj(trial):
        p = sample_params(trial, args.family)
        pred = ed_transform(rate_for(ctx, args.family, p, base_p))
        return objective(ctx, pred)
    def cb(st, tr):
        if len(st.trials) % 50 == 0:
            print(f"[opt2] {args.family} {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m", flush=True)
    study.optimize(obj, n_trials=args.trials, callbacks=[cb])
    p = study.best_params
    rate = rate_for(ctx, args.family, p, base_p)
    pred = ed_transform(rate)
    glob = score(ctx, pred)
    regs, weak_mean, weak_min, strong_mean, strong_min = weighted_region_summary(ctx, pred)
    out = {
        "family": args.family,
        "n_trials": len(study.trials),
        "seed": args.seed,
        "fast_objective": study.best_value,
        "fast_global": glob,
        "fast_regions": regs,
        "weak_mean": weak_mean,
        "weak_min": weak_min,
        "strong_mean": strong_mean,
        "strong_min": strong_min,
        "params": p,
        "diagnostics": {
            "raw_land_mean": float((rate*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),
            "raw_max": float(rate.max()),
            "factor_land_mean": float((family_factor(ctx,args.family,p)*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),
            "factor_min": float(np.nanmin(family_factor(ctx,args.family,p))),
            "factor_max": float(np.nanmax(family_factor(ctx,args.family,p))),
        },
        "mechanism_note": __doc__,
    }
    outdir = REPO / args.outdir / args.family
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"result.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"family":args.family,"best":study.best_value,"global":glob,"weak_mean":weak_mean,"strong_min":strong_min,"diag":out["diagnostics"],"out":str(outdir/"result.json")}, indent=2))
    if args.write_nc:
        write_nc(ctx, pred, outdir/"burntArea.nc", f"second order candidate {args.family}")
        print(f"wrote {outdir/'burntArea.nc'}")

if __name__ == "__main__":
    main()
