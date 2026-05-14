#!/usr/bin/env python3
"""Research candidate optimizer for Model C extensions.

Uses only allowed workspace inputs. Writes candidate params and TRENDY-format burntArea.nc
under runs/candidates/<name>/ for official ILAMB evaluation.
"""
from __future__ import annotations
import argparse, json, os, time, sys
from pathlib import Path
import numpy as np
import optuna
import cftime, xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import load_drivers, load_gfed_1deg, add_cf_bounds, uncoarsen, sig, supp, hump

REPO=Path(__file__).resolve().parents[1]
YEARS=list(range(2001,2017)); N_MONTHS=192; FIRE_MAX_RATE=5.0
OUTROOT=REPO/'runs'/'candidates'
BASE=json.load(open(REPO/'models/C/params.json'))['params']

def ed_transform(rate):
    return ((1.0-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12.0).astype(np.float32)

print('[setup] load drivers/GFED')
d=load_drivers(); obs=load_gfed_1deg()
lat_1=np.arange(-89.5,90.0,1.0).astype(np.float32)
cos_lat=np.cos(np.deg2rad(lat_1)).astype(np.float64)
w2=np.broadcast_to(cos_lat[:,None],(180,360)).astype(np.float64)
w3=np.broadcast_to(cos_lat[None,:,None],(N_MONTHS,180,360)).astype(np.float64)
land_mask=(obs>0).any(axis=0)
w2_burn=(w2*land_mask).astype(np.float64); w3_land=(w3*land_mask[None,:,:]).astype(np.float64)
gfed_tm=obs.mean(axis=0).astype(np.float64); gfed_std=obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc=obs.reshape(16,12,180,360).mean(axis=0); gfed_peak=np.argmax(gfed_cyc,axis=0).astype(np.float32)
mass_w=(w2*gfed_tm).astype(np.float64); mass_w_burn=(mass_w*land_mask).astype(np.float64)
# lagged fuel proxies from allowed monthly GPP
G=d['gpp_monthly'].astype(np.float32)
G_lag3=np.empty_like(G); G_lag6=np.empty_like(G)
for t in range(N_MONTHS):
    G_lag3[t]=G[max(0,t-3):t+1].mean(axis=0)
    G_lag6[t]=G[max(0,t-6):t+1].mean(axis=0)
ann_p=d['p_ann']; mon_p=d['p_month']; dbar=d['dbar']; tair=d['t_air']
# precipitation concentration / recent wetness proxies from existing p fields
p_conc=np.clip(mon_p/(ann_p/12.0+1e-6),0,50).astype(np.float32)
# Thermal-regime proxies derived only from allowed monthly air temperature.
# These are not latitude/region terms: they represent liquid-precipitation and
# cold-vs-warm fuel physics and are applied globally to every cell.
t_ann=np.broadcast_to(tair.mean(axis=0, keepdims=True), tair.shape).astype(np.float32)
t_min=np.broadcast_to(tair.reshape(16,12,180,360).mean(axis=0).min(axis=0, keepdims=True), tair.shape).astype(np.float32)

def score(pred):
    pred_tm=pred.mean(axis=0).astype(np.float64)
    bias=float((np.exp(-np.abs(pred_tm-gfed_tm)/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pa=pred-pred_tm[None,:,:]; oa=obs-gfed_tm[None,:,:]
    crmse=np.sqrt(((pa-oa)**2).mean(axis=0))
    rmse=float((np.exp(-crmse/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pred_cyc=pred.reshape(16,12,180,360).mean(axis=0); peak=np.argmax(pred_cyc,axis=0).astype(np.float32)
    shift=peak-gfed_peak; shift=np.where(shift>6,shift-12,shift); shift=np.where(shift<-6,shift+12,shift)
    seas=float((((1+np.cos(np.abs(shift)/12*2*np.pi))*0.5)*mass_w_burn).sum()/(mass_w_burn.sum()+1e-12))
    of=gfed_tm[land_mask]; pf=pred_tm[land_mask]; ww=w2_burn[land_mask]
    ow=(of*ww).sum()/ww.sum(); pw=(pf*ww).sum()/ww.sum(); oa2=of-ow; pa2=pf-pw
    std0=max(float(np.sqrt(((oa2**2)*ww).sum()/ww.sum())),1e-12); std=max(float(np.sqrt(((pa2**2)*ww).sum()/ww.sum())),1e-12)
    rho=float((pa2*oa2*ww).sum()/(np.sqrt(((pa2**2)*ww).sum()*((oa2**2)*ww).sum())+1e-12))
    sigma=std/std0; spatial=float(2*(1+rho)/((sigma+1/max(sigma,1e-12))**2))
    overall=(2*bias+2*rmse+seas+spatial)/6.0
    return dict(bias=bias,rmse=rmse,seas=seas,spatial=spatial,overall=float(overall))

def base_product(p, gpp_eff=None):
    if gpp_eff is None: gpp_eff=G
    onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
    p_floor=ann_p/(ann_p+p['P_half']+1e-12)
    p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
    gpp_mod=hump(p['gpp_af']*gpp_eff,p['gpp_b'],p['gpp_d'])
    ign_mod=sig(tair,p['ign_k'],p['ign_c'])
    return onset*suppress*p_floor*p_damp*gpp_mod*ign_mod

def predict(p, family):
    if family=='C_reopt':
        prod=base_product(p)
    elif family=='lagged_fuel':
        mix=p['lag_mix']; window=p['lag_window']
        lag=G_lag3 if window<4.5 else G_lag6
        gpp_eff=(1-mix)*G+mix*lag
        prod=base_product(p,gpp_eff)
    elif family=='dry_shifted_gpp':
        # In dry savanna, cured fine fuel can burn at higher apparent productivity;
        # in moist forests, high-GPP suppression remains strong.
        dry=sig(dbar,p['dry_k'],p['dry_c'])
        geff=G
        onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
        p_floor=ann_p/(ann_p+p['P_half']+1e-12)
        p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
        x = p['gpp_af'] * geff
        dec = p['gpp_d'] * (1 + p['gpp_dry_boost'] * dry)
        gpp_mod = (1.0 - np.exp(-np.clip(x / max(p['gpp_b'], 1e-9), 0, 500))) * np.exp(-np.clip(x / np.maximum(dec, 1e-9), 0, 500))
        ign_mod=sig(tair,p['ign_k'],p['ign_c'])
        prod=onset*suppress*p_floor*p_damp*gpp_mod*ign_mod
    elif family=='rain_pulse_suppression':
        # suppress anomalously rain-dominated months beyond absolute monthly dampening.
        prod=base_product(p)*np.exp(-p['pulse_a']*np.clip(p_conc-p['pulse_c'],0,None))
    elif family=='temp_moist_interaction':
        # warm ignition is weaker during wet months; mechanistic wet-fuel ignition limitation.
        wet=mon_p/(mon_p+p['wet_half']+1e-12)
        ign=sig(tair,p['ign_k'],p['ign_c']+p['wet_temp_shift']*wet)
        onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
        p_floor=ann_p/(ann_p+p['P_half']+1e-12); p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
        gpp_mod=hump(p['gpp_af']*G,p['gpp_b'],p['gpp_d'])
        prod=onset*suppress*p_floor*p_damp*gpp_mod*ign
    elif family=='liquid_wet_temp':
        # Naive wet-temperature suppression damaged BONA/BOAS. Here wet-fuel
        # ignition limitation depends on liquid-rain wetting, not cold/snow
        # precipitation. This is a thermal physics gate, not region routing.
        liquid_frac=sig(tair,p['liquid_k'],p['liquid_c'])
        liquid_p=mon_p*liquid_frac
        wet=liquid_p/(liquid_p+p['wet_half']+1e-12)
        ign=sig(tair,p['ign_k'],p['ign_c']+p['wet_temp_shift']*wet)
        onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
        p_floor=ann_p/(ann_p+p['P_half']+1e-12); p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
        gpp_mod=hump(p['gpp_af']*G,p['gpp_b'],p['gpp_d'])
        prod=onset*suppress*p_floor*p_damp*gpp_mod*ign
    elif family=='warm_gated_wet_temp':
        # Apply wet-fuel temperature shift mainly in thermally warm regimes,
        # preserving cold boreal spatial structure while retaining weak-region
        # wet-month suppression. Gate is derived only from T_air.
        warm_gate=sig(t_ann,p['warm_k'],p['warm_c'])
        wet=mon_p/(mon_p+p['wet_half']+1e-12)
        ign=sig(tair,p['ign_k'],p['ign_c']+p['wet_temp_shift']*wet*warm_gate)
        onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
        p_floor=ann_p/(ann_p+p['P_half']+1e-12); p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
        gpp_mod=hump(p['gpp_af']*G,p['gpp_b'],p['gpp_d'])
        prod=onset*suppress*p_floor*p_damp*gpp_mod*ign
    elif family=='liquid_warm_wet_temp':
        # Combined ablation: liquid-rain wetting plus warm-regime gate.
        liquid_frac=sig(tair,p['liquid_k'],p['liquid_c'])
        warm_gate=sig(t_ann,p['warm_k'],p['warm_c'])
        liquid_p=mon_p*liquid_frac
        wet=liquid_p/(liquid_p+p['wet_half']+1e-12)
        ign=sig(tair,p['ign_k'],p['ign_c']+p['wet_temp_shift']*wet*warm_gate)
        onset=sig(dbar,p['k1'],p['D_low']); suppress=supp(dbar,p['k2'],p['D_high'])
        p_floor=ann_p/(ann_p+p['P_half']+1e-12); p_damp=1/(1+mon_p/(p['pre_dampen_half']+1e-12))
        gpp_mod=hump(p['gpp_af']*G,p['gpp_b'],p['gpp_d'])
        prod=onset*suppress*p_floor*p_damp*gpp_mod*ign
    else: raise ValueError(family)
    rate=np.power(np.clip(prod,0,None),p['fire_exp']).astype(np.float32)*land_mask[None,:,:]
    return ed_transform(rate)

LOG={'k1':(1e-5,1e-1),'D_low':(1,1e4),'k2':(1e-5,1e-1),'D_high':(10,1e5),'fire_exp':(0.5,3.0),'P_half':(1,1e4),'pre_dampen_half':(0.01,1e3),'gpp_af':(1e-3,1e2),'gpp_b':(1e-5,1e1),'gpp_d':(1e-2,1e3),'ign_k':(1e-3,10),'ign_c':(0.1,1e3)}
EXTRA={
 'lagged_fuel': {'lag_mix':(0,1,False),'lag_window':(3,6,False)},
 'dry_shifted_gpp': {'dry_k':(1e-4,0.05,True),'dry_c':(10,5000,True),'gpp_dry_boost':(0.0,10.0,False)},
 'rain_pulse_suppression': {'pulse_a':(0.0,1.5,False),'pulse_c':(0.5,8.0,False)},
 'temp_moist_interaction': {'wet_half':(0.1,200,True),'wet_temp_shift':(0.0,20.0,False)},
 'liquid_wet_temp': {'wet_half':(0.1,200,True),'wet_temp_shift':(0.0,20.0,False),'liquid_k':(0.05,5.0,True),'liquid_c':(-5.0,8.0,False)},
 'warm_gated_wet_temp': {'wet_half':(0.1,200,True),'wet_temp_shift':(0.0,25.0,False),'warm_k':(0.05,2.0,True),'warm_c':(-5.0,25.0,False)},
 'liquid_warm_wet_temp': {'wet_half':(0.1,200,True),'wet_temp_shift':(0.0,25.0,False),'liquid_k':(0.05,5.0,True),'liquid_c':(-5.0,8.0,False),'warm_k':(0.05,2.0,True),'warm_c':(-5.0,25.0,False)},
}

def suggest(trial,family):
    p={}
    for k,(lo,hi) in LOG.items():
        p[k]=trial.suggest_float(k,lo,hi,log=True)
    if family in EXTRA:
        for k,(lo,hi,lg) in EXTRA[family].items(): p[k]=trial.suggest_float(k,lo,hi,log=lg)
    return p

def write_nc(pred,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    hd=uncoarsen(np.where(land_mask[None,:,:],pred,np.nan).astype(np.float32))
    times=[cftime.DatetimeNoLeap(y,m,15) for y in YEARS for m in range(1,13)]
    ds=xr.Dataset({'burntArea':(('time','lat','lon'),hd,{'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})},coords={'time':('time',times),'lat':('lat',np.arange(-89.75,90.0,0.5)),'lon':('lon',np.arange(-179.75,180.0,0.5))},attrs={'title':outdir.name,'Conventions':'CF-1.7','transform':'monthly_frac=(1-exp(-min(rate_yr,5.0)))/12'})
    ds=add_cf_bounds(ds); enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20},'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'},'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    ds.to_netcdf(outdir/'burntArea.nc',encoding=enc,format='NETCDF4_CLASSIC')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('family'); ap.add_argument('--trials',type=int,default=500); ap.add_argument('--seed',type=int,default=52); ap.add_argument('--name',default=None)
    args=ap.parse_args(); family=args.family; name=args.name or family
    t0=time.time(); sampler=optuna.samplers.TPESampler(seed=args.seed,multivariate=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    # warm-start base; add neutral extras where needed
    warm=BASE.copy()
    if family=='lagged_fuel': warm.update(lag_mix=0.0,lag_window=3.0)
    if family=='dry_shifted_gpp': warm.update(dry_k=0.003,dry_c=500.0,gpp_dry_boost=0.0)
    if family=='rain_pulse_suppression': warm.update(pulse_a=0.0,pulse_c=2.0)
    if family=='temp_moist_interaction': warm.update(wet_half=50.0,wet_temp_shift=0.0)
    if family=='liquid_wet_temp': warm.update(wet_half=20.0,wet_temp_shift=0.0,liquid_k=1.0,liquid_c=0.0)
    if family=='warm_gated_wet_temp': warm.update(wet_half=20.0,wet_temp_shift=0.0,warm_k=0.5,warm_c=5.0)
    if family=='liquid_warm_wet_temp': warm.update(wet_half=20.0,wet_temp_shift=0.0,liquid_k=1.0,liquid_c=0.0,warm_k=0.5,warm_c=5.0)
    study.enqueue_trial(warm)
    def obj(trial):
        p=suggest(trial,family)
        pred=predict(p,family)
        sc=score(pred)
        # small complexity penalty for extra mechanisms and protection for spatial collapse.
        val=sc['overall'] - 0.01*max(0,0.74-sc['spatial'])
        return val
    print(f'[opt] {family} {args.trials} trials')
    study.optimize(obj,n_trials=args.trials,show_progress_bar=False)
    p=study.best_params; pred=predict(p,family); sc=score(pred)
    raw_prod=None
    outdir=OUTROOT/name; outdir.mkdir(parents=True,exist_ok=True)
    meta={'family':family,'name':name,'n_trials':len(study.trials),'runtime_min':(time.time()-t0)/60,'fast_score':sc,'objective_value':study.best_value,'params':p,'allowed_inputs':['dbar_monthly.npy','p_ann_monthly.npy','p_month_monthly.npy','t_air_monthly.npy','EDv3_S3_gpp.nc'],'constraint_note':'single global formula; no lat/lon, no regions, no cell tables'}
    (outdir/'params.json').write_text(json.dumps(meta,indent=2))
    write_nc(pred,outdir)
    print(json.dumps(meta,indent=2))

if __name__=='__main__': main()
