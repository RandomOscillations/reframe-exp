"""Round 2 Q2 search: curing-gated antecedent GPP fuel.

Physical hypothesis:
Uniform LAG-FUEL-v1 improves global seasonality/Australia but damages MIDE,
SEAS, EURO, TENA, CEAS, NHAF, SHAF, BOAS. Antecedent productivity should only
act as burnable cured fuel when current dry-season conditions exist. Gate the
lagged-GPP replacement by Dbar and current low precipitation.

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
SEED = int(os.environ.get("SEED", "31"))
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
WINDOWS=[1,2,3,4,6,9,12]

def lag_mean(arr, window):
    return np.mean([np.roll(arr, lag, axis=0) for lag in range(1,int(window)+1)], axis=0).astype(np.float32)
gpp_lags={w:lag_mean(drivers["gpp_monthly"],w) for w in WINDOWS}

def sig(x,k,c): return 1.0/(1.0+np.exp(np.clip(-k*(x-c),-50,50)))
def supp(x,k,c): return 1.0/(1.0+np.exp(np.clip(k*(x-c),-50,50)))
def hump(x,b,dec):
    b=max(float(b),1e-9); dec=max(float(dec),1e-9)
    return (1.0-np.exp(-np.clip(x/b,0,500)))*np.exp(-np.clip(x/dec,0,500))

def predict(extra):
    p=BASE
    d_gate=sig(drivers["dbar"], extra["D_cure_k"], extra["D_cure_c"])
    p_gate=1.0/(1.0+np.power(np.clip(drivers["p_month"]/(extra["P_cure_half"]+1e-12),0,1e6), extra["P_cure_pow"]))
    # Allow either accumulated dryness or rain-free current month to express curing.
    cure=1.0-(1.0-d_gate)*(1.0-p_gate)
    a=extra["lag_alpha"]
    lag=gpp_lags[int(extra["gpp_lag_window"])]
    gpp_eff=(1.0-a*cure)*drivers["gpp_monthly"] + (a*cure)*lag
    onset=sig(drivers["dbar"],p["k1"],p["D_low"])
    dry_suppress=supp(drivers["dbar"],p["k2"],p["D_high"])
    p_floor=drivers["p_ann"]/(drivers["p_ann"]+p["P_half"]+1e-12)
    p_damp=1.0/(1.0+drivers["p_month"]/(p["pre_dampen_half"]+1e-12))
    gpp_mod=hump(p["gpp_af"]*gpp_eff,p["gpp_b"],p["gpp_d"])
    ign_mod=sig(drivers["t_air"],p["ign_k"],p["ign_c"])
    product=onset*dry_suppress*p_floor*p_damp*gpp_mod*ign_mod
    rate=np.power(np.clip(product,0,None),p["fire_exp"]).astype(np.float32)
    rate*=land_mask[None,:,:]
    return ((1.0-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12.0).astype(np.float32)

def score(pred):
    pred_tm=pred.mean(axis=0).astype(np.float64)
    bias=float((np.exp(-np.abs(pred_tm-gfed_tm)/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    crmse=np.sqrt((((pred-pred_tm[None,:,:])-(obs-gfed_tm[None,:,:]))**2).mean(axis=0))
    rmse=float((np.exp(-crmse/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pred_cyc=pred.reshape(16,12,180,360).mean(axis=0)
    shift=np.argmax(pred_cyc,axis=0).astype(np.float32)-gfed_peak_month
    shift=np.where(shift>6,shift-12,shift); shift=np.where(shift<-6,shift+12,shift)
    seas=float((((1+np.cos(np.abs(shift)/12*2*np.pi))*0.5)*mass_w_burn).sum()/(mass_w_burn.sum()+1e-12))
    obs_flat=gfed_tm[land_mask]; pred_flat=pred_tm[land_mask]; pw=w2_burn[land_mask]
    ow=(obs_flat*pw).sum()/pw.sum(); pm=(pred_flat*pw).sum()/pw.sum()
    oa=obs_flat-ow; pa=pred_flat-pm
    std0=max(float(np.sqrt(((oa**2)*pw).sum()/pw.sum())),1e-12); std=max(float(np.sqrt(((pa**2)*pw).sum()/pw.sum())),1e-12)
    rho=float((pa*oa*pw).sum()/(np.sqrt(((pa**2)*pw).sum()*((oa**2)*pw).sum())+1e-12))
    sigma=std/std0; spatial=float(2*(1+rho)/((sigma+1/max(sigma,1e-12))**2))
    overall=float((2*bias+2*rmse+seas+spatial)/6)
    return overall,{"bias":bias,"rmse":rmse,"seasonal":seas,"spatial":spatial,"overall":overall}

def objective(trial):
    e={
        "family":"curing_gated_lag_fuel",
        "gpp_lag_window":trial.suggest_categorical("gpp_lag_window",WINDOWS),
        "lag_alpha":trial.suggest_float("lag_alpha",0.0,1.0),
        "D_cure_k":trial.suggest_float("D_cure_k",1e-4,1e-1,log=True),
        "D_cure_c":trial.suggest_float("D_cure_c",10.0,2000.0,log=True),
        "P_cure_half":trial.suggest_float("P_cure_half",0.1,50.0,log=True),
        "P_cure_pow":trial.suggest_float("P_cure_pow",0.5,5.0),
    }
    pred=predict(e); overall,br=score(pred)
    for k,v in br.items(): trial.set_user_attr(k,v)
    trial.set_user_attr("extra",e)
    return overall

def main():
    base={"family":"curing_gated_lag_fuel","gpp_lag_window":1,"lag_alpha":0.0,"D_cure_k":0.01,"D_cure_c":100,"P_cure_half":5,"P_cure_pow":2}
    _,base_br=score(predict(base)); print('[baseline proxy]',base_br)
    sampler=optuna.samplers.TPESampler(seed=SEED,multivariate=True,group=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    study.enqueue_trial({"gpp_lag_window":12,"lag_alpha":1.0,"D_cure_k":0.1,"D_cure_c":10.0,"P_cure_half":50.0,"P_cure_pow":0.5}) # near uniform lag
    study.enqueue_trial({"gpp_lag_window":12,"lag_alpha":1.0,"D_cure_k":0.01,"D_cure_c":100.0,"P_cure_half":5.0,"P_cure_pow":2.0})
    t0=time.time(); last=t0
    def cb(st,tr):
        nonlocal last
        if time.time()-last>30:
            print(f"[progress] {len(st.trials)}/{N_TRIALS} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f} min")
            last=time.time()
    study.optimize(objective,n_trials=N_TRIALS,callbacks=[cb])
    best=study.best_trial
    result={"name":"CURING-LAG-v1","n_trials":len(study.trials),"seed":SEED,"baseline_proxy":base_br,"best_proxy_scores":{k:best.user_attrs[k] for k in ["bias","rmse","seasonal","spatial","overall"]},"best_extra":best.user_attrs['extra'],"best_params":best.params,"runtime_min":round((time.time()-t0)/60,3),"physical_hypothesis":"Antecedent GPP acts as burnable cured fuel only under current dry-season indicators from Dbar and P_month.","constraint_note":"Formula uses only allowed model inputs; no region/coordinate/cell routing."}
    out=OUTDIR/f"curing_lag_search_{N_TRIALS}_trials.json"; out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2)); print('[write]',out)
if __name__=='__main__': main()
