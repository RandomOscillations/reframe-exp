#!/usr/bin/env python3
"""Continued search: wet-canopy + two-threshold arid fuel-continuity limiter.

Single global formula using only allowed Model C inputs. Designed after the
wet-temperature candidate improved weak regions but damaged BONA/BOAS: avoid
thermal wet gating and instead add broad annual wet-canopy suppression plus a
fuel-network fragmentation limiter based on Dbar/Pann.
"""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
import optuna
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_candidates as rc
from reproduce_modelC import sig

BASE=rc.BASE.copy(); OUTROOT=Path('runs/candidates')
# Model C base *rate* after fire_exp. Suppressors are applied to the annual
# rate, matching the mechanistic formula: base_fire × wet × arid thresholds.
prod0=rc.base_product(BASE).astype(np.float32)
base_rate=np.power(np.clip(prod0,0,None), BASE['fire_exp']).astype(np.float32)
P=rc.ann_p.astype(np.float32); D=rc.dbar.astype(np.float32)

SEED={
 'wet_amp':0.8844066447148519,'wet_k':0.03746225268483959,'wet_c':1733.7962048788854,
 'ratio_p0':10.550923117584711,
 'arid_amp1':0.09765875631019073,'arid_k1':8.862392037192233,'arid_c1':0.8190773026156323,
 'arid_amp2':0.872802820380493,'arid_k2':1.2991349033470558,'arid_c2':5.00184048998816,
}

def predict_extra(p):
    wet_suppress = 1.0 - p['wet_amp'] * sig(P, p['wet_k'], p['wet_c'])
    ratio = D / (P + p['ratio_p0'])
    arid1 = 1.0 - p['arid_amp1'] * sig(ratio, p['arid_k1'], p['arid_c1'])
    arid2 = 1.0 - p['arid_amp2'] * sig(ratio, p['arid_k2'], p['arid_c2'])
    mod = np.clip(wet_suppress * arid1 * arid2, 0.0, 1.0).astype(np.float32)
    rate=(base_rate * mod).astype(np.float32)*rc.land_mask[None,:,:]
    return rc.ed_transform(rate)

def score(p): return rc.score(predict_extra(p))

def suggest(trial):
    return {
      'wet_amp': trial.suggest_float('wet_amp',0.0,0.95),
      'wet_k': trial.suggest_float('wet_k',0.001,0.08,log=True),
      'wet_c': trial.suggest_float('wet_c',600,3500),
      'ratio_p0': trial.suggest_float('ratio_p0',1,200,log=True),
      'arid_amp1': trial.suggest_float('arid_amp1',0.0,0.4),
      'arid_k1': trial.suggest_float('arid_k1',0.1,15,log=True),
      'arid_c1': trial.suggest_float('arid_c1',0.1,2.5),
      'arid_amp2': trial.suggest_float('arid_amp2',0.0,0.95),
      'arid_k2': trial.suggest_float('arid_k2',0.1,8,log=True),
      'arid_c2': trial.suggest_float('arid_c2',1.0,10.0),
    }

def emit(name,p,search_note):
    pred=predict_extra(p); sc=rc.score(pred); out=OUTROOT/name; out.mkdir(parents=True,exist_ok=True); rc.write_nc(pred,out)
    meta={'family':'wet_canopy_plus_two_threshold_arid_fuel_continuity','name':name,'search':search_note,'fast_score':sc,'params':p,'base_params':BASE,'constraint_note':'one global formula using P_ann and Dbar-derived deficit ratio; no region/lat/cell routing'}
    (out/'params.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta,indent=2)); return sc

def main():
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    n=600; sampler=optuna.samplers.TPESampler(seed=207,multivariate=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    study.enqueue_trial(SEED)
    # ablation warm starts
    p=SEED.copy(); p['arid_amp1']=0.0; study.enqueue_trial(p)
    p=SEED.copy(); p['arid_amp2']=0.0; study.enqueue_trial(p)
    t0=time.time()
    def obj(trial):
        p=suggest(trial); sc=score(p)
        # protect global spatial; proxy only, official regional decides.
        return sc['overall'] - 0.02*max(0,0.75-sc['spatial'])
    study.optimize(obj,n_trials=n,show_progress_bar=False)
    best=study.best_params; print('trials',len(study.trials),'runtime_min',(time.time()-t0)/60)
    emit('p2f3_seed_current',SEED,'seeded from continued hypothesis, emitted for official evaluation')
    emit('p2f3_optuna600_current',best,'600-trial Optuna refinement in current workspace')
    p=SEED.copy(); p['arid_amp1']=0.0; emit('p2f3_ablate_no_low_current',p,'ablation: remove low/soft arid threshold')
    p=SEED.copy(); p['arid_amp2']=0.0; emit('p2f3_ablate_no_high_current',p,'ablation: remove high/desert arid threshold')

if __name__=='__main__': main()
