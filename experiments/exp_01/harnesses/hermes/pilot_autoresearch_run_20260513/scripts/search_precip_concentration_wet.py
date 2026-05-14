"""Round 2 Q3 search: precipitation-concentration wetness relief.

Physical hypothesis:
Q1 used current-month dry relief and improved the wetness/savanna distinction,
but still harmed SHAF/AUST and Spatial. A more annual-scale dry-season contrast
may distinguish perhumid forests from seasonal savannas better than a single
month. Use trailing-12-month dry-month fraction from allowed P_month only.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np
import optuna
from reproduce_modelC import load_drivers, load_gfed_1deg
REPO=Path(__file__).resolve().parents[1]; OUTDIR=REPO/'models'/'C'/'candidate_search'; OUTDIR.mkdir(parents=True,exist_ok=True)
N_TRIALS=int(os.environ.get('N_TRIALS','500')); SEED=int(os.environ.get('SEED','37')); FIRE_MAX_RATE=float(os.environ.get('FIRE_MAX_RATE','5.0'))
BASE=json.loads((REPO/'models'/'C'/'params.json').read_text())['params']; drivers=load_drivers(); obs=load_gfed_1deg().astype(np.float32)
land_mask=(obs>0).any(axis=0); N_MONTHS=obs.shape[0]
lat_1=np.arange(-89.5,90.0,1.0).astype(np.float32); cos_lat=np.cos(np.deg2rad(lat_1)).astype(np.float64); w2=np.broadcast_to(cos_lat[:,None],(180,360)).astype(np.float64)
gfed_tm=obs.mean(axis=0).astype(np.float64); gfed_std=obs.std(axis=0).clip(1e-12).astype(np.float64); gfed_cyc=obs.reshape(16,12,180,360).mean(axis=0); gfed_peak_month=np.argmax(gfed_cyc,axis=0).astype(np.float32)
mass_w=(w2*gfed_tm).astype(np.float64); mass_w_burn=mass_w*land_mask; w2_burn=w2*land_mask

def sig(x,k,c): return 1/(1+np.exp(np.clip(-k*(x-c),-50,50)))
def supp(x,k,c): return 1/(1+np.exp(np.clip(k*(x-c),-50,50)))
def hump(x,b,dec):
    b=max(float(b),1e-9); dec=max(float(dec),1e-9); return (1-np.exp(-np.clip(x/b,0,500)))*np.exp(-np.clip(x/dec,0,500))

def dry_fraction(thr):
    dry=(drivers['p_month']<thr).astype(np.float32)
    return np.mean([np.roll(dry,lag,axis=0) for lag in range(0,12)],axis=0).astype(np.float32)

def predict(extra):
    p=BASE
    onset=sig(drivers['dbar'],p['k1'],p['D_low']); dry_suppress=supp(drivers['dbar'],p['k2'],p['D_high'])
    p_floor=drivers['p_ann']/(drivers['p_ann']+p['P_half']+1e-12); p_damp=1/(1+drivers['p_month']/(p['pre_dampen_half']+1e-12))
    gpp_mod=hump(p['gpp_af']*drivers['gpp_monthly'],p['gpp_b'],p['gpp_d']); ign_mod=sig(drivers['t_air'],p['ign_k'],p['ign_c'])
    product=onset*dry_suppress*p_floor*p_damp*gpp_mod*ign_mod
    wet=1/(1+np.power(np.clip(drivers['p_ann']/(extra['P_wet_half']+1e-12),0,1e6),extra['P_wet_pow']))
    df=dry_fraction(extra['dry_month_threshold'])
    season_gate=sig(df, extra['dryfrac_k'], extra['dryfrac_c'])
    # Optional Dbar support: annual dry season only relieves if it actually accumulates dryness.
    d_support=sig(drivers['dbar'], extra['D_support_k'], extra['D_support_c'])
    relief=season_gate*((1-extra['d_support_weight'])+extra['d_support_weight']*d_support)
    wet_mult=1-extra['wet_strength']*(1-wet)*(1-extra['relief_strength']*relief)
    product=product*np.clip(wet_mult,0,2)
    rate=np.power(np.clip(product,0,None),p['fire_exp']).astype(np.float32)*land_mask[None,:,:]
    return ((1-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12).astype(np.float32)

def score(pred):
    pred_tm=pred.mean(axis=0).astype(np.float64); bias=float((np.exp(-np.abs(pred_tm-gfed_tm)/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    crmse=np.sqrt((((pred-pred_tm[None,:,:])-(obs-gfed_tm[None,:,:]))**2).mean(axis=0)); rmse=float((np.exp(-crmse/gfed_std)*mass_w).sum()/(mass_w.sum()+1e-12))
    pc=pred.reshape(16,12,180,360).mean(axis=0); shift=np.argmax(pc,axis=0).astype(np.float32)-gfed_peak_month; shift=np.where(shift>6,shift-12,shift); shift=np.where(shift<-6,shift+12,shift)
    seas=float((((1+np.cos(np.abs(shift)/12*2*np.pi))*0.5)*mass_w_burn).sum()/(mass_w_burn.sum()+1e-12))
    of=gfed_tm[land_mask]; pf=pred_tm[land_mask]; pw=w2_burn[land_mask]; ow=(of*pw).sum()/pw.sum(); pm=(pf*pw).sum()/pw.sum(); oa=of-ow; pa=pf-pm
    std0=max(float(np.sqrt(((oa**2)*pw).sum()/pw.sum())),1e-12); std=max(float(np.sqrt(((pa**2)*pw).sum()/pw.sum())),1e-12); rho=float((pa*oa*pw).sum()/(np.sqrt(((pa**2)*pw).sum()*((oa**2)*pw).sum())+1e-12)); sigma=std/std0; spatial=float(2*(1+rho)/((sigma+1/max(sigma,1e-12))**2))
    overall=float((2*bias+2*rmse+seas+spatial)/6); return overall,{'bias':bias,'rmse':rmse,'seasonal':seas,'spatial':spatial,'overall':overall}

def objective(trial):
    e={'family':'precip_concentration_wet_relief','wet_strength':trial.suggest_float('wet_strength',0.3,1.0),'P_wet_half':trial.suggest_float('P_wet_half',1000,5000,log=True),'P_wet_pow':trial.suggest_float('P_wet_pow',1,5),'relief_strength':trial.suggest_float('relief_strength',0,1),'dry_month_threshold':trial.suggest_float('dry_month_threshold',1,80,log=True),'dryfrac_k':trial.suggest_float('dryfrac_k',1,25),'dryfrac_c':trial.suggest_float('dryfrac_c',0.05,0.85),'D_support_k':trial.suggest_float('D_support_k',1e-4,1e-1,log=True),'D_support_c':trial.suggest_float('D_support_c',10,2000,log=True),'d_support_weight':trial.suggest_float('d_support_weight',0,1)}
    pred=predict(e); overall,br=score(pred)
    for k,v in br.items(): trial.set_user_attr(k,v)
    trial.set_user_attr('extra',e); return overall

def main():
    base={'family':'precip_concentration_wet_relief','wet_strength':0,'P_wet_half':2000,'P_wet_pow':4,'relief_strength':0,'dry_month_threshold':10,'dryfrac_k':5,'dryfrac_c':0.3,'D_support_k':0.01,'D_support_c':100,'d_support_weight':0}
    _,base_br=score(predict(base)); print('[baseline proxy]',base_br)
    sampler=optuna.samplers.TPESampler(seed=SEED,multivariate=True,group=True); study=optuna.create_study(direction='maximize',sampler=sampler)
    study.enqueue_trial({'wet_strength':0.9254714800690381,'P_wet_half':2034.9510173025635,'P_wet_pow':4.951654707160729,'relief_strength':0.36,'dry_month_threshold':10,'dryfrac_k':8,'dryfrac_c':0.25,'D_support_k':0.005,'D_support_c':1000,'d_support_weight':0.5})
    t0=time.time(); last=t0
    def cb(st,tr):
        nonlocal last
        if time.time()-last>30:
            print(f"[progress] {len(st.trials)}/{N_TRIALS} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f} min"); last=time.time()
    study.optimize(objective,n_trials=N_TRIALS,callbacks=[cb]); best=study.best_trial
    result={'name':'PRECIP-CONC-WET-v1','n_trials':len(study.trials),'seed':SEED,'baseline_proxy':base_br,'best_proxy_scores':{k:best.user_attrs[k] for k in ['bias','rmse','seasonal','spatial','overall']},'best_extra':best.user_attrs['extra'],'best_params':best.params,'runtime_min':round((time.time()-t0)/60,3),'physical_hypothesis':'Trailing-12 dry-month fraction distinguishes seasonal savannas from perhumid wet forests and should relieve annual wetness suppression only where dry-season contrast is strong.','constraint_note':'Formula uses only allowed P_month/P_ann plus existing Model C inputs; no region/coordinate/cell routing.'}
    out=OUTDIR/f"precip_concentration_wet_search_{N_TRIALS}_trials.json"; out.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2)); print('[write]',out)
if __name__=='__main__': main()
