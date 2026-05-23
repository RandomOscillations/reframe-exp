from __future__ import annotations
import json, math, os, time
from pathlib import Path
import numpy as np
import optuna
import xarray as xr
import cftime

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import load_drivers, load_gfed_1deg, add_cf_bounds, uncoarsen, sig, supp, hump

REPO = Path(__file__).resolve().parents[1]
OUTDIR = REPO / 'experiments' / 'modelC_mechanism_search'
OUTDIR.mkdir(parents=True, exist_ok=True)
YEARS = list(range(2001, 2017))
N_MONTHS = 192
FIRE_MAX_RATE = 5.0

REGIONS = {
    'bona': ((49.75,79.75),(-170.25,-60.25)),
    'tena': ((30.25,49.75),(-125.25,-66.25)),
    'ceam': ((9.75,30.25),(-115.25,-80.25)),
    'nhsa': ((0.25,12.75),(-80.25,-50.25)),
    'shsa': ((-59.75,0.25),(-80.25,-33.25)),
    'euro': ((35.25,70.25),(-10.25,30.25)),
    'mide': ((20.25,40.25),(-10.25,60.25)),
    'nhaf': ((0.25,20.25),(-20.25,45.25)),
    'shaf': ((-34.75,0.25),(10.25,45.25)),
    'boas': ((54.75,70.25),(30.25,179.75)),
    'ceas': ((30.25,54.75),(30.25,142.58)),
    'seas': ((5.25,30.25),(65.25,120.25)),
    'eqas': ((-10.25,10.25),(99.75,150.25)),
    'aust': ((-41.25,-10.50),(112.00,154.00)),
}

BASE = json.load(open(REPO/'models/C/params.json'))['params']

print('[setup] load drivers')
drivers = load_drivers()
obs = load_gfed_1deg().astype(np.float32)
lat = np.arange(-89.5, 90.0, 1.0).astype(np.float32)
lon = np.arange(-179.5, 180.0, 1.0).astype(np.float32)
cos_lat = np.cos(np.deg2rad(lat)).astype(np.float64)
w2 = np.broadcast_to(cos_lat[:,None], (180,360)).astype(np.float64)
w3 = np.broadcast_to(cos_lat[None,:,None], obs.shape).astype(np.float64)
land_mask = (obs > 0).any(axis=0)

gfed_tm = obs.mean(axis=0).astype(np.float64)
gfed_std = obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc = obs.reshape(16,12,180,360).mean(axis=0)
gfed_peak = np.argmax(gfed_cyc, axis=0).astype(np.float32)
mass_w = (w2 * gfed_tm).astype(np.float64)
mass_w_burn = mass_w * land_mask
w2_burn = w2 * land_mask

region_masks = {}
for k,(lats,lons) in REGIONS.items():
    region_masks[k] = ((lat[:,None] >= lats[0]) & (lat[:,None] <= lats[1]) &
                       (lon[None,:] >= lons[0]) & (lon[None,:] <= lons[1]) & land_mask)


def ed_transform(rate):
    return ((1.0 - np.exp(-np.minimum(rate, FIRE_MAX_RATE))) / 12.0).astype(np.float32)


def formula_base(p):
    onset = sig(drivers['dbar'], p['k1'], p['D_low'])
    dry_suppress = supp(drivers['dbar'], p['k2'], p['D_high'])
    p_floor = drivers['p_ann'] / (drivers['p_ann'] + p['P_half'] + 1e-12)
    p_damp = 1.0 / (1.0 + drivers['p_month'] / (p['pre_dampen_half'] + 1e-12))
    gpp_mod = hump(p['gpp_af'] * drivers['gpp_monthly'], p['gpp_b'], p['gpp_d'])
    ign_mod = sig(drivers['t_air'], p['ign_k'], p['ign_c'])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p['fire_exp']).astype(np.float32)


