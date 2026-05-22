"""Third-cycle constrained global fire-model mechanisms.

This script starts from original Model C and the prior continuation evidence rather
than from a privileged final candidate. Prior learning:
  * blunt wet suppression repaired CEAM/EURO/EQAS/SHSA but collapsed global Spatial;
  * fuel charging alone and naked drydown damaged strong fire belts or were pruned;
  * the best prior signal was a current dry release window in intermediate annual
    precipitation and GPP, plus a soft wet/low-deficit cap;
  * BONA/NHSA losses remained, and a simple temperature activation interlock failed.

The third-cycle hypotheses use structural analogies to make testable global forms:
  * relay-protection grid: a release gate can have upstream cold/short-season guards
    instead of named boreal routing;
  * supply-chain bottleneck: fire occurs only when fuel supply, curing/senescence,
    warmth, and dry weather arrive together;
  * combustion corridor: hyperarid fuel limits and wet-canopy limits are two sides of
    the same stoichiometric balance.

All candidate formulas are one global formula with global parameters and use only
allowed Model C inputs/transforms: dbar, annual precipitation, monthly precipitation,
monthly air temperature, and monthly GPP. GFED is used only for screening.
"""
from pathlib import Path
import argparse, json, os, sys, time
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context, base_product, ed_transform, score, write_nc, sig, supp, prev_month, roll_mean

REPO = Path(__file__).resolve().parents[1]
FAMILIES = [
    "guarded_release",          # release_window_wetcap plus cold/short-warm-season guard
    "senescence_release",       # dry release requires GPP drawdown/curing rather than dbar derivative
    "dual_corridor_balance",    # intermediate precip/GPP release plus hyperarid and wet-canopy corridor caps
    "warm_dry_supply_chain",    # release gate requires warm, dry, low monthly precip, fuel window alignment
]
WEAK = ["ceam","euro","tena","mide","seas","shsa","eqas"]
PROTECT = ["bona","nhsa","nhaf","shaf","boas","aust","ceas"]

class Ctx4(Context):
    def __init__(self):
        super().__init__()
        t = self.d["t_air"]
        g = self.d["gpp_monthly"]
        p = self.d["p_month"]
        # Repeated annual context derived only from monthly allowed fields.
        self.t_ann = t.reshape(-1,12,180,360).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.t_warm_frac = (t.reshape(-1,12,180,360) > 285.0).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.gpp_prev = prev_month(g)
        self.gpp_drop = (self.gpp_prev - g).astype(np.float32)
        self.gpp_ann = g.reshape(-1,12,180,360).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.p_prev3 = roll_mean(p,3)
        self.t3 = roll_mean(t,3)

def suggest(trial,n,lo,hi,log=False):
    return trial.suggest_float(n,lo,hi,log=log)

def base_release_terms(ctx,p):
    d=ctx.d; gpp=d['gpp_monthly']
    dry=sig(d['dbar'],p['dry_k'],p['dry_c'])
    pwin=sig(d['p_ann'],p['p_low_k'],p['p_low_c'])*supp(d['p_ann'],p['p_high_k'],p['p_high_c'])
    gwin=sig(gpp,p['gpp_lo_k'],p['gpp_lo_c'])*supp(gpp,p['gpp_hi_k'],p['gpp_hi_c'])
    wet_low=sig(d['p_ann'],p.get('wet_k',0.001),p.get('wet_c',2200.0))*supp(d['dbar'],p.get('lowdef_k',0.01),p.get('lowdef_c',250.0))
    return dry,pwin,gwin,wet_low

