"""Constrained combo search: Q3 precip-concentration wetness + curing-gated lag.

Only run because Q3 leaves small AUST/SHAF losses while Q2 improves AUST and
seasonality. Q3 wetness parameters are fixed; tune only the small curing-lag
extension. This tests whether Q2 is complementary or dominated.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np, optuna
from search_precip_concentration_wet import REPO, OUTDIR, BASE, drivers, obs, land_mask, N_MONTHS, FIRE_MAX_RATE, sig, supp, hump, score
WINDOWS=[1,2,3,4,6]
Q3=json.loads((REPO/'models'/'C'/'candidate_search'/'precip_concentration_wet_search_500_trials.json').read_text())['best_extra']
N_TRIALS=int(os.environ.get('N_TRIALS','500')); SEED=int(os.environ.get('SEED','41'))
def lag_mean(arr,w): return np.mean([np.roll(arr,lag,axis=0) for lag in range(1,int(w)+1)],axis=0).astype(np.float32)
gpp_lags={w:lag_mean(drivers['gpp_monthly'],w) for w in WINDOWS}
def predict(e):
    p=BASE
    d_gate=sig(drivers['dbar'],e['D_cure_k'],e['D_cure_c']); p_gate=1/(1+np.power(np.clip(drivers['p_month']/(e['P_cure_half']+1e-12),0,1e6),e['P_cure_pow']))
    cure=1-(1-d_gate)*(1-p_gate); a=e['lag_alpha']; lag=gpp_lags[int(e['gpp_lag_window'])]
    gpp=(1-a*cure)*drivers['gpp_monthly']+(a*cure)*lag
    product=sig(drivers['dbar'],p['k1'],p['D_low'])*supp(drivers['dbar'],p['k2'],p['D_high'])*(drivers['p_ann']/(drivers['p_ann']+p['P_half']+1e-12))*(1/(1+drivers['p_month']/(p['pre_dampen_half']+1e-12)))*hump(p['gpp_af']*gpp,p['gpp_b'],p['gpp_d'])*sig(drivers['t_air'],p['ign_k'],p['ign_c'])
    wet=1/(1+np.power(np.clip(drivers['p_ann']/(Q3['P_wet_half']+1e-12),0,1e6),Q3['P_wet_pow']))
    dry=(drivers['p_month']<Q3['dry_month_threshold']).astype(np.float32); dry_frac=np.mean([np.roll(dry,lag,axis=0) for lag in range(0,12)],axis=0).astype(np.float32)
    season=sig(dry_frac,Q3['dryfrac_k'],Q3['dryfrac_c']); ds=sig(drivers['dbar'],Q3['D_support_k'],Q3['D_support_c']); dw=Q3['d_support_weight']; relief=season*((1-dw)+dw*ds)
    wet_mult=1-Q3['wet_strength']*(1-wet)*(1-Q3['relief_strength']*relief)
    product*=np.clip(wet_mult,0,2)
    rate=np.power(np.clip(product,0,None),p['fire_exp']).astype(np.float32)*land_mask[None,:,:]
    return ((1-np.exp(-np.minimum(rate,FIRE_MAX_RATE)))/12).astype(np.float32)
def objective(trial):
    e={'family':'precip_conc_wet_plus_curing_lag',**Q3,'gpp_lag_window':trial.suggest_categorical('gpp_lag_window',WINDOWS),'lag_alpha':trial.suggest_float('lag_alpha',0,0.6),'D_cure_k':trial.suggest_float('D_cure_k',1e-4,1e-1,log=True),'D_cure_c':trial.suggest_float('D_cure_c',10,2000,log=True),'P_cure_half':trial.suggest_float('P_cure_half',0.1,50,log=True),'P_cure_pow':trial.suggest_float('P_cure_pow',0.5,5)}
    pred=predict(e); overall,br=score(pred)
    for k,v in br.items(): trial.set_user_attr(k,v)
    trial.set_user_attr('extra',e); return overall

def main():
    base={**Q3,'family':'precip_conc_wet_plus_curing_lag','gpp_lag_window':1,'lag_alpha':0,'D_cure_k':0.01,'D_cure_c':100,'P_cure_half':5,'P_cure_pow':2}
    _,base_br=score(predict(base)); print('[Q3 fixed proxy]',base_br)
    sampler=optuna.samplers.TPESampler(seed=SEED,multivariate=True,group=True); study=optuna.create_study(direction='maximize',sampler=sampler)
    study.enqueue_trial({'gpp_lag_window':1,'lag_alpha':0.1,'D_cure_k':0.024,'D_cure_c':289,'P_cure_half':0.45,'P_cure_pow':3.3})
    t0=time.time(); study.optimize(objective,n_trials=N_TRIALS)
    best=study.best_trial; res={'name':'PRECIP-CONC-WET-CURING-LAG-v1','n_trials':len(study.trials),'seed':SEED,'q3_fixed_proxy':base_br,'best_proxy_scores':{k:best.user_attrs[k] for k in ['bias','rmse','seasonal','spatial','overall']},'best_extra':best.user_attrs['extra'],'best_params':best.params,'runtime_min':round((time.time()-t0)/60,3),'physical_hypothesis':'Curing-gated lag may restore AUST/seasonality on top of precipitation-concentration wetness relief; fixed Q3 wetness tests complementarity without opening a broad black-box search.'}
    out=OUTDIR/f"precip_conc_wet_curing_lag_search_{N_TRIALS}_trials.json"; out.write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2)); print('[write]',out)
if __name__=='__main__': main()
