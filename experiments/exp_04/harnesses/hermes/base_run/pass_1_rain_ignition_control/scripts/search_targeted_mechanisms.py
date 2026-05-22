#!/usr/bin/env python3
"""Targeted constrained searches around original Model C.

These searches keep the Model C core fixed and tune only small, interpretable
mechanism gates plus optionally fire_exp. This is meant as an ablation/variant
counterpoint to full refits in research_model_variants.py.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
import cftime, numpy as np, optuna, xarray as xr

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import add_cf_bounds, uncoarsen
import research_model_variants as rmv

REPO=Path(__file__).resolve().parents[1]
FAMILY=os.environ.get('FAMILY','annual_wet_amp')
MODEL_NAME=os.environ.get('MODEL_NAME',f'ED-C2-{FAMILY}')
N_TRIALS=int(os.environ.get('N_TRIALS','1000'))
SEED=int(os.environ.get('SEED','202'))
BASE=rmv.BASE
BASE_RATE=rmv.base_rate(BASE)*rmv.land[None,:,:]


def ed_transform(rate, fire_exp_scale=1.0):
    # optional power on annual rate before ED transform; multiplicative gates otherwise keep units.
    r=np.power(np.clip(rate,0,None), fire_exp_scale).astype(np.float32)
    return rmv.ed_transform(r*rmv.land[None,:,:])


def predict(p):
    r=BASE_RATE.copy()
    if FAMILY in ('annual_wet_amp','combined_wet_rain'):
        # Annual precipitation high-end suppression: low P_ann remains fuel-limited by Model C;
        # high P_ann reduces spread via humidity/live fuel moisture/rainforest persistence.
        wet_supp=1.0/(1.0+(rmv.DR['p_ann']/(p['P_wet']+1e-12))**p['P_pow'])
        gate=(1.0-p['P_amp'])+p['P_amp']*wet_supp
        r*=np.clip(gate,0.02,1.0)
    if FAMILY in ('wet_gpp_amp','combined_wet_rain'):
        # Productive-wet suppression: very high monthly GPP under wet annual climate can represent
        # live moist fuels/closed canopy rather than cured fine fuel.
        x=BASE['gpp_af']*rmv.DR['gpp_monthly']
        wet=rmv.DR['p_ann']/(rmv.DR['p_ann']+p['WG_Phalf']+1e-12)
        hi=1.0/(1.0+np.exp(np.clip(-p['WG_k']*(x-p['WG_c']),-50,50)))
        gate=1.0-p['WG_amp']*wet*hi
        r*=np.clip(gate,0.02,1.0)
    if FAMILY in ('rain_ignition_shift','combined_wet_rain'):
        # Rain/humidity raises effective ignition threshold. Replace Model C ignition term by a
        # monthly precip-conditioned version, holding other Model C mechanisms fixed.
        old=rmv.sig(rmv.DR['t_air'],BASE['ign_k'],BASE['ign_c'])
        c=BASE['ign_c'] + p['rain_shift']*np.log1p(rmv.DR['p_month'])
        new=rmv.sig(rmv.DR['t_air'],p['ign_k'],c)
        r*=np.clip(new/(old+1e-6),0.02,5.0)
    return ed_transform(r, p.get('rate_power',1.0))


def suggest(trial):
    p={}
    if FAMILY in ('annual_wet_amp','combined_wet_rain'):
        p['P_amp']=trial.suggest_float('P_amp',0.0,0.9)
        p['P_wet']=trial.suggest_float('P_wet',300,6000,log=True)
        p['P_pow']=trial.suggest_float('P_pow',0.2,6.0)
    if FAMILY in ('wet_gpp_amp','combined_wet_rain'):
        p['WG_amp']=trial.suggest_float('WG_amp',0.0,0.9)
        p['WG_Phalf']=trial.suggest_float('WG_Phalf',100,5000,log=True)
        p['WG_k']=trial.suggest_float('WG_k',0.01,100,log=True)
        p['WG_c']=trial.suggest_float('WG_c',1e-4,10,log=True)
    if FAMILY in ('rain_ignition_shift','combined_wet_rain'):
        p['rain_shift']=trial.suggest_float('rain_shift',0.0,10.0)
        p['ign_k']=trial.suggest_float('ign_k',0.05,3.0,log=True)
    p['rate_power']=trial.suggest_float('rate_power',0.7,1.3)
    return p


def main():
    print(f'[setup] targeted family={FAMILY} model={MODEL_NAME} trials={N_TRIALS}')
    base_pred=rmv.ed_transform(BASE_RATE)
    bobj,bg,br=rmv.score(base_pred)
    print('[baseline]',bobj,bg,br)
    sampler=optuna.samplers.TPESampler(seed=SEED,multivariate=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    # Enqueue exact baseline/no-op where possible.
    enq={'rate_power':1.0}
    if FAMILY in ('annual_wet_amp','combined_wet_rain'):
        enq.update(P_amp=0.0,P_wet=1500.0,P_pow=2.0)
    if FAMILY in ('wet_gpp_amp','combined_wet_rain'):
        enq.update(WG_amp=0.0,WG_Phalf=1000.0,WG_k=1.0,WG_c=0.03)
    if FAMILY in ('rain_ignition_shift','combined_wet_rain'):
        enq.update(rain_shift=0.0,ign_k=BASE['ign_k'])
    study.enqueue_trial(enq)
    t0=time.time()
    def obj(trial):
        p=suggest(trial); pred=predict(p); objective,g,regs=rmv.score(pred)
        # More regional-balanced than C1 but still anchored to global performance.
        regmean=float(np.mean([v['overall'] for v in regs.values()]))
        regmin=float(np.min([v['overall'] for v in regs.values()]))
        return 0.70*g['overall']+0.22*regmean+0.08*regmin
    study.optimize(obj,n_trials=N_TRIALS,show_progress_bar=False)
    p=study.best_params; pred=predict(p); objective,g,regs=rmv.score(pred)
    meta={'model':MODEL_NAME,'family':FAMILY,'n_trials':len(study.trials),'objective':'targeted fixed-Model-C mechanism; score=0.70 global + 0.22 macroregion mean + 0.08 macroregion min using ILAMB-proxy scorer','internal_objective':float(study.best_value),'internal_global':g,'internal_macroregions':regs,'params':p,'elapsed_min':(time.time()-t0)/60}
    outdir=REPO/'models/research'/MODEL_NAME; outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'params.json').write_text(json.dumps(meta,indent=2))
    pred_hd=uncoarsen(np.where(rmv.land[None,:,:],pred,np.nan).astype(np.float32))
    times=[cftime.DatetimeNoLeap(y,m,15) for y in rmv.YEARS for m in range(1,13)]
    ds=xr.Dataset({'burntArea':(('time','lat','lon'),pred_hd,{'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})},coords={'time':('time',times),'lat':('lat',np.arange(-89.75,90.0,0.5)),'lon':('lon',np.arange(-179.75,180.0,0.5))},attrs={'title':MODEL_NAME,'formula_family':FAMILY,'Conventions':'CF-1.7','transform':'monthly_frac=(1-exp(-min(rate,5.0)))/12'})
    ds=add_cf_bounds(ds)
    mdir=REPO/'ilamb/MODELS'/MODEL_NAME; mdir.mkdir(parents=True,exist_ok=True)
    enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20},'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'},'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    tmp=mdir/'burntArea.nc.tmp'; ds.to_netcdf(tmp,encoding=enc,format='NETCDF4_CLASSIC'); os.replace(tmp,mdir/'burntArea.nc')
    print('[best]',study.best_value,g,regs,p)
    print('[write]',outdir/'params.json'); print('[write]',mdir/'burntArea.nc')

if __name__=='__main__': main()
