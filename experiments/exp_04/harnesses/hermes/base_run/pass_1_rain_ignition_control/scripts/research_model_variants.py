#!/usr/bin/env python3
"""Constrained Model-C variant search for ED fire autoresearch.

All candidates are one global formula using only the fixed workspace inputs:
dbar, annual precip, monthly precip, monthly GPP, monthly air temperature.

Usage:
  N_TRIALS=500 FAMILY=wet_gpp_supp MODEL_NAME=ED-C1 python scripts/research_model_variants.py

Writes:
  models/research/<MODEL_NAME>/params.json
  ilamb/MODELS/<MODEL_NAME>/burntArea.nc
"""
from __future__ import annotations
import json, os, time, shutil
from pathlib import Path
import cftime, h5py, numpy as np, optuna, xarray as xr

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import load_drivers, load_gfed_1deg, add_cf_bounds, uncoarsen, sig, supp, hump

REPO=Path(__file__).resolve().parents[1]
YEARS=list(range(2001,2017)); N_MONTHS=192
FIRE_MAX_RATE=float(os.environ.get('FIRE_MAX_RATE',5.0))
FAMILY=os.environ.get('FAMILY','wet_gpp_supp')
MODEL_NAME=os.environ.get('MODEL_NAME',f'ED-{FAMILY}')
N_TRIALS=int(os.environ.get('N_TRIALS','500'))
SEED=int(os.environ.get('SEED','42'))

BASE=json.load(open(REPO/'models/C/params.json'))['params']
DR=load_drivers(); OBS=load_gfed_1deg()
lat_1=np.arange(-89.5,90.0,1.0).astype(np.float32)
cos_lat=np.cos(np.deg2rad(lat_1)).astype(np.float64)
w2=np.broadcast_to(cos_lat[:,None],(180,360)).astype(np.float64)
w3=np.broadcast_to(cos_lat[None,:,None],(N_MONTHS,180,360)).astype(np.float64)
land=(OBS>0).any(axis=0)
w2_land=w2*land; w3_land=w3*land[None,:,:]
gfed_tm=OBS.mean(axis=0).astype(np.float64)
gfed_std=OBS.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc=OBS.reshape(16,12,180,360).mean(axis=0)
gfed_peak=np.argmax(gfed_cyc,axis=0).astype(np.float32)
mass_w=(w2*gfed_tm).astype(np.float64); mass_w_burn=mass_w*land

REGIONS={
 'bona': lambda lat: lat>=50,
 'tena': lambda lat: (lat>=30)&(lat<50),
 'tropics': lambda lat: (lat>-23.5)&(lat<23.5),
 'sh': lambda lat: lat<=-23.5,
}
reg_masks={k: np.broadcast_to(f(lat_1)[:,None],(180,360)) & land for k,f in REGIONS.items()}

# baseline prediction scores for diagnostics
def base_rate(p):
    onset=sig(DR['dbar'],p['k1'],p['D_low'])
    suppress=supp(DR['dbar'],p['k2'],p['D_high'])
    p_floor=DR['p_ann']/(DR['p_ann']+p['P_half']+1e-12)
    p_damp=1/(1+DR['p_month']/(p['pre_dampen_half']+1e-12))
    gpp_mod=hump(p['gpp_af']*DR['gpp_monthly'],p['gpp_b'],p['gpp_d'])
    ign_mod=sig(DR['t_air'],p['ign_k'],p['ign_c'])
    prod=onset*suppress*p_floor*p_damp*gpp_mod*ign_mod
    return np.power(np.clip(prod,0,None),p['fire_exp']).astype(np.float32)

