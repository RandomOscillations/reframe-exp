"""Pass-2 fire model research starting from F3b, not original Model C.

All formulas use only allowed Model C/F3b inputs and global smooth transforms.
"""
from __future__ import annotations
import argparse, json, os, sys, time, math
from pathlib import Path
import numpy as np, optuna, xarray as xr, cftime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import load_drivers, load_gfed_1deg, fire_C, add_cf_bounds, uncoarsen

REPO=Path(__file__).resolve().parents[1]
MODELS_DIR=REPO/'models'/'C'
RESEARCH_DIR=REPO/'research_candidates_pass2'; RESEARCH_DIR.mkdir(exist_ok=True)
OUT_NC=REPO/'ilamb'/'MODELS'/'ED-ModelC-final'/'burntArea.nc'
YEARS=list(range(2001,2017)); N_MONTHS=192
FIRE_MAX_RATE=float(os.environ.get('FIRE_MAX_RATE',5.0))
N_TRIALS=int(os.environ.get('N_TRIALS',500)); SEED=int(os.environ.get('SEED',701))

print('[setup] loading drivers + GFED ...')
drivers=load_drivers(); obs=load_gfed_1deg()
lat_1=np.arange(-89.5,90.0,1.0).astype(np.float32)
cos_lat=np.cos(np.deg2rad(lat_1)).astype(np.float32)
w2=np.broadcast_to(cos_lat[:,None],(180,360)).astype(np.float64)
w3=np.broadcast_to(cos_lat[None,:,None],(N_MONTHS,180,360)).astype(np.float64)
land_mask=(obs>0).any(axis=0); w2_burn=(w2*land_mask).astype(np.float64); w3_land=(w3*land_mask[None,:,:]).astype(np.float64)
print(f'[setup] land cells: {int(land_mask.sum())} / {land_mask.size}')

gfed_tm=obs.mean(axis=0).astype(np.float64); gfed_std=obs.std(axis=0).clip(1e-12).astype(np.float64)
gfed_cyc=obs.reshape(16,12,180,360).mean(axis=0); gfed_peak_month=np.argmax(gfed_cyc,axis=0).astype(np.float32)
mass_w=(w2*gfed_tm).astype(np.float64); mass_w_burn=(mass_w*land_mask).astype(np.float64)

def load_json(path): return json.load(open(path))
def load_base():
    for path in [MODELS_DIR/'params.BASELINE-before-research.json']:
        obj=load_json(path); p=obj.get('params',obj)
        if 'k1' in p: return p
    raise RuntimeError('base params missing')
BASE=load_base()

def load_f3b():
    """Load the pass-1 F3b incumbent even after pass-2 emits overwrite params.json."""
    for path in [REPO/'research_candidates'/'F3abl_no_cool.json', MODELS_DIR/'params.json']:
        if not path.exists():
            continue
        obj=load_json(path); p=obj.get('params',obj)
        if all(k in p for k in ['wet_amp','wet_k','wet_c','ratio_p0','arid_amp','arid_k','arid_c']):
            return p
    raise RuntimeError('F3b incumbent params missing')
F3B=load_f3b()