def formula_precip_shape(p):
    onset = sig(drivers['dbar'], p['k1'], p['D_low'])
    dry_suppress = supp(drivers['dbar'], p['k2'], p['D_high'])
    p_floor0 = drivers['p_ann'] / (drivers['p_ann'] + p['P_half'] + 1e-12)
    p_damp0 = 1.0 / (1.0 + drivers['p_month'] / (p['pre_dampen_half'] + 1e-12))
    p_floor = np.power(np.clip(p_floor0,1e-8,1), p['p_floor_exp'])
    p_damp = np.power(np.clip(p_damp0,1e-8,1), p['p_damp_exp'])
    gpp_mod = hump(p['gpp_af'] * drivers['gpp_monthly'], p['gpp_b'], p['gpp_d'])
    ign_mod = sig(drivers['t_air'], p['ign_k'], p['ign_c'])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p['fire_exp']).astype(np.float32)


def formula_temp_window(p):
    onset = sig(drivers['dbar'], p['k1'], p['D_low'])
    dry_suppress = supp(drivers['dbar'], p['k2'], p['D_high'])
    p_floor = drivers['p_ann'] / (drivers['p_ann'] + p['P_half'] + 1e-12)
    p_damp = 1.0 / (1.0 + drivers['p_month'] / (p['pre_dampen_half'] + 1e-12))
    gpp_mod = hump(p['gpp_af'] * drivers['gpp_monthly'], p['gpp_b'], p['gpp_d'])
    ign_mod = sig(drivers['t_air'], p['ign_k'], p['ign_c']) * supp(drivers['t_air'], p['heat_k'], p['heat_c'])
    product = onset * dry_suppress * p_floor * p_damp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p['fire_exp']).astype(np.float32)


def formula_humid_suppression(p):
    onset = sig(drivers['dbar'], p['k1'], p['D_low'])
    dry_suppress = supp(drivers['dbar'], p['k2'], p['D_high'])
    p_floor = drivers['p_ann'] / (drivers['p_ann'] + p['P_half'] + 1e-12)
    p_damp = 1.0 / (1.0 + drivers['p_month'] / (p['pre_dampen_half'] + 1e-12))
    humid_supp = supp(drivers['p_ann'], p['humid_k'], p['humid_c'])
    gpp_mod = hump(p['gpp_af'] * drivers['gpp_monthly'], p['gpp_b'], p['gpp_d'])
    ign_mod = sig(drivers['t_air'], p['ign_k'], p['ign_c'])
    product = onset * dry_suppress * p_floor * p_damp * humid_supp * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p['fire_exp']).astype(np.float32)


def formula_fuel_moisture_balance(p):
    onset = sig(drivers['dbar'], p['k1'], p['D_low'])
    dry_suppress = supp(drivers['dbar'], p['k2'], p['D_high'])
    p_floor = drivers['p_ann'] / (drivers['p_ann'] + p['P_half'] + 1e-12)
    p_damp = 1.0 / (1.0 + drivers['p_month'] / (p['pre_dampen_half'] + 1e-12))
    # In wet productive cells, high monthly precipitation should suppress less if accumulated dryness is high;
    # in persistently humid cells, dampening remains strong. Smooth global physical interaction, not region routing.
    dry_relief = sig(drivers['dbar'], p['relief_k'], p['relief_c'])
    p_damp_eff = p_damp + (1.0 - p_damp) * p['relief_amp'] * dry_relief
    gpp_mod = hump(p['gpp_af'] * drivers['gpp_monthly'], p['gpp_b'], p['gpp_d'])
    ign_mod = sig(drivers['t_air'], p['ign_k'], p['ign_c'])
    product = onset * dry_suppress * p_floor * np.clip(p_damp_eff,0,1) * gpp_mod * ign_mod
    return np.power(np.clip(product, 0, None), p['fire_exp']).astype(np.float32)

FAMILIES = {
    'base_refit': (formula_base, {}),
    'precip_shape': (formula_precip_shape, {'p_floor_exp':(0.2,5.0,'log'), 'p_damp_exp':(0.2,5.0,'log')}),
    'temp_window': (formula_temp_window, {'heat_k':(0.01,5.0,'log'), 'heat_c':(25.0,60.0,'linear')}),
    'humid_suppression': (formula_humid_suppression, {'humid_k':(0.0001,0.05,'log'), 'humid_c':(500.0,5000.0,'log')}),
    'fuel_moisture_balance': (formula_fuel_moisture_balance, {'relief_k':(0.0001,0.05,'log'), 'relief_c':(50.0,5000.0,'log'), 'relief_amp':(0.0,0.8,'linear')}),
}