def apply_family(rate,p):
    # All terms are bounded global mechanisms, not region routing.
    if FAMILY=='wet_gpp_supp':
        # Missing mechanism: persistently wet/high-productivity fuels are less flammable
        # because live fuel moisture/rainforest humidity/cropland management counteract fuel amount.
        x=p['gpp_af']*DR['gpp_monthly']
        wet=DR['p_ann']/(DR['p_ann']+p['wetP_half']+1e-12)
        hi=1/(1+np.exp(np.clip(-p['wetgpp_k']*(x-p['wetgpp_c']),-50,50)))
        gate=1-p['wetgpp_amp']*wet*hi
        return rate*np.clip(gate,0.02,1.0)
    if FAMILY=='annual_p_hump':
        # Missing mechanism: annual precipitation is not only a fuel floor; very wet climates suppress fire.
        hi_supp=1/(1+(DR['p_ann']/(p['P_wet_supp']+1e-12))**p['P_wet_pow'])
        floor=(DR['p_ann']/(DR['p_ann']+p['P_half2']+1e-12))**p['P_floor_pow']
        # replace old monotone floor approximately by multiplying ratio of new/old floor
        old=DR['p_ann']/(DR['p_ann']+BASE['P_half']+1e-12)
        return rate*np.clip(floor*hi_supp/(old+1e-6),0.01,5.0)
    if FAMILY=='rain_temp_shift':
        # Missing mechanism: rain/high humidity raises the effective ignition temperature threshold.
        old=sig(DR['t_air'],BASE['ign_k'],BASE['ign_c'])
        c=p['ign_c2'] + p['rain_shift']*np.log1p(DR['p_month'])
        new=sig(DR['t_air'],p['ign_k2'],c)
        return rate*np.clip(new/(old+1e-6),0.01,5.0)
    if FAMILY=='dry_season_gate':
        # Missing mechanism: fire requires a month dry relative to local annual water supply.
        dry_anom=np.maximum(DR['p_ann']/12.0 - DR['p_month'],0.0)
        gate=1-np.exp(-dry_anom/(p['dryanom_half']+1e-12))
        return rate*np.clip((1-p['dry_amp'])+p['dry_amp']*gate,0.02,1.0)
    if FAMILY=='base_refit':
        return rate
    raise ValueError(FAMILY)

