"""Pareto-focused refinement after third-cycle tradeoffs.

The first third-cycle search showed two useful but conflicting signals:
  * senescence_release nearly tied ED-Cand3 global diagnostic and repaired NHSA/EURO/EQAS,
    but still worsened BONA more than ED-Cand3;
  * dual_corridor_balance strongly repaired weak regions (EURO/EQAS/SHSA/NHSA/TENA) but
    paid for it with BONA and African fire-belt losses.

This script tests whether those signals can be combined under realistic fast-score
protection thresholds calibrated to ED-Cand3's fast diagnostics, rather than the
previous overly high official-scale proxy thresholds. The analogy is Pareto-front
control in engineering design: after discovering two actuators, tune them with hard
protection limits instead of maximizing one aggregate.

All formulas remain one global formula with allowed predictors only.
"""
from pathlib import Path
import argparse, json, sys, time
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_third_order_candidates import Ctx4, base_release_terms, sample_common
from explore_fire_candidates import base_product, ed_transform, score, write_nc, sig, supp
REPO=Path(__file__).resolve().parents[1]
FAMILIES=['pareto_senescence_corridor','pareto_guarded_corridor']
WEAK=['ceam','euro','tena','mide','seas','shsa','eqas']
PROTECT=['bona','nhsa','nhaf','shaf','boas','aust','ceas']
# Fast proxy thresholds from ED-Cand3-release_window_wetcap result.json.
C3_FAST={'overall':0.6358675,'spatial':0.7722817,'bona':0.6560549,'nhsa':0.4876411,'nhaf':0.6514797,'shaf':0.6478458,'weak':0.35007}

def suggest(t,n,lo,hi,log=False): return t.suggest_float(n,lo,hi,log=log)
def sample(t,fam):
    p=sample_common(t)
    p['boost']=suggest(t,'boost',0.0,1.6)
    p['cap_amp']=suggest(t,'cap_amp',0.0,0.30)
    if 'senescence' in fam:
        p.update({'sen_k':suggest(t,'sen_k',0.2,80,True),'sen_c':suggest(t,'sen_c',-0.5,1.5),'sen_mix':suggest(t,'sen_mix',0,1),'ann_gpp_k':suggest(t,'ann_gpp_k',0.02,20,True),'ann_gpp_c':suggest(t,'ann_gpp_c',0.01,8,True)})
    if 'guarded' in fam:
        p.update({'guard_amp':suggest(t,'guard_amp',0,0.8),'cold_k':suggest(t,'cold_k',0.02,1,True),'cold_c':suggest(t,'cold_c',270,292),'short_k':suggest(t,'short_k',2,40,True),'short_c':suggest(t,'short_c',0.1,0.85),'guard_gpp_k':suggest(t,'guard_gpp_k',0.05,30,True),'guard_gpp_c':suggest(t,'guard_gpp_c',0.01,8,True)})
    p.update({'arid_amp':suggest(t,'arid_amp',0,0.45),'arid_k':suggest(t,'arid_k',5e-4,5e-2,True),'arid_c':suggest(t,'arid_c',20,1000,True),'hotboost':suggest(t,'hotboost',0,0.45),'hot_k':suggest(t,'hot_k',0.005,1,True),'hot_c':suggest(t,'hot_c',270,315)})
    return p

def rate(ctx,fam,p,base_p):
    prod=base_product(ctx,base_p); dry,pwin,gwin,wet_low=base_release_terms(ctx,p)
    release=dry*pwin*gwin
    if 'senescence' in fam:
        sen=sig(ctx.gpp_drop,p['sen_k'],p['sen_c']); annfuel=sig(ctx.gpp_ann,p['ann_gpp_k'],p['ann_gpp_c'])
        release=(1-p['sen_mix'])*release + p['sen_mix']*dry*pwin*sen*annfuel
    if 'guarded' in fam:
        cold=supp(ctx.t_ann,p['cold_k'],p['cold_c']); short=supp(ctx.t_warm_frac,p['short_k'],p['short_c']); productive=sig(ctx.gpp_ann,p['guard_gpp_k'],p['guard_gpp_c'])
        release=release*(1-p['guard_amp']*cold*short*productive)
    arid=supp(ctx.d['p_ann'],p['arid_k'],p['arid_c']); warm=sig(ctx.d['t_air'],p['hot_k'],p['hot_c']); hotdry=warm*dry*pwin
    fac=(1+p['boost']*release)*(1-p['cap_amp']*wet_low)*(1-p['arid_amp']*arid)*(1+p['hotboost']*hotdry)
    return np.power(np.clip(prod*fac,0,None),base_p['fire_exp']*p['exp_mult']).astype(np.float32)*ctx.land[None,:,:]

def summarize(ctx,pred):
    g=score(ctx,pred); regs={r:score(ctx,pred,ctx.region_masks[r]) for r in ctx.region_masks}
    weak=float(np.mean([regs[r]['overall'] for r in WEAK])); weakmin=float(min(regs[r]['overall'] for r in WEAK)); prot=float(min(regs[r]['overall'] for r in PROTECT))
    return g,regs,weak,weakmin,prot

def objective(ctx,pred):
    g,regs,weak,weakmin,prot=summarize(ctx,pred)
    penalty=0
    penalty+=max(0,C3_FAST['spatial']-g['spatial'])*1.2
    penalty+=max(0,C3_FAST['bona']-regs['bona']['overall'])*0.8
    penalty+=max(0,C3_FAST['nhaf']-regs['nhaf']['overall'])*0.5
    penalty+=max(0,C3_FAST['shaf']-regs['shaf']['overall'])*0.5
    # Encourage true Pareto behavior: global near C3, weak-region improvement over C3.
    return 0.74*g['overall']+0.10*g['spatial']+0.10*weak+0.03*weakmin+0.03*prot-penalty

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--family',choices=FAMILIES,required=True); ap.add_argument('--trials',type=int,default=500); ap.add_argument('--seed',type=int,default=20260523); ap.add_argument('--write-nc',action='store_true')
    args=ap.parse_args(); ctx=Ctx4(); base_p=json.load(open(REPO/'models/C/params.json'))['params']
    study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=args.seed,multivariate=True,group=True)); t0=time.time()
    def obj(trial): return objective(ctx,ed_transform(rate(ctx,args.family,sample(trial,args.family),base_p)))
    def cb(st,tr):
        if len(st.trials)%50==0: print(f"[pareto] {args.family} {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m",flush=True)
    study.optimize(obj,n_trials=args.trials,callbacks=[cb])
    p=study.best_params; raw=rate(ctx,args.family,p,base_p); pred=ed_transform(raw); g,regs,weak,weakmin,prot=summarize(ctx,pred)
    out={'family':args.family,'n_trials':len(study.trials),'seed':args.seed,'fast_objective':study.best_value,'fast_global':g,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'params':p,'diagnostics':{'raw_land_mean':float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),'raw_max':float(raw.max())},'mechanism_note':__doc__}
    outdir=REPO/'models/explore4'/args.family; outdir.mkdir(parents=True,exist_ok=True); (outdir/'result.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'family':args.family,'best':study.best_value,'global':g,'weak_mean':weak,'protect_min':prot,'out':str(outdir/'result.json')},indent=2))
    if args.write_nc:
        write_nc(ctx,pred,outdir/'burntArea.nc',f'pareto release candidate {args.family}'); print(f"wrote {outdir/'burntArea.nc'}")
if __name__=='__main__': main()