def sample_common(trial):
    return {
        'exp_mult': suggest(trial,'exp_mult',0.98,1.12),
        'boost': suggest(trial,'boost',0.0,1.8),
        'dry_k': suggest(trial,'dry_k',5e-4,8e-2,True), 'dry_c': suggest(trial,'dry_c',20,2500,True),
        'p_low_k': suggest(trial,'p_low_k',5e-4,8e-2,True), 'p_low_c': suggest(trial,'p_low_c',40,1600,True),
        'p_high_k': suggest(trial,'p_high_k',5e-4,4e-2,True), 'p_high_c': suggest(trial,'p_high_c',900,5500,True),
        'gpp_lo_k': suggest(trial,'gpp_lo_k',0.02,35,True), 'gpp_lo_c': suggest(trial,'gpp_lo_c',0.0005,2.5,True),
        'gpp_hi_k': suggest(trial,'gpp_hi_k',0.02,35,True), 'gpp_hi_c': suggest(trial,'gpp_hi_c',0.05,14.0,True),
        'cap_amp': suggest(trial,'cap_amp',0.0,0.35),
        'wet_k': suggest(trial,'wet_k',5e-4,2e-2,True), 'wet_c': suggest(trial,'wet_c',700,5500,True),
        'lowdef_k': suggest(trial,'lowdef_k',5e-4,6e-2,True), 'lowdef_c': suggest(trial,'lowdef_c',30,3000,True),
    }

def sample(trial,fam):
    p=sample_common(trial)
    if fam=='guarded_release':
        p.update({
            'guard_amp': suggest(trial,'guard_amp',0.0,0.75),
            'cold_k': suggest(trial,'cold_k',0.02,1.0,True), 'cold_c': suggest(trial,'cold_c',270,292),
            'short_k': suggest(trial,'short_k',2.0,40.0,True), 'short_c': suggest(trial,'short_c',0.10,0.85),
            'guard_gpp_k': suggest(trial,'guard_gpp_k',0.05,30,True), 'guard_gpp_c': suggest(trial,'guard_gpp_c',0.01,8,True),
        })
    elif fam=='senescence_release':
        p.update({
            'sen_k': suggest(trial,'sen_k',0.2,80,True), 'sen_c': suggest(trial,'sen_c',-0.5,1.5),
            'sen_mix': suggest(trial,'sen_mix',0.0,1.0),
            'ann_gpp_k': suggest(trial,'ann_gpp_k',0.02,20,True), 'ann_gpp_c': suggest(trial,'ann_gpp_c',0.01,8,True),
        })
    elif fam=='dual_corridor_balance':
        p.update({
            'arid_amp': suggest(trial,'arid_amp',0.0,0.60),
            'arid_k': suggest(trial,'arid_k',5e-4,5e-2,True), 'arid_c': suggest(trial,'arid_c',20,1000,True),
            'hotboost': suggest(trial,'hotboost',0.0,0.7),
            'hot_k': suggest(trial,'hot_k',0.005,1.0,True), 'hot_c': suggest(trial,'hot_c',270,315),
        })
    elif fam=='warm_dry_supply_chain':
        p.update({
            'warm_k': suggest(trial,'warm_k',0.005,1.0,True), 'warm_c': suggest(trial,'warm_c',270,315),
            'pm_k': suggest(trial,'pm_k',0.005,1.0,True), 'pm_c': suggest(trial,'pm_c',1,250,True),
            'gate_floor': suggest(trial,'gate_floor',0.0,0.8),
        })
    return p

def rate(ctx,fam,p,base_p):
    prod=base_product(ctx,base_p)
    dry,pwin,gwin,wet_low=base_release_terms(ctx,p)
    release=dry*pwin*gwin
    cap=1.0-p['cap_amp']*wet_low
    if fam=='guarded_release':
        # Cold/short-season guard is a physical state, not BONA routing: cold annual temp, short warm season,
        # and productive fuel imply slow decomposition/snow-season constraints where the generic release boost
        # should be attenuated.
        cold=supp(ctx.t_ann,p['cold_k'],p['cold_c'])
        short=supp(ctx.t_warm_frac,p['short_k'],p['short_c'])
        productive=sig(ctx.gpp_ann,p['guard_gpp_k'],p['guard_gpp_c'])
        guard=1.0-p['guard_amp']*cold*short*productive
        fac=(1.0+p['boost']*release*guard)*cap
    elif fam=='senescence_release':
        # Agricultural/grass curing analogy: a standing fuel supply becomes flammable as live productivity falls.
        sen=sig(ctx.gpp_drop,p['sen_k'],p['sen_c'])
        annfuel=sig(ctx.gpp_ann,p['ann_gpp_k'],p['ann_gpp_c'])
        release2=dry*pwin*(p['sen_mix']*sen*annfuel + (1-p['sen_mix'])*gwin)
        fac=(1.0+p['boost']*release2)*cap
    elif fam=='dual_corridor_balance':
        # Two-sided combustion corridor: suppress true hyperarid fuel absence, softly cap wet/low-deficit canopy,
        # and allow hot-dry semi-arid compensation only inside the annual precip window.
        arid=supp(ctx.d['p_ann'],p['arid_k'],p['arid_c'])
        warm=sig(ctx.d['t_air'],p['hot_k'],p['hot_c'])
        hotdry=warm*dry*pwin
        fac=(1.0+p['boost']*release)*(1.0-p['arid_amp']*arid)*(1.0+p['hotboost']*hotdry)*cap
    elif fam=='warm_dry_supply_chain':
        # Supply-chain/F1 pit analogy: all stations must be ready in the same month. Require warm temperatures
        # and absence of recent rain to synchronize with dry fuel release.
        warm=sig(ctx.t3,p['warm_k'],p['warm_c'])
        no_recent_rain=supp(ctx.p_prev3,p['pm_k'],p['pm_c'])
        sync=p['gate_floor']+(1-p['gate_floor'])*warm*no_recent_rain
        fac=(1.0+p['boost']*release*sync)*cap
    else:
        raise ValueError(fam)
    return (np.power(np.clip(prod*fac,0,None),base_p['fire_exp']*p['exp_mult']).astype(np.float32)*ctx.land[None,:,:])