def ed_transform(rate):
    return ((1-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12).astype(np.float32)

def predict(p):
    r=base_rate(p)*land[None,:,:]
    r=apply_family(r,p)*land[None,:,:]
    return ed_transform(r)

def score_region(pred, mask=None):
    if mask is None: mask=land
    pred_tm=pred.mean(axis=0)
    mw=mass_w*mask; mw_b=mass_w_burn*mask
    if mw.sum()<=0: return dict(overall=0,bias=0,rmse=0,seas=0,spatial=0)
    bias=np.exp(-np.abs(pred_tm-gfed_tm)/gfed_std)
    bias=float((bias*mw).sum()/(mw.sum()+1e-12))
    pa=pred-pred_tm[None,:,:]; oa=OBS-gfed_tm[None,:,:]
    rmse=np.exp(-np.sqrt(((pa-oa)**2).mean(axis=0))/gfed_std)
    rmse=float((rmse*mw).sum()/(mw.sum()+1e-12))
    pred_cyc=pred.reshape(16,12,180,360).mean(axis=0)
    shift=np.argmax(pred_cyc,axis=0).astype(np.float32)-gfed_peak
    shift=np.where(shift>6,shift-12,shift); shift=np.where(shift<-6,shift+12,shift)
    seas_cell=(1+np.cos(np.abs(shift)/12*2*np.pi))*0.5
    seas=float((seas_cell*mw_b).sum()/(mw_b.sum()+1e-12))
    obs_flat=gfed_tm[mask]; pred_flat=pred_tm[mask]; ww=w2_land[mask]
    if ww.sum()>0 and len(obs_flat)>2:
        ow=(obs_flat*ww).sum()/ww.sum(); pw=(pred_flat*ww).sum()/ww.sum()
        oo=obs_flat-ow; pp=pred_flat-pw
        std0=max(float(np.sqrt((oo**2*ww).sum()/ww.sum())),1e-12)
        std=max(float(np.sqrt((pp**2*ww).sum()/ww.sum())),1e-12)
        rho=float((oo*pp*ww).sum()/(np.sqrt((oo**2*ww).sum()*(pp**2*ww).sum())+1e-12))
        sigma=std/std0; spatial=2*(1+rho)/((sigma+1/max(sigma,1e-12))**2)
    else: spatial=0.0
    overall=(2*bias+2*rmse+seas+spatial)/6
    return dict(overall=float(overall),bias=bias,rmse=rmse,seas=seas,spatial=float(spatial))

def score(pred):
    g=score_region(pred)
    regs={k:score_region(pred,m) for k,m in reg_masks.items()}
    # objective: primarily global, with a small floor term to avoid sacrificing weak macro-regions.
    reg_mean=float(np.mean([v['overall'] for v in regs.values()]))
    reg_min=float(np.min([v['overall'] for v in regs.values()]))
    obj=0.78*g['overall']+0.17*reg_mean+0.05*reg_min
    return obj,g,regs

BASE_RANGES={
 'k1':(1e-5,1e-1),'D_low':(1,1e4),'k2':(1e-5,1e-1),'D_high':(10,1e5),
 'fire_exp':(0.35,10),'P_half':(0.1,1e4),'pre_dampen_half':(1e-2,1e3),
 'gpp_af':(1e-3,1e2),'gpp_b':(1e-6,1e1),'gpp_d':(1e-2,1e3),'ign_k':(1e-3,1e1),'ign_c':(0.1,1e3)
}
EXTRA={
 'wet_gpp_supp': {'wetP_half':(10,5000),'wetgpp_k':(1e-3,1e3),'wetgpp_c':(1e-5,100),'wetgpp_amp':(0.0,0.98)},
 'annual_p_hump': {'P_wet_supp':(10,10000),'P_wet_pow':(0.05,5),'P_half2':(0.1,1e4),'P_floor_pow':(0.05,5)},
 'rain_temp_shift': {'ign_k2':(1e-3,1e1),'ign_c2':(0.1,60),'rain_shift':(0.0,20)},
 'dry_season_gate': {'dryanom_half':(0.1,500),'dry_amp':(0.0,0.98)},
 'base_refit': {}
}

def suggest(trial):
    p={}
    # allow full retune for serious families, but enqueue baseline first.
    for k,(lo,hi) in BASE_RANGES.items(): p[k]=trial.suggest_float(k,lo,hi,log=True)
    for k,(lo,hi) in EXTRA[FAMILY].items():
        log=(lo>0 and hi/lo>100)
        p[k]=trial.suggest_float(k,lo,hi,log=log)
    return p

def main():
    print(f'[setup] family={FAMILY} model={MODEL_NAME} trials={N_TRIALS} cap={FIRE_MAX_RATE}')
    print(f'[setup] land cells={land.sum()}')
    bpred=predict({**BASE, **{k:(v[0] if k.endswith("amp") else np.sqrt(v[0]*v[1]) if v[0]>0 else v[1]/2) for k,v in EXTRA.get(FAMILY,{}).items()}})
    bscore,bg,br=score(bpred)
    print('[baseline internal]', bscore, bg)
    sampler=optuna.samplers.TPESampler(seed=SEED, multivariate=True)
    study=optuna.create_study(direction='maximize', sampler=sampler)
    enq=dict(BASE)
    for k,v in EXTRA[FAMILY].items():
        if k.endswith('amp'): enq[k]=0.0
        else: enq[k]=float(np.sqrt(v[0]*v[1]) if v[0]>0 else v[1]/2)
    study.enqueue_trial(enq)
    t0=time.time()
    def objective(trial):
        p=suggest(trial); pred=predict(p); obj,_,_=score(pred); return obj
    study.optimize(objective,n_trials=N_TRIALS,show_progress_bar=False)
    best=study.best_params; pred=predict(best); obj,g,regs=score(pred)
    print('[best]', obj, g); print('[regions]', regs); print('[params]', best)
    outdir=REPO/'models/research'/MODEL_NAME; outdir.mkdir(parents=True,exist_ok=True)
    meta={'model':MODEL_NAME,'family':FAMILY,'n_trials':len(study.trials),'objective':'0.78*global_weighted_overall+0.17*macroregion_mean+0.05*macroregion_min; scorer approximates ILAMB','internal_objective':obj,'internal_global':g,'internal_macroregions':regs,'params':best,'elapsed_min':(time.time()-t0)/60}
    (outdir/'params.json').write_text(json.dumps(meta,indent=2))
    pred_hd=uncoarsen(np.where(land[None,:,:],pred,np.nan).astype(np.float32))
    times=[cftime.DatetimeNoLeap(y,m,15) for y in YEARS for m in range(1,13)]
    ds=xr.Dataset({'burntArea':(('time','lat','lon'),pred_hd,{'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})},coords={'time':('time',times),'lat':('lat',np.arange(-89.75,90.0,0.5)),'lon':('lon',np.arange(-179.75,180.0,0.5))},attrs={'title':MODEL_NAME,'formula_family':FAMILY,'Conventions':'CF-1.7','transform':f'monthly_frac=(1-exp(-min(rate,{FIRE_MAX_RATE})))/12'})
    ds=add_cf_bounds(ds)
    mdir=REPO/'ilamb/MODELS'/MODEL_NAME; mdir.mkdir(parents=True,exist_ok=True)
    tmp=mdir/'burntArea.nc.tmp'
    enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20},'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'},'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    ds.to_netcdf(tmp,encoding=enc,format='NETCDF4_CLASSIC'); os.replace(tmp,mdir/'burntArea.nc')
    print('[write]',outdir/'params.json'); print('[write]',mdir/'burntArea.nc')
if __name__=='__main__': main()
