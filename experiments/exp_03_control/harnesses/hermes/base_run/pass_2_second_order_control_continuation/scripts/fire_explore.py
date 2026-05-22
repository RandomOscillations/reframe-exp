from __future__ import annotations
import argparse, json, math, os, shutil, subprocess, time
from pathlib import Path
import h5py
import numpy as np
import optuna
import pandas as pd
import xarray as xr
import cftime

REPO = Path(__file__).resolve().parents[1]
N_MONTHS = 192
YEARS = list(range(2001, 2017))
REGION_KEYS = ['global','bona','tena','ceam','nhsa','shsa','euro','mide','nhaf','shaf','boas','ceas','seas','eqas','aust']
FIRE_MAX_RATE = 5.0


def coarsen(arr):
    return arr.reshape(*arr.shape[:-2], 180, 2, 360, 2).mean(axis=(-3, -1)).astype(np.float32)

def uncoarsen(arr):
    return np.repeat(np.repeat(arr, 2, axis=1), 2, axis=2).astype(np.float32)

def sig(x,k,c): return 1/(1+np.exp(np.clip(-k*(x-c),-50,50)))
def supp(x,k,c): return 1/(1+np.exp(np.clip(k*(x-c),-50,50)))
def hump(x,b,dec):
    return (1-np.exp(-np.clip(x/max(b,1e-9),0,500))) * np.exp(-np.clip(x/max(dec,1e-9),0,500))

def load_params(): return json.loads((REPO/'models/C/params.json').read_text())['params']

def load_drivers_obs():
    cru=REPO/'data/crujra'
    d={k:np.load(cru/f'{fn}_monthly.npy').astype(np.float32) for k,fn in [('dbar','dbar'),('p_ann','p_ann'),('p_month','p_month'),('t_air','t_air')]}
    ds=xr.open_dataset(REPO/'data/trendy_v14/EDv3_S3_gpp.nc', decode_times=False)
    gpp=ds['gpp'].isel(time=slice(3612,3804)).values.astype(np.float32)*86400*365
    lat_v=ds.latitude.values if 'latitude' in ds.coords else ds.lat.values
    if lat_v[0] > 0: gpp=gpp[:,::-1,:]
    d['gpp_monthly']=coarsen(np.nan_to_num(gpp,nan=0.0)); ds.close()
    obs=np.zeros((N_MONTHS,180,360),np.float32); idx=0
    for yr in YEARS:
        with h5py.File(REPO/'data/gfed'/f'GFED4.1s_{yr}.hdf5','r') as f:
            for m in range(1,13):
                a=f[f'burned_area/{m:02d}/burned_fraction'][:][::-1,:]
                obs[idx]=a.reshape(180,4,360,4).mean(axis=(1,3)); idx+=1
    obs=np.nan_to_num(obs,nan=0.0)
    return d,obs

def region_masks(land_mask):
    # Mirror the built-in GFED rectangular regions from ILAMB.Regions._regions.
    from ILAMB.Regions import Regions
    r=Regions(); lat=np.arange(-89.5,90,1.0); lon=np.arange(-179.5,180,1.0)
    lon2, lat2 = np.meshgrid(lon, lat)
    masks={}
    for key in REGION_KEYS:
        if key=='global':
            masks[key]=land_mask.copy(); continue
        _, lat_edges, lon_edges, _ = r._regions[key]
        inside=(lat2 >= lat_edges[1]) & (lat2 <= lat_edges[2]) & (lon2 >= lon_edges[1]) & (lon2 <= lon_edges[2])
        masks[key]=inside & land_mask
    return masks

def base_rate(d,p):
    return (sig(d['dbar'],p['k1'],p['D_low']) * supp(d['dbar'],p['k2'],p['D_high']) *
            (d['p_ann']/(d['p_ann']+p['P_half']+1e-12)) *
            (1/(1+d['p_month']/(p['pre_dampen_half']+1e-12))) *
            hump(p['gpp_af']*d['gpp_monthly'],p['gpp_b'],p['gpp_d']) *
            sig(d['t_air'],p['ign_k'],p['ign_c']))

