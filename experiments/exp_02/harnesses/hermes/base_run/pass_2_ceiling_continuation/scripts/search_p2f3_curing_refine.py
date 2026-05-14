#!/usr/bin/env python3
"""Refine P2F3 curing-phase candidate after official regional diagnostics.

Signal:
- curing_phase: big global gain and AUST/NHAF/SHAF gains, BONA/BOAS mostly preserved,
  but dryland/wet weak regions partly regress vs P2F3.
- curing_with_wet_comp: larger global gain but BONA/BOAS spatial damage.

New family: keep curing-phase enhancement, but make wet-month compensation apply mainly
in warm regimes so cold/continental BONA/BOAS are protected. All gates use allowed T/P/Dbar.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, optuna
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_p2f3_next as s
import research_candidates as rc
from reproduce_modelC import sig
OUTROOT=Path('runs/candidates')

def pred_warmwet(p):
    drying=sig(s.dD,p['drying_k'],p['drying_c'])
    drymonth=1/(1+np.power(np.clip(s.p_conc/p['pconc_half'],0,50),p['pconc_pow']))
    warm_month=sig(s.T,p['temp_k'],p['temp_c'])
    cure=drying*drymonth*warm_month
    wetmonth=sig(s.p_conc,p['wet_k'],p['wet_c'])
    warm_clim=sig(s.t_ann,p['warm_k'],p['warm_c'])
    wet_supp=wetmonth*(p['warm_floor']+(1-p['warm_floor'])*warm_clim)
    mult=np.clip((1+p['cure_amp']*cure)*(1-p['wet_amp']*wet_supp),0,2)
    return s.ed(s.P2RATE*mult)

def score(p): return rc.score(pred_warmwet(p))

def suggest(trial):
    return {
      'drying_k':trial.suggest_float('drying_k',0.005,0.25,log=True),
      'drying_c':trial.suggest_float('drying_c',20,100),
      'pconc_half':trial.suggest_float('pconc_half',0.15,1.5,log=True),
      'pconc_pow':trial.suggest_float('pconc_pow',1,5),
      'temp_k':trial.suggest_float('temp_k',0.05,2,log=True),
      'temp_c':trial.suggest_float('temp_c',0,20),
      'cure_amp':trial.suggest_float('cure_amp',0,1.8),
      'wet_k':trial.suggest_float('wet_k',0.2,3,log=True),
      'wet_c':trial.suggest_float('wet_c',0.5,5),
      'wet_amp':trial.suggest_float('wet_amp',0,0.7),
      'warm_k':trial.suggest_float('warm_k',0.05,2,log=True),
      'warm_c':trial.suggest_float('warm_c',-5,25),
      'warm_floor':trial.suggest_float('warm_floor',0,1),
    }

def emit(name,p,note,n_trials=0):
    pred=pred_warmwet(p); sc=rc.score(pred); out=OUTROOT/name; out.mkdir(parents=True,exist_ok=True); rc.write_nc(pred,out)
    meta={'family':'curing_phase_with_warm_gated_wet_comp','name':name,'search':note,'n_trials':n_trials,'fast_score':sc,'params':p,'p2f3_params':s.P2F3,'constraint_note':'single global formula: dbar tendency + precipitation concentration + T_air warm gate; no region/lat/cell routing'}
    (out/'params.json').write_text(json.dumps(meta,indent=2)); print(json.dumps(meta,indent=2)); return sc

def main():
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler=optuna.samplers.TPESampler(seed=505,multivariate=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    # starts: curing_phase, curing_wet_comp, warm-gated variants
    study.enqueue_trial({'drying_k':0.16870209880980871,'drying_c':71.17350795277348,'pconc_half':0.20748504787360555,'pconc_pow':3.3506752838624436,'temp_k':0.9594474500094113,'temp_c':3.9835049607606248,'cure_amp':0.45194351382483045,'wet_k':1,'wet_c':2,'wet_amp':0,'warm_k':0.5,'warm_c':8,'warm_floor':0})
    study.enqueue_trial({'drying_k':0.1735538360934589,'drying_c':68.64017764099074,'pconc_half':0.20729095122097288,'pconc_pow':3.4650356988258544,'temp_k':0.25000418411542363,'temp_c':6.901977911071024,'cure_amp':1.441590733503803,'wet_k':1.0250609893183358,'wet_c':0.809452567254946,'wet_amp':0.66644849452502,'warm_k':0.5,'warm_c':8,'warm_floor':0})
    def obj(trial):
        p=suggest(trial); sc=score(p)
        return sc['overall'] - 0.04*max(0,0.78-sc['spatial'])
    t0=time.time(); study.optimize(obj,n_trials=700,show_progress_bar=False)
    print('trials',len(study.trials),'runtime_min',(time.time()-t0)/60,'best',study.best_value)
    emit('next_curing_warmwet_opt700',study.best_params,'700-trial warm-gated wet-comp curing refinement',len(study.trials))
    # deterministic ablations based on best
    p=study.best_params.copy(); p['wet_amp']=0; emit('next_curing_warmwet_no_wet_ablation',p,'ablation: remove wet compensation from best warmwet')
    p=study.best_params.copy(); p['cure_amp']=0; emit('next_curing_warmwet_no_cure_ablation',p,'ablation: remove curing enhancement from best warmwet')
    p=study.best_params.copy(); p['warm_floor']=1; emit('next_curing_warmwet_no_warmgate_ablation',p,'ablation: wet compensation ungated by climate')
if __name__=='__main__': main()
