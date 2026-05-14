"""Generate TRENDY-format burntArea.nc for Model C plus a candidate extension.

Candidate spec is JSON with an `extra` object or direct extra keys. Uses only the
allowed Model C driver inputs. Writes ilamb/MODELS/ED-ModelC-final/burntArea.nc
so the existing official ILAMB wrappers can be reused.
"""
from __future__ import annotations

import json, os, sys
from pathlib import Path

import cftime
import numpy as np
import xarray as xr

from reproduce_modelC import add_cf_bounds, fire_C, load_drivers, load_gfed_1deg, uncoarsen

REPO = Path(__file__).resolve().parents[1]
YEARS = list(range(2001, 2017))
N_MONTHS = 192
FIRE_MAX_RATE = float(os.environ.get("FIRE_MAX_RATE", "5.0"))


def sig(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(-k * (x - c), -50, 50)))


def supp(x, k, c):
    return 1.0 / (1.0 + np.exp(np.clip(k * (x - c), -50, 50)))


def hump(x, b, dec):
    b = max(float(b), 1e-9); dec = max(float(dec), 1e-9)
    return (1.0 - np.exp(-np.clip(x / b, 0, 500))) * np.exp(-np.clip(x / dec, 0, 500))


def lag_mean(arr, window):
    return np.mean([np.roll(arr, lag, axis=0) for lag in range(1, int(window)+1)], axis=0).astype(np.float32)


def candidate_rate(drivers, params, extra, land_mask):
    gpp = drivers["gpp_monthly"]
    if extra.get("family") in ("curing_gated_lag_fuel", "precip_conc_wet_plus_curing_lag") and extra.get("lag_alpha", 0.0) > 0:
        # Round 2 Q2: antecedent GPP only becomes fuel when current dry-season
        # indicators imply curing/accessibility.
        a = float(extra["lag_alpha"]); w = int(extra["gpp_lag_window"])
        d_gate = sig(drivers["dbar"], float(extra.get("D_cure_k", 0.01)), float(extra.get("D_cure_c", 100.0)))
        p_half = float(extra.get("P_cure_half", 5.0)); p_pow = float(extra.get("P_cure_pow", 2.0))
        p_gate = 1.0 / (1.0 + np.power(np.clip(drivers["p_month"]/(p_half+1e-12), 0, 1e6), p_pow))
        cure = 1.0 - (1.0 - d_gate) * (1.0 - p_gate)
        gpp = (1.0-a*cure)*gpp + (a*cure)*lag_mean(drivers["gpp_monthly"], w)
    elif extra.get("gpp_lag_alpha", 0.0) > 0:
        a = float(extra["gpp_lag_alpha"]); w = int(extra["gpp_lag_window"])
        gpp = (1.0-a)*gpp + a*lag_mean(drivers["gpp_monthly"], w)
    p_month = drivers["p_month"]
    if extra.get("precip_memory_alpha", 0.0) > 0:
        a = float(extra["precip_memory_alpha"]); w = int(extra["precip_memory_window"])
        p_month = (1.0-a)*p_month + a*lag_mean(drivers["p_month"], w)
    onset = sig(drivers["dbar"], params["k1"], params["D_low"])
    dry_suppress = supp(drivers["dbar"], params["k2"], params["D_high"])
    p_floor = drivers["p_ann"] / (drivers["p_ann"] + params["P_half"] + 1e-12)
    p_damp = 1.0 / (1.0 + p_month / (params["pre_dampen_half"] + 1e-12))
    gpp_mod = hump(params["gpp_af"] * gpp, params["gpp_b"], params["gpp_d"])
    ign_mod = sig(drivers["t_air"], params["ign_k"], params["ign_c"])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod
    if extra.get("wet_strength", 0.0) > 0:
        s = float(extra["wet_strength"]); half = float(extra["P_wet_half"]); pow_ = float(extra["P_wet_pow"])
        wet = 1.0 / (1.0 + np.power(np.clip(drivers["p_ann"]/(half+1e-12), 0, 1e6), pow_))
        if extra.get("family") == "dryseason_wet_relief":
            # Round 2 Q1: annual wetness suppression relieved by current dry-season
            # indicators, using only Dbar and monthly precipitation.
            rel_s = float(extra.get("relief_strength", 0.0))
            d_k = float(extra.get("D_relief_k", 0.01)); d_c = float(extra.get("D_relief_c", 100.0))
            p_half = float(extra.get("P_relief_half", 5.0)); p_pow = float(extra.get("P_relief_pow", 2.0))
            d_relief = sig(drivers["dbar"], d_k, d_c)
            p_relief = 1.0 / (1.0 + np.power(np.clip(drivers["p_month"]/(p_half+1e-12), 0, 1e6), p_pow))
            dry_relief = 1.0 - (1.0 - d_relief) * (1.0 - p_relief)
            wet_mult = 1.0 - s * (1.0 - wet) * (1.0 - rel_s * dry_relief)
            product = product * np.clip(wet_mult, 0.0, 2.0)
        elif extra.get("family") in ("precip_concentration_wet_relief", "precip_conc_wet_plus_curing_lag"):
            # Round 2 Q3: annual wetness suppression relieved by trailing-12
            # dry-month fraction, a precipitation concentration / dry-season
            # contrast signal derived only from monthly precipitation.
            thr = float(extra.get("dry_month_threshold", 10.0))
            dry = (drivers["p_month"] < thr).astype(np.float32)
            dry_frac = np.mean([np.roll(dry, lag, axis=0) for lag in range(0, 12)], axis=0).astype(np.float32)
            season_gate = sig(dry_frac, float(extra.get("dryfrac_k", 5.0)), float(extra.get("dryfrac_c", 0.3)))
            d_support = sig(drivers["dbar"], float(extra.get("D_support_k", 0.01)), float(extra.get("D_support_c", 100.0)))
            dw = float(extra.get("d_support_weight", 0.0)); rel_s = float(extra.get("relief_strength", 0.0))
            relief = season_gate * ((1.0 - dw) + dw * d_support)
            wet_mult = 1.0 - s * (1.0 - wet) * (1.0 - rel_s * relief)
            product = product * np.clip(wet_mult, 0.0, 2.0)
        else:
            product = product * ((1.0-s) + s*wet)
    if extra.get("drydown_strength", 0.0) > 0:
        s = float(extra["drydown_strength"]); amp = float(extra["drydown_amp"]); half = float(extra["drydown_half"])
        prev_d = np.roll(drivers["dbar"], 1, axis=0)
        dd = np.maximum(drivers["dbar"] - prev_d, 0.0)
        drypulse = 1.0 + amp * dd/(dd + half + 1e-12)
        product = product * ((1.0-s) + s*drypulse)
    rate = np.power(np.clip(product, 0, None), params["fire_exp"]).astype(np.float32)
    return rate * land_mask[None,:,:]


