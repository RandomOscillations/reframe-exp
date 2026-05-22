"""Focused second-order search after curing-window ablation.

The ablation of ED-Cand2-curing_window showed the month-to-month drydown term is not
needed; the useful mechanism is a windowed release boost:
  1 + boost * dry_now * annual_precip_window * GPP_window.
This script searches that simpler family directly, plus a variant with a very soft
conditional wet cap to test whether CEAM/EQAS/SHSA repairs can be increased without
losing the newly recovered spatial skill.
"""
from pathlib import Path
import argparse, json, os, sys, time
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context, base_product, ed_transform, score, write_nc, sig, supp

REPO=Path(__file__).resolve().parents[1]
FAMILIES=['release_window','release_window_wetcap']
WEAK=['ceam','euro','tena','mide','seas','shsa','eqas']
PROTECT=['bona','nhsa','nhaf','shaf']

def suggest(trial,n,lo,hi,log=False): return trial.suggest_float(n,lo,hi,log=log)

def sample(trial,fam):
    p={
        'exp_mult':suggest(trial,'exp_mult',0.96,1.10),
        'boost':suggest(trial,'boost',0.0,1.4),
        'dry_k':suggest(trial,'dry_k',5e-4,8e-2,True),'dry_c':suggest(trial,'dry_c',20,2500,True),
        'p_low_k':suggest(trial,'p_low_k',5e-4,6e-2,True),'p_low_c':suggest(trial,'p_low_c',40,1500,True),
        'p_high_k':suggest(trial,'p_high_k',5e-4,3e-2,True),'p_high_c':suggest(trial,'p_high_c',900,5000,True),
        'gpp_lo_k':suggest(trial,'gpp_lo_k',0.02,30,True),'gpp_lo_c':suggest(trial,'gpp_lo_c',0.0005,2.0,True),
        'gpp_hi_k':suggest(trial,'gpp_hi_k',0.02,30,True),'gpp_hi_c':suggest(trial,'gpp_hi_c',0.05,12.0,True),
    }
    if fam=='release_window_wetcap':
        p.update({
            'cap_amp':suggest(trial,'cap_amp',0.0,0.25),
            'wet_k':suggest(trial,'wet_k',5e-4,2e-2,True),'wet_c':suggest(trial,'wet_c',800,5000,True),
            'lowdef_k':suggest(trial,'lowdef_k',5e-4,5e-2,True),'lowdef_c':suggest(trial,'lowdef_c',50,2500,True),
        })
    return p

def rate(ctx,fam,p,base_p):
    d=ctx.d; gpp=d['gpp_monthly']; prod=base_product(ctx,base_p)
    dry=sig(d['dbar'],p['dry_k'],p['dry_c'])
    pwin=sig(d['p_ann'],p['p_low_k'],p['p_low_c'])*supp(d['p_ann'],p['p_high_k'],p['p_high_c'])
    gwin=sig(gpp,p['gpp_lo_k'],p['gpp_lo_c'])*supp(gpp,p['gpp_hi_k'],p['gpp_hi_c'])
    fac=1.0+p['boost']*dry*pwin*gwin
    if fam=='release_window_wetcap':
        wet=sig(d['p_ann'],p['wet_k'],p['wet_c'])*supp(d['dbar'],p['lowdef_k'],p['lowdef_c'])
        fac=fac*(1.0-p['cap_amp']*wet)
    return np.power(np.clip(prod*fac,0,None),base_p['fire_exp']*p['exp_mult']).astype(np.float32)*ctx.land[None,:,:]

def objective(ctx,pred):
    g=score(ctx,pred)
    regs={r:score(ctx,pred,ctx.region_masks[r])['overall'] for r in ctx.region_masks}
    weak=np.mean([regs[r] for r in WEAK]); weakmin=min(regs[r] for r in WEAK)
    protect=min(regs[r] for r in PROTECT)
    # Protect BONA/NHSA/NHAF/SHAF after ablation showed BONA,NHSA losses.
    penalty=max(0,0.790-regs['bona'])*0.8+max(0,0.585-regs['nhsa'])*0.6+max(0,0.780-g['spatial'])*1.5
    return 0.78*g['overall']+0.08*g['spatial']+0.08*weak+0.03*weakmin+0.03*protect-penalty

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--family',choices=FAMILIES,required=True); ap.add_argument('--trials',type=int,default=500); ap.add_argument('--seed',type=int,default=20260521); ap.add_argument('--write-nc',action='store_true')
    args=ap.parse_args(); ctx=Context(); base_p=json.load(open(REPO/'models/C/params.json'))['params']
    sampler=optuna.samplers.TPESampler(seed=args.seed,multivariate=True,group=True)
    study=optuna.create_study(direction='maximize',sampler=sampler); t0=time.time()
    def obj(trial):
        p=sample(trial,args.family); return objective(ctx,ed_transform(rate(ctx,args.family,p,base_p)))
    def cb(st,tr):
        if len(st.trials)%50==0: print(f"[focus] {args.family} {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m",flush=True)
    study.optimize(obj,n_trials=args.trials,callbacks=[cb])
    p=study.best_params; raw=rate(ctx,args.family,p,base_p); pred=ed_transform(raw); glob=score(ctx,pred); regs={r:score(ctx,pred,ctx.region_masks[r]) for r in ctx.region_masks}
    out={'family':args.family,'n_trials':len(study.trials),'seed':args.seed,'fast_objective':study.best_value,'fast_global':glob,'fast_regions':regs,'params':p,'diagnostics':{'raw_land_mean':float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),'raw_max':float(raw.max())},'mechanism_note':__doc__}
    outdir=REPO/'models/explore3'/args.family; outdir.mkdir(parents=True,exist_ok=True); (outdir/'result.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'family':args.family,'best':study.best_value,'global':glob,'out':str(outdir/'result.json')},indent=2))
    if args.write_nc:
        write_nc(ctx,pred,outdir/'burntArea.nc',f'focused candidate {args.family}')
        print(outdir/'burntArea.nc')
if __name__=='__main__': main()