def candidate_rate(d,p,family):
    prod=base_rate(d,p)
    if family in ('annual_humid_supp','combined'):
        prod *= 1/(1+np.power(np.maximum(d['p_ann'],0)/(p['P_humid']+1e-12), p['P_humid_q']))
    if family in ('wetmonth_logistic','combined'):
        prod *= supp(d['p_month'], p['wet_k'], p['wet_c'])
    if family in ('seasonal_contrast','combined'):
        # Curing/seasonal contrast: wet month relative to annual climatology suppresses active fire.
        mean_m = d['p_ann']/12.0
        ratio = d['p_month']/(mean_m + p['contrast_eps'])
        prod *= 1/(1+np.power(np.maximum(ratio,0), p['contrast_q']))
    if family in ('dry_gated_humid','second_order_combo'):
        # Previous humid suppression helped weak wet regions but damaged dry savannas/boreal.
        # Gate the high-annual-precipitation suppression by LOW accumulated deficit so it acts
        # mainly on persistently wet, uncured fuels and relaxes when sustained dry-season deficit exists.
        humid = 1/(1+np.power(np.maximum(d['p_ann'],0)/(p['P_humid']+1e-12), p['P_humid_q']))
        lowdry = supp(d['dbar'], p['drygate_k'], p['drygate_c'])
        prod *= np.clip(1 - p['humid_alpha'] * lowdry * (1 - humid), 0, 1)
    if family in ('dry_gated_wetmonth','second_order_combo'):
        # Current-month rain only suppresses active burning when the cell has not accumulated
        # enough antecedent drying; intended to preserve dry savanna fire while damping wet mosaics.
        wet = supp(d['p_month'], p['wet_k'], p['wet_c'])
        lowdry = supp(d['dbar'], p['drygate_k'], p['drygate_c'])
        prod *= np.clip(1 - p['wet_alpha'] * lowdry * (1 - wet), 0, 1)
    if family in ('wet_productive_forest','second_order_combo'):
        # Wet productive forest/closed-canopy proxy: high GPP + high annual rain + low deficit.
        # This is a fire-type inference from allowed cell state, not a region route.
        highgpp = sig(d['gpp_monthly'], p['gppwet_k'], p['gppwet_c'])
        highp = sig(d['p_ann'], p['pwet_k'], p['pwet_c'])
        lowdry = supp(d['dbar'], p['drygate_k'], p['drygate_c'])
        prod *= np.clip(1 - p['wetprod_alpha'] * highgpp * highp * lowdry, 0, 1)
    if family in ('hyperarid_fuel','second_order_combo'):
        # Very low precipitation plus low productivity: fuel discontinuity / desert limitation.
        # Kept separate because broad hyperarid suppression risks damaging Australian drylands.
        lowp = supp(d['p_ann'], p['arid_k'], p['arid_c'])
        lowgpp = supp(d['gpp_monthly'], p['gppmin_k'], p['gppmin_c'])
        prod *= np.clip(1 - p['arid_alpha'] * lowp * lowgpp, 0, 1)
    if family in ('cool_uncured_supp','second_order_combo'):
        # Temperature ignition interaction: cool, insufficiently cured months should not burn
        # efficiently even if productivity exists. Hot/dry savannas should be mostly untouched.
        cool = supp(d['t_air'], p['cool_k'], p['cool_c'])
        lowdry = supp(d['dbar'], p['drygate_k'], p['drygate_c'])
        prod *= np.clip(1 - p['cool_alpha'] * cool * lowdry, 0, 1)
    return np.power(np.clip(prod,0,None),p['fire_exp']).astype(np.float32)

def transform(rate,land_mask):
    return ((1-np.exp(-np.minimum(rate*land_mask[None,:,:], FIRE_MAX_RATE)))/12).astype(np.float32)

def proxy_scores(pred,obs,w3,masks):
    out={}
    for key,mask in masks.items():
        ww=w3*mask[None,:,:]
        sw=ww.sum()+1e-12
        pm=float((pred*ww).sum()/sw); om=float((obs*ww).sum()/sw)
        bias=math.exp(-abs(math.log((pm+1e-12)/(om+1e-12))))
        diff=pred-obs
        rmse=float(np.sqrt(((diff*diff)*ww).sum()/sw))
        obs_std=float(np.sqrt((((obs-om)**2)*ww).sum()/sw))+1e-12
        rmse_score=1/(1+rmse/obs_std)
        # seasonal monthly climatology correlation score
        ps=[]; os=[]
        for m in range(12):
            ps.append(float((pred[m::12]*ww[m::12]).sum()/(ww[m::12].sum()+1e-12)))
            os.append(float((obs[m::12]*ww[m::12]).sum()/(ww[m::12].sum()+1e-12)))
        pc=np.array(ps); oc=np.array(os)
        seas=max(0.0,float(np.corrcoef(pc,oc)[0,1])) if pc.std()>0 and oc.std()>0 else 0.0
        # spatial annual mean correlation weighted
        pa=(pred.reshape(16,12,180,360).mean(axis=(0,1)))
        oa=(obs.reshape(16,12,180,360).mean(axis=(0,1)))
        x=pa[mask]; y=oa[mask]
        spat=max(0.0,float(np.corrcoef(x,y)[0,1])) if x.size>3 and x.std()>0 and y.std()>0 else 0.0
        overall=(2*bias+2*rmse_score+seas+spat)/6
        out[key]={'bias':bias,'rmse':rmse_score,'seasonal':seas,'spatial':spat,'overall':overall,'pred_mean':pm,'obs_mean':om,'ratio':pm/(om+1e-12)}
    return out

