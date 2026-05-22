"""Temperature-conditioned release-window search.

After release_window_wetcap improved global/public/regional scores but still degraded BONA,
this tests whether the boost should require an explicit warm ignition state. Analogy:
releasing stored chemical energy still needs an activation temperature; the base Model C
has a temperature gate, but the added fuel-release boost may need its own ignition
interlock to avoid amplifying cool boreal cells.
"""
from pathlib import Path
import argparse,json,sys,time
import numpy as np, optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context,base_product,ed_transform,score,write_nc,sig,supp
REPO=Path(__file__).resolve().parents[1]
WEAK=['ceam','euro','tena','mide','seas','shsa','eqas']

def sug(t,n,lo,hi,log=False): return t.suggest_float(n,lo,hi,log=log)
def sample(t):
 return {'exp_mult':sug(t,'exp_mult',0.96,1.10),'boost':sug(t,'boost',0,1.6),'dry_k':sug(t,'dry_k',5e-4,8e-2,True),'dry_c':sug(t,'dry_c',20,2500,True),'p_low_k':sug(t,'p_low_k',5e-4,6e-2,True),'p_low_c':sug(t,'p_low_c',40,1500,True),'p_high_k':sug(t,'p_high_k',5e-4,3e-2,True),'p_high_c':sug(t,'p_high_c',900,5000,True),'gpp_lo_k':sug(t,'gpp_lo_k',0.02,30,True),'gpp_lo_c':sug(t,'gpp_lo_c',5e-4,2,True),'gpp_hi_k':sug(t,'gpp_hi_k',0.02,30,True),'gpp_hi_c':sug(t,'gpp_hi_c',0.05,12,True),'temp_k':sug(t,'temp_k',0.005,1.5,True),'temp_c':sug(t,'temp_c',275,310),'cap_amp':sug(t,'cap_amp',0,0.25),'wet_k':sug(t,'wet_k',5e-4,2e-2,True),'wet_c':sug(t,'wet_c',800,5000,True),'lowdef_k':sug(t,'lowdef_k',5e-4,5e-2,True),'lowdef_c':sug(t,'lowdef_c',50,2500,True)}
def rate(ctx,p,base):
 d=ctx.d; g=d['gpp_monthly']; prod=base_product(ctx,base)
 rel=sig(d['dbar'],p['dry_k'],p['dry_c'])*sig(d['p_ann'],p['p_low_k'],p['p_low_c'])*supp(d['p_ann'],p['p_high_k'],p['p_high_c'])*sig(g,p['gpp_lo_k'],p['gpp_lo_c'])*supp(g,p['gpp_hi_k'],p['gpp_hi_c'])*sig(d['t_air'],p['temp_k'],p['temp_c'])
 wet=sig(d['p_ann'],p['wet_k'],p['wet_c'])*supp(d['dbar'],p['lowdef_k'],p['lowdef_c'])
 fac=(1+p['boost']*rel)*(1-p['cap_amp']*wet)
 return np.power(np.clip(prod*fac,0,None),base['fire_exp']*p['exp_mult']).astype(np.float32)*ctx.land[None,:,:]
def obj(ctx,pred):
 g=score(ctx,pred); regs={r:score(ctx,pred,ctx.region_masks[r])['overall'] for r in ctx.region_masks}; weak=np.mean([regs[r] for r in WEAK])
 penalty=max(0,0.800-regs['bona'])*1.2+max(0,0.586-regs['nhsa'])*0.8+max(0,0.785-g['spatial'])*1.2
 return .78*g['overall']+.08*g['spatial']+.08*weak+.03*min(regs[r] for r in WEAK)+.03*min(regs[r] for r in ['nhaf','shaf','boas','bona'])-penalty
def main():
 ctx=Context(); base=json.load(open(REPO/'models/C/params.json'))['params']; sampler=optuna.samplers.TPESampler(seed=20260522,multivariate=True,group=True); study=optuna.create_study(direction='maximize',sampler=sampler); t0=time.time()
 def f(trial): return obj(ctx,ed_transform(rate(ctx,sample(trial),base)))
 def cb(st,tr):
  if len(st.trials)%50==0: print(f"[temp] {len(st.trials)}/500 best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m",flush=True)
 study.optimize(f,n_trials=500,callbacks=[cb]); p=study.best_params; raw=rate(ctx,p,base); pred=ed_transform(raw); glob=score(ctx,pred); regs={r:score(ctx,pred,ctx.region_masks[r]) for r in ctx.region_masks}; out={'family':'release_window_temp_wetcap','n_trials':len(study.trials),'seed':20260522,'fast_objective':study.best_value,'fast_global':glob,'fast_regions':regs,'params':p,'mechanism_note':__doc__}
 outdir=REPO/'models/explore3/release_window_temp_wetcap'; outdir.mkdir(parents=True,exist_ok=True); (outdir/'result.json').write_text(json.dumps(out,indent=2)); print(json.dumps({'global':glob,'out':str(outdir/'result.json')},indent=2)); write_nc(ctx,pred,outdir/'burntArea.nc','release window temp wetcap')
if __name__=='__main__': main()