def write_nc(pred, title):
    pred_hd = uncoarsen(pred)
    times = [cftime.DatetimeNoLeap(y, m, 15) for y in YEARS for m in range(1,13)]
    lat = np.arange(-89.75, 90.0, 0.5)
    lon = np.arange(-179.75, 180.0, 0.5)
    ds = xr.Dataset(
        {"burntArea": (("time","lat","lon"), pred_hd, {"units":"1", "standard_name":"burnt_area_fraction", "long_name":"Burnt Area Fraction"})},
        coords={"time": ("time", times), "lat": ("lat", lat), "lon": ("lon", lon)},
        attrs={"title": title, "Conventions":"CF-1.7", "transform": f"monthly_frac=(1-exp(-min(rate,{FIRE_MAX_RATE})))/12"},
    )
    ds = add_cf_bounds(ds)
    dst = REPO / "ilamb" / "MODELS" / "ED-ModelC-final" / "burntArea.nc"
    dst.parent.mkdir(parents=True, exist_ok=True)
    enc = {"burntArea":{"zlib":True,"complevel":4,"_FillValue":1e20},
           "time":{"units":"days since 2001-01-01 00:00:00","calendar":"noleap","dtype":"float64"},
           "time_bounds":{"units":"days since 2001-01-01 00:00:00","calendar":"noleap","dtype":"float64"}}
    tmp = dst.with_suffix(".nc.tmp")
    ds.to_netcdf(tmp, encoding=enc, format="NETCDF4_CLASSIC")
    os.replace(tmp, dst)
    print(f"[write] {dst} ({dst.stat().st_size/1e6:.1f} MB)")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: generate_candidate_output.py SPEC_JSON [candidate_name]")
    spec_path = Path(sys.argv[1])
    spec = json.loads(spec_path.read_text())
    extra = spec.get("extra", spec.get("best_extra", spec))
    name = sys.argv[2] if len(sys.argv) > 2 else spec.get("name", spec_path.stem)
    params = json.loads((REPO/"models"/"C"/"params.json").read_text())["params"]
    drivers = load_drivers()
    obs = load_gfed_1deg()
    land_mask = (obs > 0).any(axis=0)
    rate = candidate_rate(drivers, params, extra, land_mask)
    raw_lm = float((rate * land_mask[None,:,:]).sum() / (land_mask.sum() * N_MONTHS + 1e-12))
    pred = ((1.0 - np.exp(-np.minimum(rate, FIRE_MAX_RATE))) / 12.0).astype(np.float32)
    pred = np.where(land_mask[None,:,:], pred, np.nan).astype(np.float32)
    print(f"[candidate] {name}: extra={extra}")
    print(f"[diag] raw unweighted land/time mean={raw_lm:.6g}, max={float(np.nanmax(rate)):.6g}")
    write_nc(pred, f"ED-ModelC-final candidate {name}")

if __name__ == "__main__":
    main()