def propose(trial,base,family,tune_base=False):
    p=dict(base)
    if tune_base:
        p['fire_exp']=trial.suggest_float('fire_exp',0.35,0.9)
        p['D_low']=trial.suggest_float('D_low',10,150)
        p['D_high']=trial.suggest_float('D_high',1500,6000)
        p['pre_dampen_half']=trial.suggest_float('pre_dampen_half',1,40,log=True)
        p['P_half']=trial.suggest_float('P_half',0.5,30,log=True)
        p['gpp_d']=trial.suggest_float('gpp_d',20,400,log=True)
        p['ign_c']=trial.suggest_float('ign_c',10,30)
    if family in ('annual_humid_supp','combined'):
        p['P_humid']=trial.suggest_float('P_humid',300,3500,log=True)
        p['P_humid_q']=trial.suggest_float('P_humid_q',0.3,5.0)
    if family in ('wetmonth_logistic','combined','dry_gated_wetmonth','second_order_combo'):
        p['wet_k']=trial.suggest_float('wet_k',0.005,0.3,log=True)
        p['wet_c']=trial.suggest_float('wet_c',5,250,log=True)
    if family in ('seasonal_contrast','combined'):
        p['contrast_eps']=trial.suggest_float('contrast_eps',0.5,20,log=True)
        p['contrast_q']=trial.suggest_float('contrast_q',0.2,5.0)
    if family in ('dry_gated_humid','second_order_combo'):
        p['P_humid']=trial.suggest_float('P_humid',500,5000,log=True)
        p['P_humid_q']=trial.suggest_float('P_humid_q',0.3,6.0)
        p['humid_alpha']=trial.suggest_float('humid_alpha',0.05,1.0)
    if family in ('dry_gated_humid','dry_gated_wetmonth','wet_productive_forest','cool_uncured_supp','second_order_combo'):
        p['drygate_k']=trial.suggest_float('drygate_k',0.001,0.05,log=True)
        p['drygate_c']=trial.suggest_float('drygate_c',50,2500,log=True)
    if family in ('dry_gated_wetmonth','second_order_combo'):
        p['wet_alpha']=trial.suggest_float('wet_alpha',0.05,1.0)
    if family in ('wet_productive_forest','second_order_combo'):
        p['wetprod_alpha']=trial.suggest_float('wetprod_alpha',0.05,1.0)
        p['gppwet_k']=trial.suggest_float('gppwet_k',0.5,8.0,log=True)
        p['gppwet_c']=trial.suggest_float('gppwet_c',0.3,3.0)
        p['pwet_k']=trial.suggest_float('pwet_k',0.001,0.02,log=True)
        p['pwet_c']=trial.suggest_float('pwet_c',500,2500)
    if family in ('hyperarid_fuel','second_order_combo'):
        p['arid_alpha']=trial.suggest_float('arid_alpha',0.05,1.0)
        p['arid_k']=trial.suggest_float('arid_k',0.005,0.05,log=True)
        p['arid_c']=trial.suggest_float('arid_c',100,600)
        p['gppmin_k']=trial.suggest_float('gppmin_k',1.0,20.0,log=True)
        p['gppmin_c']=trial.suggest_float('gppmin_c',0.05,0.8)
    if family in ('cool_uncured_supp','second_order_combo'):
        p['cool_alpha']=trial.suggest_float('cool_alpha',0.05,1.0)
        p['cool_k']=trial.suggest_float('cool_k',0.05,0.8,log=True)
        p['cool_c']=trial.suggest_float('cool_c',5.0,25.0)
    return p

