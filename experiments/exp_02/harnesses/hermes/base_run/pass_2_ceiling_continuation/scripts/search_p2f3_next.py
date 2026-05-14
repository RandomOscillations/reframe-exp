#!/usr/bin/env python3
"""Next continuation from P2F3 best-so-far.

Explores unified global mechanisms targeted at P2F3 failures:
- BONA spatial degradation: relax/attenuate suppressors in cold continental regimes using T_air-derived gates.
- AUST seasonality: curing/drying phase gate using dbar tendency + current-month precipitation concentration.
- Weak-region spatial: keep P2F3 wet-canopy + arid fuel-continuity core.

No region/lat/cell features are used in formulas. Regional failures only motivate global physical gates.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import optuna
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_candidates as rc
from reproduce_modelC import sig

BASE=rc.BASE.copy(); OUTROOT=Path('runs/candidates')
P2F3={
 'wet_amp':0.8844066447148519,'wet_k':0.03746225268483959,'wet_c':1733.7962048788854,
 'ratio_p0':10.550923117584711,
 'arid_amp1':0.09765875631019073,'arid_k1':8.862392037192233,'arid_c1':0.8190773026156323,
 'arid_amp2':0.872802820380493,'arid_k2':1.2991349033470558,'arid_c2':5.00184048998816,
}
prod0=rc.base_product(BASE).astype(np.float32)
base_rate=np.power(np.clip(prod0,0,None), BASE['fire_exp']).astype(np.float32)
P=rc.ann_p.astype(np.float32); D=rc.dbar.astype(np.float32); T=rc.tair.astype(np.float32); PM=rc.mon_p.astype(np.float32)
tclim=T.reshape(16,12,180,360).mean(axis=0).astype(np.float32)
t_ann=np.broadcast_to(tclim.mean(axis=0, keepdims=True), T.shape).astype(np.float32)
t_amp=np.broadcast_to((tclim.max(axis=0)-tclim.min(axis=0))[None,:,:], T.shape).astype(np.float32)
# previous-month dbar tendency, only past/current state conceptually
dD=np.empty_like(D); dD[0]=0; dD[1:]=D[1:]-D[:-1]
p_conc=np.clip(PM/(P/12.0+1e-6),0,50).astype(np.float32)

def p2f3_mod(p=P2F3):
    wet=1-p['wet_amp']*sig(P,p['wet_k'],p['wet_c'])
    ratio=D/(P+p['ratio_p0'])
    a1=1-p['arid_amp1']*sig(ratio,p['arid_k1'],p['arid_c1'])
    a2=1-p['arid_amp2']*sig(ratio,p['arid_k2'],p['arid_c2'])
    return np.clip(wet*a1*a2,0,1).astype(np.float32)
P2MOD=p2f3_mod()
P2RATE=(base_rate*P2MOD*rc.land_mask[None,:,:]).astype(np.float32)

def ed(rate): return rc.ed_transform(rate*rc.land_mask[None,:,:])

def predict(family,p):
    ratio=D/(P+P2F3['ratio_p0'])
    wet=1-P2F3['wet_amp']*sig(P,P2F3['wet_k'],P2F3['wet_c'])
    a2=1-P2F3['arid_amp2']*sig(ratio,P2F3['arid_k2'],P2F3['arid_c2'])
    if family=='low_arid_warm_gate':
        # Attenuate the low/soft semi-arid threshold in cold regimes to recover BONA,
        # while retaining it in warm dryland weak regions (TENA/MIDE/EURO warm margins).
        warm=sig(t_ann,p['warm_k'],p['warm_c'])
        low_eff=p['floor']+(1-p['floor'])*warm
        a1=1-P2F3['arid_amp1']*low_eff*sig(ratio,P2F3['arid_k1'],P2F3['arid_c1'])
        mod=np.clip(wet*a1*a2,0,1)
        return ed(base_rate*mod)
    if family=='cold_continental_relax':
        # Restore a fraction of P2F3 suppression in cold, high-seasonality climates.
        # This targets boreal spatial over-suppression without using geography.
        cold=1-sig(t_ann,p['cold_k'],p['cold_c'])
        cont=sig(t_amp,p['amp_k'],p['amp_c'])
        relax=np.clip(p['relax_amp']*cold*cont,0,1)
        mod=np.clip(P2MOD + (1-P2MOD)*relax,0,1)
        return ed(base_rate*mod)
    if family=='curing_phase':
        # Fire spread/seasonality enhanced during active drying and below-normal rainfall.
        drying=sig(dD,p['drying_k'],p['drying_c'])
        drymonth=1/(1+np.power(np.clip(p_conc/p['pconc_half'],0,50),p['pconc_pow']))
        warm=sig(T,p['temp_k'],p['temp_c'])
        cure=drying*drymonth*warm
        # bounded enhancement; P2F3 suppressors remain the structural constraints
        rate=P2RATE*(1+p['cure_amp']*cure)
        return ed(rate)
    if family=='curing_with_wet_comp':
        drying=sig(dD,p['drying_k'],p['drying_c'])
        drymonth=1/(1+np.power(np.clip(p_conc/p['pconc_half'],0,50),p['pconc_pow']))
        wetmonth=sig(p_conc,p['wet_k'],p['wet_c'])
        warm=sig(T,p['temp_k'],p['temp_c'])
        mult=np.clip((1+p['cure_amp']*drying*drymonth*warm)*(1-p['wet_amp']*wetmonth),0,2)
        return ed(P2RATE*mult)
    raise ValueError(family)

def score_pred(pred): return rc.score(pred)

def suggest(trial,family):
    if family=='low_arid_warm_gate':
        return {'warm_k':trial.suggest_float('warm_k',0.05,2,log=True),'warm_c':trial.suggest_float('warm_c',-5,25),'floor':trial.suggest_float('floor',0,1)}
    if family=='cold_continental_relax':
        return {'cold_k':trial.suggest_float('cold_k',0.05,2,log=True),'cold_c':trial.suggest_float('cold_c',-10,15),'amp_k':trial.suggest_float('amp_k',0.05,2,log=True),'amp_c':trial.suggest_float('amp_c',5,35),'relax_amp':trial.suggest_float('relax_amp',0,0.6)}
    if family=='curing_phase':
        return {'drying_k':trial.suggest_float('drying_k',0.001,0.2,log=True),'drying_c':trial.suggest_float('drying_c',-20,80),'pconc_half':trial.suggest_float('pconc_half',0.2,3,log=True),'pconc_pow':trial.suggest_float('pconc_pow',0.5,4),'temp_k':trial.suggest_float('temp_k',0.05,2,log=True),'temp_c':trial.suggest_float('temp_c',0,35),'cure_amp':trial.suggest_float('cure_amp',0,1.5)}
    if family=='curing_with_wet_comp':
        p=suggest(trial,'curing_phase')
        p.update({'wet_k':trial.suggest_float('wet_k',0.2,3,log=True),'wet_c':trial.suggest_float('wet_c',0.5,5),'wet_amp':trial.suggest_float('wet_amp',0,0.7)})
        return p
    raise ValueError(family)

def objective(family,p):
    pred=predict(family,p); sc=score_pred(pred)
    # Proxy BONA/BOAS exact regional not in fast scorer; protect global spatial and avoid tiny overfit.
    return sc['overall'] - 0.04*max(0,0.765-sc['spatial'])

def emit(name,family,p,note,n_trials=0):
    pred=predict(family,p); sc=score_pred(pred)
    out=OUTROOT/name; out.mkdir(parents=True,exist_ok=True); rc.write_nc(pred,out)
    meta={'family':family,'name':name,'search':note,'n_trials':n_trials,'fast_score':sc,'params':p,'p2f3_params':P2F3,'constraint_note':'single global formula using allowed P/T/Dbar/GPP-derived quantities; no region/lat/cell routing'}
    (out/'params.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta,indent=2)); return sc

def run_family(family,trials,seed):
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler=optuna.samplers.TPESampler(seed=seed,multivariate=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    # neutral or known plausible warm starts
    if family=='low_arid_warm_gate':
        study.enqueue_trial({'warm_k':0.5,'warm_c':5,'floor':1.0})
        study.enqueue_trial({'warm_k':0.5,'warm_c':8,'floor':0.0})
        study.enqueue_trial({'warm_k':0.25,'warm_c':2,'floor':0.3})
    elif family=='cold_continental_relax':
        study.enqueue_trial({'cold_k':0.5,'cold_c':5,'amp_k':0.3,'amp_c':15,'relax_amp':0.0})
        study.enqueue_trial({'cold_k':0.5,'cold_c':5,'amp_k':0.3,'amp_c':15,'relax_amp':0.2})
    elif family=='curing_phase':
        study.enqueue_trial({'drying_k':0.02,'drying_c':0,'pconc_half':1,'pconc_pow':2,'temp_k':0.5,'temp_c':15,'cure_amp':0.0})
        study.enqueue_trial({'drying_k':0.02,'drying_c':0,'pconc_half':1,'pconc_pow':2,'temp_k':0.5,'temp_c':15,'cure_amp':0.5})
    elif family=='curing_with_wet_comp':
        study.enqueue_trial({'drying_k':0.02,'drying_c':0,'pconc_half':1,'pconc_pow':2,'temp_k':0.5,'temp_c':15,'cure_amp':0.3,'wet_k':1,'wet_c':2,'wet_amp':0.1})
    t0=time.time()
    study.optimize(lambda tr: objective(family,suggest(tr,family)),n_trials=trials,show_progress_bar=False)
    print('family',family,'trials',len(study.trials),'runtime_min',(time.time()-t0)/60,'best',study.best_value)
    return study.best_params,len(study.trials)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--trials',type=int,default=700); args=ap.parse_args()
    # Emit current best baseline under this script for proxy reference.
    emit('p2f3_reference_next','low_arid_warm_gate',{'warm_k':0.5,'warm_c':5,'floor':1.0},'P2F3 reference emitted via equivalent low-threshold floor=1',0)
    for i,fam in enumerate(['low_arid_warm_gate','cold_continental_relax','curing_phase','curing_with_wet_comp'],1):
        p,n=run_family(fam,args.trials,300+i)
        emit(f'next_{fam}_opt{args.trials}',fam,p,f'{args.trials}-trial Optuna from P2F3 failure-directed family',n)
    # Deterministic ablations around promising structural ideas.
    emit('next_low_arid_no_low','low_arid_warm_gate',{'warm_k':0.5,'warm_c':5,'floor':0.0},'ablation-like: low arid threshold only in warm regimes, no cold floor',0)
    emit('next_boreal_relax_strong','cold_continental_relax',{'cold_k':0.5,'cold_c':5,'amp_k':0.3,'amp_c':15,'relax_amp':0.25},'deterministic boreal relax diagnostic',0)

if __name__=='__main__': main()