def sig(x,k,c): return 1/(1+np.exp(np.clip(-k*(x-c),-50,50)))
def supp(x,k,c): return 1/(1+np.exp(np.clip(k*(x-c),-50,50)))
def ed_transform(rate): return ((1-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12).astype(np.float32)

dbar_prev=np.concatenate([drivers['dbar'][:1],drivers['dbar'][:-1]],axis=0)
drying_rate=np.maximum(drivers['dbar']-dbar_prev,0).astype(np.float32)
p_rel=drivers['p_month']/(drivers['p_ann']/12.0+1e-6)
# previous 3 month precipitation anomaly: low values mean antecedent curing after wet growth
p_rel_prev=np.concatenate([p_rel[:1],p_rel[:-1]],axis=0)

def f3b_rate(d,p=F3B):
    base=fire_C(d,BASE)
    wet=1-p['wet_amp']*sig(d['p_ann'],p['wet_k'],p['wet_c'])
    deficit=d['dbar']/(d['p_ann']+p['ratio_p0'])
    arid=1-p['arid_amp']*sig(deficit,p['arid_k'],p['arid_c'])
    return (base*np.clip(wet*arid,0,1)).astype(np.float32)

def fire_p2_curing_gate(d,p):
    """F3b times global seasonal curing gate: fire survives when dry, drying, and rain-free align."""
    base=f3b_rate(d)
    dry_state=sig(d['dbar'],p['dry_k'],p['dry_c'])
    dry_tendency=sig(drying_rate,p['dr_k'],p['dr_c'])
    rainfree=supp(p_rel,p['pr_k'],p['pr_c'])
    curing=np.clip(dry_state*dry_tendency*rainfree,0,1)
    gate=(1-p['gate_amp'])+p['gate_amp']*np.power(curing,p['gate_gamma'])
    return (base*np.clip(gate,0,1)).astype(np.float32)

def fire_p2_seasonal_wet(d,p):
    """Model C core times arid limiter and seasonal wet inhibition instead of blunt annual wet inhibition."""
    base=fire_C(d,BASE)
    deficit=d['dbar']/(d['p_ann']+F3B['ratio_p0'])
    arid=1-F3B['arid_amp']*sig(deficit,F3B['arid_k'],F3B['arid_c'])
    wet_climate=sig(d['p_ann'],p['wet_k'],p['wet_c'])
    rainy_now=sig(p_rel,p['rain_k'],p['rain_c'])
    # optional antecedent-rain memory: if previous months were wet, fuels/canopy remain moist
    rainy_prev=sig(p_rel_prev,p['prev_k'],p['prev_c'])
    wet_inhib=wet_climate*((1-p['prev_weight'])*rainy_now + p['prev_weight']*rainy_prev)
    wet=1-p['wet_amp']*wet_inhib
    return (base*np.clip(wet*arid,0,1)).astype(np.float32)

def fire_p2_arid_softplus(d,p):
    """F3b variant replacing arid sigmoid with a smoother two-threshold desert/semidesert limiter."""
    base=fire_C(d,BASE)
    wet=1-F3B['wet_amp']*sig(d['p_ann'],F3B['wet_k'],F3B['wet_c'])
    deficit=d['dbar']/(d['p_ann']+p['ratio_p0'])
    arid1=1-p['arid_amp1']*sig(deficit,p['arid_k1'],p['arid_c1'])
    arid2=1-p['arid_amp2']*sig(deficit,p['arid_k2'],p['arid_c2'])
    return (base*np.clip(wet*arid1*arid2,0,1)).astype(np.float32)

def fire_p2_seasonal_wet_arid2(d,p):
    """Hybrid: seasonal wet/canopy inhibition plus two-threshold fuel-continuity arid limiter."""
    base=fire_C(d,BASE)
    wet_climate=sig(d['p_ann'],p['wet_k'],p['wet_c'])
    rainy_now=sig(p_rel,p['rain_k'],p['rain_c'])
    rainy_prev=sig(p_rel_prev,p['prev_k'],p['prev_c'])
    wet_inhib=wet_climate*((1-p['prev_weight'])*rainy_now + p['prev_weight']*rainy_prev)
    wet=1-p['wet_amp']*wet_inhib
    deficit=d['dbar']/(d['p_ann']+p['ratio_p0'])
    arid1=1-p['arid_amp1']*sig(deficit,p['arid_k1'],p['arid_c1'])
    arid2=1-p['arid_amp2']*sig(deficit,p['arid_k2'],p['arid_c2'])
    return (base*np.clip(wet*arid1*arid2,0,1)).astype(np.float32)

FAMILIES={'p2_curing_gate':fire_p2_curing_gate,'p2_seasonal_wet':fire_p2_seasonal_wet,'p2_arid_softplus':fire_p2_arid_softplus,'p2_seasonal_wet_arid2':fire_p2_seasonal_wet_arid2}

def predict(family,p):
    rate=FAMILIES[family](drivers,p)*land_mask[None,:,:]
    return ed_transform(rate),rate

def score(pred):
    pred_tm=pred.mean(axis=0)
    bias=float((np.exp(-np.abs(pred_tm-gfed_tm)/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pred_anom=pred-pred_tm[None,:,:]; obs_anom=obs-gfed_tm[None,:,:]
    rmse=float((np.exp(-np.sqrt(((pred_anom-obs_anom)**2).mean(axis=0))/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pred_cyc=pred.reshape(16,12,180,360).mean(axis=0); pred_peak=np.argmax(pred_cyc,axis=0).astype(np.float32)
    shift=pred_peak-gfed_peak_month; shift=np.where(shift>6,shift-12,shift); shift=np.where(shift<-6,shift+12,shift)
    seas=float((((1+np.cos(np.abs(shift)/12*2*np.pi))*0.5)*mass_w_burn).sum()/(mass_w_burn.sum()+1e-12))
    obs_flat=gfed_tm[land_mask]; pred_flat=pred_tm[land_mask]; pw=w2_burn[land_mask]
    ow=(obs_flat*pw).sum()/pw.sum(); mw=(pred_flat*pw).sum()/pw.sum(); oa=obs_flat-ow; pa=pred_flat-mw
    std0=max(float(np.sqrt(((oa**2)*pw).sum()/pw.sum())),1e-12); std=max(float(np.sqrt(((pa**2)*pw).sum()/pw.sum())),1e-12)
    rho=float((pa*oa*pw).sum()/(np.sqrt(((pa**2)*pw).sum()*((oa**2)*pw).sum())+1e-12)); sigma=std/std0
    spatial=2*(1+rho)/((sigma+1/max(sigma,1e-12))**2)
    simple=float(np.mean([bias,rmse,seas,spatial])); tier2=float((2*bias+2*rmse+seas+spatial)/6)
    return {'bias':bias,'rmse':rmse,'seas':seas,'spatial':spatial,'overall_simple':simple,'overall_tier2':tier2}

def suggest(trial,fam):
    if fam=='p2_curing_gate':
        return dict(gate_amp=trial.suggest_float('gate_amp',0,0.9), gate_gamma=trial.suggest_float('gate_gamma',0.2,5,log=True), dry_k=trial.suggest_float('dry_k',1e-5,1e-1,log=True), dry_c=trial.suggest_float('dry_c',1,1e4,log=True), dr_k=trial.suggest_float('dr_k',1e-4,1,log=True), dr_c=trial.suggest_float('dr_c',1e-3,1e3,log=True), pr_k=trial.suggest_float('pr_k',1e-2,1e2,log=True), pr_c=trial.suggest_float('pr_c',0.05,10,log=True))
    if fam=='p2_seasonal_wet':
        return dict(wet_amp=trial.suggest_float('wet_amp',0,0.95), wet_k=trial.suggest_float('wet_k',1e-5,5e-2,log=True), wet_c=trial.suggest_float('wet_c',300,5000,log=True), rain_k=trial.suggest_float('rain_k',1e-2,1e2,log=True), rain_c=trial.suggest_float('rain_c',0.05,10,log=True), prev_k=trial.suggest_float('prev_k',1e-2,1e2,log=True), prev_c=trial.suggest_float('prev_c',0.05,10,log=True), prev_weight=trial.suggest_float('prev_weight',0,1))
    if fam=='p2_arid_softplus':
        return dict(ratio_p0=trial.suggest_float('ratio_p0',1,500,log=True), arid_amp1=trial.suggest_float('arid_amp1',0,0.95), arid_k1=trial.suggest_float('arid_k1',1e-3,10,log=True), arid_c1=trial.suggest_float('arid_c1',0.5,30,log=True), arid_amp2=trial.suggest_float('arid_amp2',0,0.95), arid_k2=trial.suggest_float('arid_k2',1e-3,10,log=True), arid_c2=trial.suggest_float('arid_c2',5,100,log=True))
    if fam=='p2_seasonal_wet_arid2':
        p=dict(wet_amp=trial.suggest_float('wet_amp',0,0.95), wet_k=trial.suggest_float('wet_k',1e-5,5e-2,log=True), wet_c=trial.suggest_float('wet_c',300,5000,log=True), rain_k=trial.suggest_float('rain_k',1e-2,1e2,log=True), rain_c=trial.suggest_float('rain_c',0.05,10,log=True), prev_k=trial.suggest_float('prev_k',1e-2,1e2,log=True), prev_c=trial.suggest_float('prev_c',0.05,10,log=True), prev_weight=trial.suggest_float('prev_weight',0,1))
        p.update(dict(ratio_p0=trial.suggest_float('ratio_p0',1,500,log=True), arid_amp1=trial.suggest_float('arid_amp1',0,0.95), arid_k1=trial.suggest_float('arid_k1',1e-3,10,log=True), arid_c1=trial.suggest_float('arid_c1',0.5,30,log=True), arid_amp2=trial.suggest_float('arid_amp2',0,0.95), arid_k2=trial.suggest_float('arid_k2',1e-3,10,log=True), arid_c2=trial.suggest_float('arid_c2',5,100,log=True)))
        return p
    raise ValueError(fam)

def warm(fam):
    if fam=='p2_curing_gate': return dict(gate_amp=0,gate_gamma=1,dry_k=0.01,dry_c=100,dr_k=0.01,dr_c=1,pr_k=1,pr_c=1)
    if fam=='p2_seasonal_wet': return dict(wet_amp=F3B['wet_amp'],wet_k=F3B['wet_k'],wet_c=F3B['wet_c'],rain_k=1,rain_c=0.01,prev_k=1,prev_c=0.01,prev_weight=0)
    if fam=='p2_arid_softplus': return dict(ratio_p0=F3B['ratio_p0'],arid_amp1=F3B['arid_amp'],arid_k1=F3B['arid_k'],arid_c1=F3B['arid_c'],arid_amp2=0,arid_k2=0.1,arid_c2=20)
    if fam=='p2_seasonal_wet_arid2': return dict(wet_amp=F3B['wet_amp'],wet_k=F3B['wet_k'],wet_c=F3B['wet_c'],rain_k=1,rain_c=0.01,prev_k=1,prev_c=0.01,prev_weight=0,ratio_p0=F3B['ratio_p0'],arid_amp1=F3B['arid_amp'],arid_k1=F3B['arid_k'],arid_c1=F3B['arid_c'],arid_amp2=0,arid_k2=0.1,arid_c2=20)

def objective_factory(fam):
    def obj(trial):
        p=suggest(trial,fam); pred,_=predict(fam,p); s=score(pred)
        penalty=0.0005*len(p)
        return -(s['overall_simple']-penalty)
    return obj

def save_candidate(candidate,fam,p,s,n,runtime,rate):
    obj={'candidate':candidate,'family':fam,'n_trials':n,'runtime_min':runtime,'scores_internal':s,'params':p,'raw_rate_diag':{'land_mean_yr-1':float((rate*w3_land).sum()/(w3_land.sum()+1e-12)),'max_yr-1':float(np.nanmax(rate)),'cap_binding_count':int(((rate>FIRE_MAX_RATE)&land_mask[None,:,:]).sum())}}
    path=RESEARCH_DIR/f'{candidate}.json'; path.write_text(json.dumps(obj,indent=2)); print('[write]',path)

def optimize(args):
    fam=args.family; sampler=optuna.samplers.TPESampler(seed=SEED,multivariate=True,warn_independent_sampling=False)
    study=optuna.create_study(direction='minimize',sampler=sampler); study.enqueue_trial(warm(fam)); t0=time.time(); last=t0
    def cb(st,tr):
        nonlocal last
        if time.time()-last>30:
            print(f'  trial {len(st.trials):4d}/{N_TRIALS} best={-st.best_value:.5f}'); last=time.time()
    print(f'[opt] {fam} {args.candidate} trials={N_TRIALS}')
    study.optimize(objective_factory(fam),n_trials=N_TRIALS,callbacks=[cb])
    p=study.best_params; pred,rate=predict(fam,p); s=score(pred); runtime=(time.time()-t0)/60
    print('[done]',s); save_candidate(args.candidate,fam,p,s,len(study.trials),runtime,rate)

def emit(args):
    cand=json.load(open(RESEARCH_DIR/f'{args.candidate}.json')); pred,rate=predict(cand['family'],cand['params'])
    pred_hd=uncoarsen(np.where(land_mask[None,:,:],pred,np.nan).astype(np.float32))
    times=[cftime.DatetimeNoLeap(y,m,15) for y in YEARS for m in range(1,13)]
    ds=xr.Dataset({'burntArea':(('time','lat','lon'),pred_hd,{'units':'1','standard_name':'burnt_area_fraction','long_name':'Burnt Area Fraction'})},coords={'time':('time',times),'lat':('lat',np.arange(-89.75,90,0.5)),'lon':('lon',np.arange(-179.75,180,0.5))},attrs={'title':f"Pass2 candidate {args.candidate}",'Conventions':'CF-1.7'})
    ds=add_cf_bounds(ds); enc={'burntArea':{'zlib':True,'complevel':4,'_FillValue':1e20},'time':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'},'time_bounds':{'units':'days since 2001-01-01 00:00:00','calendar':'noleap','dtype':'float64'}}
    tmp=OUT_NC.with_suffix('.nc.tmp'); ds.to_netcdf(tmp,encoding=enc,format='NETCDF4_CLASSIC'); os.replace(tmp,OUT_NC)
    (MODELS_DIR/'params.json').write_text(json.dumps({'model':f"Pass2 candidate {args.candidate}: {cand['family']}",'candidate_json':str((RESEARCH_DIR/f'{args.candidate}.json').relative_to(REPO)),'params':cand['params']},indent=2))
    print('[write]',OUT_NC); print('[diag]',score(pred))

def score_current(args):
    pred=ed_transform(f3b_rate(drivers)*land_mask[None,:,:]); print(json.dumps(score(pred),indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('score-current')
    op=sub.add_parser('optimize'); op.add_argument('--family',choices=sorted(FAMILIES),required=True); op.add_argument('--candidate',required=True)
    em=sub.add_parser('emit'); em.add_argument('--candidate',required=True)
    args=ap.parse_args()
    if args.cmd=='score-current': score_current(args)
    elif args.cmd=='optimize': optimize(args)
    elif args.cmd=='emit': emit(args)
if __name__=='__main__': main()