def tune(args):
    d,obs=load_drivers_obs(); base=load_params(); land=(obs>0).any(axis=0)
    lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32)
    masks=region_masks(land)
    def objective(trial):
        p=propose(trial,base,args.family,args.tune_base)
        pred=transform(candidate_rate(d,p,args.family),land)
        scores=proxy_scores(pred,obs,w3,masks)
        # weighted: global plus weak-region uplift; avoid sacrificing global.
        weak=['ceam','euro','mide','tena','eqas','seas','shsa']
        val=0.55*scores['global']['overall']+0.45*np.mean([scores[k]['overall'] for k in weak])
        trial.set_user_attr('global', scores['global'])
        trial.set_user_attr('weak_mean', float(np.mean([scores[k]['overall'] for k in weak])))
        trial.set_user_attr('params', p)
        return val
    study=optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=args.seed))
    study.optimize(objective, n_trials=args.trials, show_progress_bar=True)
    best=study.best_trial.user_attrs['params']; best['_family']=args.family
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'family':args.family,'trials':args.trials,'best_value':study.best_value,'params':best,'global_proxy':study.best_trial.user_attrs['global'],'weak_mean_proxy':study.best_trial.user_attrs['weak_mean']},indent=2))
    print(out)
    print(json.dumps(json.loads(out.read_text()),indent=2))

def add_cf_bounds(ds):
    times=ds.time.values; tb=np.empty((len(times),2),dtype=object)
    for i,t in enumerate(times):
        y,m=t.year,t.month; tb[i,0]=cftime.DatetimeNoLeap(y,m,1); tb[i,1]=cftime.DatetimeNoLeap(y+(m==12),(m%12)+1,1)
    ds=ds.assign(time_bounds=(("time","nb"),tb)); ds.time.attrs.update({'bounds':'time_bounds','standard_name':'time','axis':'T'})
    lat=ds.lat.values; dlat=abs(float(lat[1]-lat[0])); lon=ds.lon.values; dlon=abs(float(lon[1]-lon[0]))
    ds=ds.assign(lat_bounds=(("lat","nb"),np.stack([lat-dlat/2,lat+dlat/2],axis=1)), lon_bounds=(("lon","nb"),np.stack([lon-dlon/2,lon+dlon/2],axis=1)))
    ds.lat.attrs.update({'bounds':'lat_bounds','units':'degrees_north','standard_name':'latitude','axis':'Y'}); ds.lon.attrs.update({'bounds':'lon_bounds','units':'degrees_east','standard_name':'longitude','axis':'X'})
    return ds

def write_nc(args):
    d,obs=load_drivers_obs(); p=json.loads(Path(args.params).read_text())['params']; family=p.get('_family',args.family)
    land=(obs>0).any(axis=0); pred=np.where(land[None,:,:], transform(candidate_rate(d,p,family),land), np.nan).astype(np.float32)
    pred_hd=uncoarsen(pred)
    times=[cftime.DatetimeNoLeap(y,m,15) for y in YEARS for m in range(1,13)]
    ds=xr.Dataset({'burntArea':(('time','lat','lon'),pred_hd,{'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})}, coords={'time':('time',times),'lat':('lat',np.arange(-89.75,90,0.5)),'lon':('lon',np.arange(-179.75,180,0.5))}, attrs={'title':args.model,'family':family})
    ds=add_cf_bounds(ds); out=REPO/'ilamb/MODELS'/args.model; out.mkdir(parents=True,exist_ok=True)
    enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20},'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'},'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    tmp=out/'burntArea.nc.tmp'; ds.to_netcdf(tmp,encoding=enc,format='NETCDF4_CLASSIC'); os.replace(tmp,out/'burntArea.nc')
    print(out/'burntArea.nc')

def diag(args):
    d,obs=load_drivers_obs(); land=(obs>0).any(axis=0); lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32); masks=region_masks(land)
    p=load_params(); pred=transform(np.power(np.clip(base_rate(d,p),0,None),p['fire_exp']).astype(np.float32),land)
    scores=proxy_scores(pred,obs,w3,masks)
    print(json.dumps(scores,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    families=['annual_humid_supp','wetmonth_logistic','seasonal_contrast','combined','dry_gated_humid','dry_gated_wetmonth','wet_productive_forest','hyperarid_fuel','cool_uncured_supp','second_order_combo']
    t=sub.add_parser('tune'); t.add_argument('--family',required=True,choices=families); t.add_argument('--trials',type=int,default=500); t.add_argument('--out',required=True); t.add_argument('--seed',type=int,default=7); t.add_argument('--tune-base',action='store_true')
    w=sub.add_parser('write-nc'); w.add_argument('--params',required=True); w.add_argument('--model',required=True); w.add_argument('--family',default='annual_humid_supp')
    sub.add_parser('diag')
    args=ap.parse_args()
    if args.cmd=='tune': tune(args)
    elif args.cmd=='write-nc': write_nc(args)
    else: diag(args)