BASE_SPACE = {
    'k1':(1e-5,1e-1,'log'), 'D_low':(1.0,1e4,'log'), 'k2':(1e-5,1e-1,'log'), 'D_high':(10.0,1e5,'log'),
    'fire_exp':(0.4,5.0,'log'), 'P_half':(0.1,1e4,'log'), 'pre_dampen_half':(0.01,1e3,'log'),
    'gpp_af':(1e-3,1e2,'log'), 'gpp_b':(1e-6,1e1,'log'), 'gpp_d':(0.01,1e3,'log'),
    'ign_k':(1e-3,1e1,'log'), 'ign_c':(0.1,50.0,'log'),
}


def predict(formula, p):
    rate = formula(p) * land_mask[None,:,:]
    return ed_transform(rate)


def component_scores(pred, mask=None):
    if mask is None:
        mask = land_mask
    if mask.sum() < 5:
        return dict(bias=np.nan, rmse=np.nan, seasonal=np.nan, spatial=np.nan, overall=np.nan)
    pred_tm = pred.mean(axis=0).astype(np.float64)
    mw = mass_w * mask
    mwb = mw
    if mw.sum() <= 0:
        ww = w2 * mask
        mw = ww
        mwb = ww
    bias_s = np.exp(-np.abs(pred_tm - gfed_tm) / gfed_std)
    bias = float((bias_s * mw).sum() / (mw.sum()+1e-12))
    pred_anom = pred - pred_tm[None,:,:]
    obs_anom = obs - gfed_tm[None,:,:]
    crmse = np.sqrt(((pred_anom - obs_anom)**2).mean(axis=0))
    rmse_s = np.exp(-crmse / gfed_std)
    rmse = float((rmse_s * mw).sum() / (mw.sum()+1e-12))
    pred_cyc = pred.reshape(16,12,180,360).mean(axis=0)
    pred_peak = np.argmax(pred_cyc, axis=0).astype(np.float32)
    shift = pred_peak - gfed_peak
    shift = np.where(shift > 6, shift-12, shift)
    shift = np.where(shift < -6, shift+12, shift)
    seas_s = (1+np.cos(np.abs(shift)/12*2*np.pi))*0.5
    seasonal = float((seas_s * mwb).sum()/(mwb.sum()+1e-12))
    obs_flat = gfed_tm[mask]
    pred_flat = pred_tm[mask]
    pw = (w2*mask)[mask]
    ow = (obs_flat*pw).sum()/pw.sum(); pp = (pred_flat*pw).sum()/pw.sum()
    oa = obs_flat-ow; pa=pred_flat-pp
    std0=max(float(np.sqrt(((oa**2)*pw).sum()/pw.sum())),1e-12)
    std=max(float(np.sqrt(((pa**2)*pw).sum()/pw.sum())),1e-12)
    rho=float((pa*oa*pw).sum()/(np.sqrt(((pa**2)*pw).sum()*((oa**2)*pw).sum())+1e-12))
    sigma=std/std0
    spatial=float(2*(1+rho)/((sigma+1/max(sigma,1e-12))**2))
    overall=(2*bias+2*rmse+seasonal+spatial)/6
    return dict(bias=bias, rmse=rmse, seasonal=seasonal, spatial=spatial, overall=overall)


def score_candidate(pred):
    g = component_scores(pred)
    regs = {r: component_scores(pred, m) for r,m in region_masks.items()}
    ro = np.array([v['overall'] for v in regs.values() if np.isfinite(v['overall'])])
    # Keep global primary, but reward regional robustness and worst-region repair.
    objective = 0.75*g['overall'] + 0.15*float(np.mean(ro)) + 0.10*float(np.quantile(ro,0.20))
    return objective, g, regs


