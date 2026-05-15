#!/usr/bin/env python3
"""Continuation after ED-next-curing-hotwet-1.

Mechanism families are global and use only allowed P/T/Dbar/GPP-derived inputs:
1. boreal_protected_wetcomp: keep high-scalar wet compensation where useful, but
   attenuate it in cold/high-temperature-amplitude climates to avoid BONA/BOAS collapse.
2. arid_curing_attenuation: reduce curing enhancement in extreme deficit regimes,
   seeking to restore MIDE/CEAM dryland behavior while retaining AUST/Africa gains.
3. wet_productivity_curing_attenuation: reduce curing enhancement in productive/wet
   regimes where broad curing over-amplifies South America / wet tropics.

No region, latitude/longitude, cell tables, or residual corrections.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np, optuna
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
HOT={
 'drying_k':0.151909755193002,'drying_c':71.10327035972242,
 'pconc_half':0.17733668059544083,'pconc_pow':3.6607083389419017,
 'temp_k':0.5483001798421393,'temp_c':6.554353498957058,
 'cure_amp':1.5049730144952744,
 'wet_k':1.9603357957179453,'wet_c':0.6295980601621034,
 'wet_amp':0.65,'warm_k':0.5,'warm_c':8.0,'warm_floor':0.0,
}
prod0=rc.base_product(BASE).astype(np.float32)
base_rate=np.power(np.clip(prod0,0,None), BASE['fire_exp']).astype(np.float32)
P=rc.ann_p.astype(np.float32); D=rc.dbar.astype(np.float32); T=rc.tair.astype(np.float32); PM=rc.mon_p.astype(np.float32)
gpp=rc.G.astype(np.float32)
tclim=T.reshape(16,12,180,360).mean(axis=0).astype(np.float32)
t_ann=np.broadcast_to(tclim.mean(axis=0, keepdims=True), T.shape).astype(np.float32)
t_amp=np.broadcast_to((tclim.max(axis=0)-tclim.min(axis=0))[None,:,:], T.shape).astype(np.float32)
dD=np.empty_like(D); dD[0]=0; dD[1:]=D[1:]-D[:-1]
p_conc=np.clip(PM/(P/12.0+1e-6),0,50).astype(np.float32)

def p2f3_rate():
    wet=1-P2F3['wet_amp']*sig(P,P2F3['wet_k'],P2F3['wet_c'])
    ratio=D/(P+P2F3['ratio_p0'])
    a1=1-P2F3['arid_amp1']*sig(ratio,P2F3['arid_k1'],P2F3['arid_c1'])
    a2=1-P2F3['arid_amp2']*sig(ratio,P2F3['arid_k2'],P2F3['arid_c2'])
    return (base_rate*np.clip(wet*a1*a2,0,1)*rc.land_mask[None,:,:]).astype(np.float32)
P2RATE=p2f3_rate()
ratio=D/(P+P2F3['ratio_p0'])

def components(p):
    drying=sig(dD,p['drying_k'],p['drying_c'])
    drymonth=1/(1+np.power(np.clip(p_conc/p['pconc_half'],0,50),p['pconc_pow']))
    warm_month=sig(T,p['temp_k'],p['temp_c'])
    wetmonth=sig(p_conc,p['wet_k'],p['wet_c'])
    warm_clim=sig(t_ann,p['warm_k'],p['warm_c'])
    return drying,drymonth,warm_month,wetmonth,warm_clim

def ed(rate): return rc.ed_transform(rate*rc.land_mask[None,:,:])

def predict(family,p):
    pp=HOT.copy(); pp.update(p)
    drying,drymonth,warm_month,wetmonth,warm_clim=components(pp)
    cure=drying*drymonth*warm_month
    if family=='base_hotwet':
        wet_gate=pp['warm_floor']+(1-pp['warm_floor'])*warm_clim
        mult=(1+pp['cure_amp']*cure)*(1-pp['wet_amp']*wetmonth*wet_gate)
    elif family=='boreal_protected_wetcomp':
        # Start from high-scalar wet compensation but remove it in cold continental regimes.
        cold=1-sig(t_ann,pp['cold_k'],pp['cold_c'])
        cont=sig(t_amp,pp['amp_k'],pp['amp_c'])
        protect=np.clip(pp['protect_amp']*cold*cont,0,1)
        wet_gate=pp['warm_floor']+(1-pp['warm_floor'])*warm_clim
        wet_eff=wetmonth*wet_gate*(1-protect)
        mult=(1+pp['cure_amp']*cure)*(1-pp['wet_amp']*wet_eff)
    elif family=='arid_curing_attenuation':
        arid=sig(ratio,pp['arid_k'],pp['arid_c'])
        cure_eff=cure*(1-pp['arid_att']*arid)
        wet_gate=pp['warm_floor']+(1-pp['warm_floor'])*warm_clim
        mult=(1+pp['cure_amp']*cure_eff)*(1-pp['wet_amp']*wetmonth*wet_gate)
    elif family=='wet_productivity_curing_attenuation':
        wetclim=sig(P,pp['pann_k'],pp['pann_c'])
        gpphi=sig(gpp,pp['gpp_k'],pp['gpp_c'])
        att=np.clip(pp['prod_att']*wetclim*gpphi,0,1)
        cure_eff=cure*(1-att)
        wet_gate=pp['warm_floor']+(1-pp['warm_floor'])*warm_clim
        mult=(1+pp['cure_amp']*cure_eff)*(1-pp['wet_amp']*wetmonth*wet_gate)
    elif family=='combined_protect_attenuate':
        cold=1-sig(t_ann,pp['cold_k'],pp['cold_c']); cont=sig(t_amp,pp['amp_k'],pp['amp_c'])
        protect=np.clip(pp['protect_amp']*cold*cont,0,1)
        arid=sig(ratio,pp['arid_k'],pp['arid_c'])
        wetclim=sig(P,pp['pann_k'],pp['pann_c'])
        cure_eff=cure*(1-pp['arid_att']*arid)*(1-pp['wet_att']*wetclim)
        wet_gate=pp['warm_floor']+(1-pp['warm_floor'])*warm_clim
        wet_eff=wetmonth*wet_gate*(1-protect)
        mult=(1+pp['cure_amp']*cure_eff)*(1-pp['wet_amp']*wet_eff)
    else:
        raise ValueError(family)
    return ed(np.clip(P2RATE*mult,0,None))

def score(p,family): return rc.score(predict(family,p))

def suggest(trial,family):
    p={}
    # allow moderate retuning around hotwet for all families
    p['cure_amp']=trial.suggest_float('cure_amp',0.5,2.2)
    p['wet_amp']=trial.suggest_float('wet_amp',0.2,0.8)
    p['warm_k']=trial.suggest_float('warm_k',0.1,1.5,log=True)
    p['warm_c']=trial.suggest_float('warm_c',0,18)
    p['warm_floor']=trial.suggest_float('warm_floor',0,1)
    if family in ('boreal_protected_wetcomp','combined_protect_attenuate'):
        p.update({'cold_k':trial.suggest_float('cold_k',0.1,2,log=True),'cold_c':trial.suggest_float('cold_c',-5,12),'amp_k':trial.suggest_float('amp_k',0.1,2,log=True),'amp_c':trial.suggest_float('amp_c',10,35),'protect_amp':trial.suggest_float('protect_amp',0,1)})
    if family in ('arid_curing_attenuation','combined_protect_attenuate'):
        p.update({'arid_k':trial.suggest_float('arid_k',0.2,8,log=True),'arid_c':trial.suggest_float('arid_c',0.5,8),'arid_att':trial.suggest_float('arid_att',0,1)})
    if family=='wet_productivity_curing_attenuation':
        p.update({'pann_k':trial.suggest_float('pann_k',0.002,0.08,log=True),'pann_c':trial.suggest_float('pann_c',500,2500),'gpp_k':trial.suggest_float('gpp_k',0.002,0.1,log=True),'gpp_c':trial.suggest_float('gpp_c',20,300),'prod_att':trial.suggest_float('prod_att',0,1)})
    if family=='combined_protect_attenuate':
        p.update({'pann_k':trial.suggest_float('pann_k',0.002,0.08,log=True),'pann_c':trial.suggest_float('pann_c',500,2500),'wet_att':trial.suggest_float('wet_att',0,1)})
    return p

def objective(family,p):
    sc=score(p,family)
    # Screening only: prefer global + spatial, discourage known BONA/BOAS collapse through spatial penalty.
    return sc['overall'] + 0.04*(sc['spatial']-0.787) - 0.08*max(0,0.79-sc['spatial'])

def run_family(family,trials,seed):
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=seed,multivariate=True))
    if family=='boreal_protected_wetcomp':
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.6870145681883499,'warm_k':0.3505191473516711,'warm_c':1.0746987182178573,'warm_floor':1.0,'cold_k':0.5,'cold_c':5,'amp_k':0.4,'amp_c':18,'protect_amp':0.8})
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'cold_k':0.5,'cold_c':5,'amp_k':0.4,'amp_c':18,'protect_amp':0.0})
    elif family=='arid_curing_attenuation':
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'arid_k':1.5,'arid_c':2.5,'arid_att':0.0})
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'arid_k':1.5,'arid_c':2.5,'arid_att':0.6})
    elif family=='wet_productivity_curing_attenuation':
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'pann_k':0.02,'pann_c':1500,'gpp_k':0.02,'gpp_c':100,'prod_att':0.0})
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'pann_k':0.02,'pann_c':1500,'gpp_k':0.02,'gpp_c':100,'prod_att':0.6})
    elif family=='combined_protect_attenuate':
        study.enqueue_trial({'cure_amp':1.5049730144952744,'wet_amp':0.65,'warm_k':0.5,'warm_c':8,'warm_floor':0.0,'cold_k':0.5,'cold_c':5,'amp_k':0.4,'amp_c':18,'protect_amp':0.3,'arid_k':1.5,'arid_c':2.5,'arid_att':0.2,'pann_k':0.02,'pann_c':1500,'wet_att':0.2})
    t0=time.time(); study.optimize(lambda tr: objective(family,suggest(tr,family)),n_trials=trials,show_progress_bar=False)
    print('family',family,'trials',len(study.trials),'runtime_min',(time.time()-t0)/60,'best',study.best_value,'params',study.best_params)
    return study.best_params,len(study.trials)

def emit(name,family,p,note,n_trials=0):
    pred=predict(family,p); sc=rc.score(pred)
    out=OUTROOT/name; out.mkdir(parents=True,exist_ok=True); rc.write_nc(pred,out)
    meta={'family':family,'name':name,'search':note,'n_trials':n_trials,'fast_score':sc,'params':p,'hotwet_base_params':HOT,'p2f3_params':P2F3,'constraint_note':'single global formula using allowed P/T/Dbar/GPP-derived quantities; no region/lat/cell routing'}
    (out/'params.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta,indent=2)); return sc

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--trials',type=int,default=500); args=ap.parse_args()
    emit('hotwet_reference_loop13','base_hotwet',{},'reference ED-next-curing-hotwet-1 implementation',0)
    for i,fam in enumerate(['boreal_protected_wetcomp','arid_curing_attenuation','wet_productivity_curing_attenuation','combined_protect_attenuate'],1):
        p,n=run_family(fam,args.trials,700+i)
        emit(f'loop13_{fam}_opt{args.trials}',fam,p,f'{args.trials}-trial Optuna continuation after hotwet-1',n)
    # deterministic scientific ablations around high-scalar no-warmgate with boreal protection
    emit('loop13_boreal_protect_no_warmgate_diag','boreal_protected_wetcomp',{'cure_amp':1.5049730144952744,'wet_amp':0.6870145681883499,'warm_k':0.3505191473516711,'warm_c':1.0746987182178573,'warm_floor':1.0,'cold_k':0.5,'cold_c':5,'amp_k':0.4,'amp_c':18,'protect_amp':0.8},'diagnostic: rejected high-scalar wet comp with boreal protection',0)

if __name__=='__main__': main()