def summarize(ctx,pred):
    glob=score(ctx,pred)
    regs={r:score(ctx,pred,ctx.region_masks[r]) for r in ctx.region_masks}
    weak=[regs[r]['overall'] for r in WEAK]
    prot=[regs[r]['overall'] for r in PROTECT]
    return glob,regs,float(np.mean(weak)),float(min(weak)),float(np.mean(prot)),float(min(prot))

def objective(ctx,pred):
    g,regs,weak,weakmin,prot,protmin=summarize(ctx,pred)
    # Prior failures: do not buy weak-region repairs by losing Spatial or boreal/African belts.
    penalty=(max(0,0.770-g['spatial'])*1.8 + max(0,0.790-regs['bona']['overall'])*0.8 +
             max(0,0.585-regs['nhsa']['overall'])*0.6 + max(0,0.660,min(regs['nhaf']['overall'],regs['shaf']['overall']))*0.5)
    return 0.76*g['overall']+0.10*g['spatial']+0.08*weak+0.03*weakmin+0.03*prot-penalty

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--family',choices=FAMILIES,required=True)
    ap.add_argument('--trials',type=int,default=500)
    ap.add_argument('--seed',type=int,default=20260522)
    ap.add_argument('--outdir',default='models/explore4')
    ap.add_argument('--write-nc',action='store_true')
    args=ap.parse_args()
    ctx=Ctx4(); base_p=json.load(open(REPO/'models/C/params.json'))['params']
    sampler=optuna.samplers.TPESampler(seed=args.seed,multivariate=True,group=True)
    study=optuna.create_study(direction='maximize',sampler=sampler)
    t0=time.time()
    def obj(trial):
        p=sample(trial,args.family)
        return objective(ctx,ed_transform(rate(ctx,args.family,p,base_p)))
    def cb(st,tr):
        if len(st.trials)%50==0:
            print(f"[opt4] {args.family} {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m", flush=True)
    study.optimize(obj,n_trials=args.trials,callbacks=[cb])
    p=study.best_params; raw=rate(ctx,args.family,p,base_p); pred=ed_transform(raw)
    glob,regs,weak,weakmin,prot,protmin=summarize(ctx,pred)
    out={'family':args.family,'n_trials':len(study.trials),'seed':args.seed,'fast_objective':study.best_value,
         'fast_global':glob,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_mean':prot,'protect_min':protmin,
         'params':p,'diagnostics':{'raw_land_mean':float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),'raw_max':float(raw.max())},
         'mechanism_note':__doc__}
    outdir=REPO/args.outdir/args.family; outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'result.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'family':args.family,'best':study.best_value,'global':glob,'weak_mean':weak,'protect_min':protmin,'out':str(outdir/'result.json')},indent=2))
    if args.write_nc:
        write_nc(ctx,pred,outdir/'burntArea.nc',f'third-cycle candidate {args.family}')
        print(f"wrote {outdir/'burntArea.nc'}")
if __name__=='__main__': main()