def suggest(trial, name, spec):
    lo,hi,kind=spec
    return trial.suggest_float(name,lo,hi,log=(kind=='log'))


def write_nc(model_name, pred):
    pred_hd = uncoarsen(np.where(land_mask[None,:,:], pred, np.nan).astype(np.float32))
    times=[cftime.DatetimeNoLeap(y,m,15) for y in YEARS for m in range(1,13)]
    lat_hd=np.arange(-89.75,90.0,0.5); lon_hd=np.arange(-179.75,180.0,0.5)
    ds=xr.Dataset({'burntArea':(('time','lat','lon'), pred_hd, {'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})}, coords={'time':('time',times),'lat':('lat',lat_hd),'lon':('lon',lon_hd)}, attrs={'title':model_name,'Conventions':'CF-1.7','transform':'monthly_frac=(1-exp(-min(rate_yr,5)*1yr))/12'})
    ds=add_cf_bounds(ds)
    enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20}, 'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}, 'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    d=REPO/'ilamb/MODELS'/model_name
    d.mkdir(parents=True,exist_ok=True)
    tmp=d/'burntArea.nc.tmp'; dst=d/'burntArea.nc'
    ds.to_netcdf(tmp,encoding=enc,format='NETCDF4_CLASSIC')
    os.replace(tmp,dst)
    return str(dst)


def run_family(name, n_trials, seed):
    formula, extra = FAMILIES[name]
    space = dict(BASE_SPACE); space.update(extra)
    sampler=optuna.samplers.TPESampler(seed=seed, multivariate=True, warn_independent_sampling=False)
    study=optuna.create_study(direction='maximize', sampler=sampler)
    warm=dict(BASE)
    for k,(lo,hi,kind) in extra.items():
        if k.endswith('_exp'): warm[k]=1.0
        elif k=='heat_k': warm[k]=0.05
        elif k=='heat_c': warm[k]=45.0
        elif k=='humid_k': warm[k]=0.001
        elif k=='humid_c': warm[k]=2500.0
        elif k=='relief_k': warm[k]=0.002
        elif k=='relief_c': warm[k]=500.0
        elif k=='relief_amp': warm[k]=0.2
    study.enqueue_trial(warm)
    def objective(trial):
        p={k:suggest(trial,k,s) for k,s in space.items()}
        pred=predict(formula,p)
        obj,_,_=score_candidate(pred)
        return obj
    t0=time.time()
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    p=study.best_params
    pred=predict(formula,p)
    obj,g,regs=score_candidate(pred)
    model_name='ED-ModelC-' + name
    nc=write_nc(model_name,pred)
    result={'family':name,'model_name':model_name,'n_trials':len(study.trials),'runtime_min':(time.time()-t0)/60,'objective':obj,'global_proxy':g,'regional_proxy':regs,'params':p,'nc':nc}
    (OUTDIR/f'{name}.json').write_text(json.dumps(result,indent=2))
    print('[result]', name, 'obj', obj, 'global', g, 'nc', nc, flush=True)
    return result


def main():
    n=int(os.environ.get('N_TRIALS_PER_FAMILY','500'))
    families=os.environ.get('FAMILIES', ','.join(FAMILIES)).split(',')
    results=[]
    # baseline diagnostics
    pred0=predict(formula_base,BASE)
    obj0,g0,r0=score_candidate(pred0)
    baseline={'family':'original_C','model_name':'ED-ModelC-final','objective':obj0,'global_proxy':g0,'regional_proxy':r0,'params':BASE,'nc':str(REPO/'ilamb/MODELS/ED-ModelC-final/burntArea.nc')}
    (OUTDIR/'original_C.json').write_text(json.dumps(baseline,indent=2))
    print('[baseline]', obj0, g0)
    for i,f in enumerate(families):
        results.append(run_family(f.strip(), n, 100+i))
    summary=[baseline]+results
    (OUTDIR/'summary.json').write_text(json.dumps(summary,indent=2))
    print('[done] wrote', OUTDIR/'summary.json')

if __name__=='__main__':
    main()
