"""Cycle-3-after-report constrained fire mechanism search.

This continuation treats previous reports as checkpoints, not endpoints.  Failure
learning carried forward:
  * ED-Cand4Abl-no_hotboost is the global/public leader but loses NHSA/SHSA/SEAS/
    CEAM/TENA mostly through regional Spatial and Seasonal degradation relative to
    ED-Cand3-release_window_wetcap.
  * ED-Cand3 is the broad regional compromise, but leaves global/public score on the
    table and still weakens BONA/NHSA.
  * Dual-corridor repair helped weak wet/temperate regions but damaged BONA/Africa.
  * Senescence repaired NHSA/EURO/EQAS but hurt strong belts.
  * Hotboost and month-to-month dbar drydown were pruned; blunt wet suppression hurt
    global Spatial.

New analogies converted into testable one-global-formula mechanisms:
  1. monsoon_break_release: wildfire as a supply-chain handoff in monsoon systems.
     Wet-season fuel charging is only useful when followed by a rain-free break, so
     the release term is gated by recent precipitation hiatus and live-fuel drawdown.
  2. mosaic_edge_release: a fire-line/forest-edge analogy.  Burning in humid mixed
     regions occurs at edges where high annual productivity is temporarily cured, not
     in the wet core; the wet cap is relaxed only under allowed cell-state evidence of
     a dry edge month.
  3. protected_corridor: a power-grid protection analogy.  Keep the global/public
     corridor terms that helped Cand4Abl, but add physically inferred protection for
     monsoon dry-season phase and cold productive short-season cells to avoid moving
     power through the wrong line.

All formulas are one global formula with global parameters and use only allowed Model C
inputs/transforms: dbar, annual precipitation, monthly precipitation, monthly air
temperature, and monthly GPP. GFED is used only for screening/evaluation.
"""
from pathlib import Path
import argparse, json, sys, time
import numpy as np
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context, base_product, ed_transform, score, write_nc, sig, supp, prev_month, roll_mean

REPO=Path(__file__).resolve().parents[1]
FAMILIES=['monsoon_break_release','mosaic_edge_release','protected_corridor']
WEAK=['ceam','euro','tena','mide','seas','shsa','eqas','nhsa']
PROTECT=['bona','nhaf','shaf','boas','aust','ceas']
# Fast-proxy checkpoint metrics from prior logs/result files. These are only screening
# thresholds; official ILAMB remains the acceptance evidence.
C3={'overall':0.6358675,'spatial':0.7722817,'weak':0.35007,'nhsa':0.4876411,'shsa':0.4442,'seas':0.4448,'ceam':0.3253,'tena':0.3959,'bona':0.6560549,'nhaf':0.6514797,'shaf':0.6478458}
C4={'overall':0.63750,'spatial':0.778832,'bona':0.655867,'nhaf':0.652985,'shaf':0.663826}

class Ctx5(Context):
    def __init__(self):
        super().__init__()
        t=self.d['t_air']; g=self.d['gpp_monthly']; p=self.d['p_month']
        self.t_ann=t.reshape(-1,12,180,360).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.t_warm_frac=(t.reshape(-1,12,180,360)>285.0).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.gpp_prev=prev_month(g)
        self.gpp_drop=(self.gpp_prev-g).astype(np.float32)
        self.gpp_ann=g.reshape(-1,12,180,360).mean(axis=1).repeat(12,axis=0).astype(np.float32)
        self.p_prev3=roll_mean(p,3)
        self.p_prev6=roll_mean(p,6)
        self.gpp_prev3=roll_mean(g,3)
        self.t3=roll_mean(t,3)
        # Allowed annual/monthly derived seasonality proxies; no region/lat/lon.
        years=p.reshape(-1,12,180,360)
        self.p_month_frac=(p/(self.d['p_ann']+1e-6)).astype(np.float32)
        self.p_seasonality=(years.max(axis=1)-years.min(axis=1)).repeat(12,axis=0).astype(np.float32)
        self.gpp_seasonality=(g.reshape(-1,12,180,360).max(axis=1)-g.reshape(-1,12,180,360).min(axis=1)).repeat(12,axis=0).astype(np.float32)

def sf(t,n,lo,hi,log=False): return t.suggest_float(n,lo,hi,log=log)

def common(trial):
    return {
        'exp_mult': sf(trial,'exp_mult',0.98,1.12),
        'boost': sf(trial,'boost',0.0,1.8),
        'dry_k': sf(trial,'dry_k',5e-4,8e-2,True), 'dry_c': sf(trial,'dry_c',20,2500,True),
        'p_low_k': sf(trial,'p_low_k',5e-4,8e-2,True), 'p_low_c': sf(trial,'p_low_c',40,1800,True),
        'p_high_k': sf(trial,'p_high_k',5e-4,4e-2,True), 'p_high_c': sf(trial,'p_high_c',900,6000,True),
        'gpp_lo_k': sf(trial,'gpp_lo_k',0.02,35,True), 'gpp_lo_c': sf(trial,'gpp_lo_c',0.0005,3.0,True),
        'gpp_hi_k': sf(trial,'gpp_hi_k',0.02,35,True), 'gpp_hi_c': sf(trial,'gpp_hi_c',0.05,14.0,True),
        'cap_amp': sf(trial,'cap_amp',0.0,0.35),
        'wet_k': sf(trial,'wet_k',5e-4,2e-2,True), 'wet_c': sf(trial,'wet_c',700,6000,True),
        'lowdef_k': sf(trial,'lowdef_k',5e-4,6e-2,True), 'lowdef_c': sf(trial,'lowdef_c',30,3000,True),
        'arid_amp': sf(trial,'arid_amp',0.0,0.45), 'arid_k': sf(trial,'arid_k',5e-4,5e-2,True), 'arid_c': sf(trial,'arid_c',20,1000,True),
    }

def sample(trial,fam):
    p=common(trial)
    # Shared physically inferred guards/corridors.
    p.update({
        'rainbreak_k': sf(trial,'rainbreak_k',0.005,1.0,True), 'rainbreak_c': sf(trial,'rainbreak_c',1,220,True),
        'sen_k': sf(trial,'sen_k',0.2,80,True), 'sen_c': sf(trial,'sen_c',-0.5,1.5),
        'monsoon_k': sf(trial,'monsoon_k',1e-4,5e-2,True), 'monsoon_c': sf(trial,'monsoon_c',20,2500,True),
        'cold_guard_amp': sf(trial,'cold_guard_amp',0.0,0.55),
        'cold_k': sf(trial,'cold_k',0.02,1.0,True), 'cold_c': sf(trial,'cold_c',270,292),
        'short_k': sf(trial,'short_k',2.0,40.0,True), 'short_c': sf(trial,'short_c',0.1,0.85),
    })
    if fam=='monsoon_break_release':
        p.update({'charge_k':sf(trial,'charge_k',0.005,0.8,True),'charge_c':sf(trial,'charge_c',2,300,True),'phase_mix':sf(trial,'phase_mix',0,1),'cap_relief':sf(trial,'cap_relief',0,0.35)})
    elif fam=='mosaic_edge_release':
        p.update({'edge_k':sf(trial,'edge_k',0.005,0.8,True),'edge_c':sf(trial,'edge_c',1,250,True),'annfuel_k':sf(trial,'annfuel_k',0.02,20,True),'annfuel_c':sf(trial,'annfuel_c',0.01,8,True),'edge_mix':sf(trial,'edge_mix',0,1),'cap_relief':sf(trial,'cap_relief',0,0.45)})
    elif fam=='protected_corridor':
        p.update({'guard_gpp_k':sf(trial,'guard_gpp_k',0.05,30,True),'guard_gpp_c':sf(trial,'guard_gpp_c',0.01,8,True),'phase_amp':sf(trial,'phase_amp',0,0.7),'cap_relief':sf(trial,'cap_relief',0,0.30)})
    return p

def base_terms(ctx,p):
    d=ctx.d; g=d['gpp_monthly']
    dry=sig(d['dbar'],p['dry_k'],p['dry_c'])
    pwin=sig(d['p_ann'],p['p_low_k'],p['p_low_c'])*supp(d['p_ann'],p['p_high_k'],p['p_high_c'])
    gwin=sig(g,p['gpp_lo_k'],p['gpp_lo_c'])*supp(g,p['gpp_hi_k'],p['gpp_hi_c'])
    wet_low=sig(d['p_ann'],p['wet_k'],p['wet_c'])*supp(d['dbar'],p['lowdef_k'],p['lowdef_c'])
    arid=supp(d['p_ann'],p['arid_k'],p['arid_c'])
    rainbreak=supp(ctx.p_prev3,p['rainbreak_k'],p['rainbreak_c'])
    sen=sig(ctx.gpp_drop,p['sen_k'],p['sen_c'])
    monsoon=sig(ctx.p_seasonality,p['monsoon_k'],p['monsoon_c'])
    cold=supp(ctx.t_ann,p['cold_k'],p['cold_c']); short=supp(ctx.t_warm_frac,p['short_k'],p['short_c'])
    cold_guard=1-p['cold_guard_amp']*cold*short
    return dry,pwin,gwin,wet_low,arid,rainbreak,sen,monsoon,cold_guard

def rate(ctx,fam,p,base_p):
    prod=base_product(ctx,base_p)
    dry,pwin,gwin,wet_low,arid,rainbreak,sen,monsoon,cold_guard=base_terms(ctx,p)
    release=dry*pwin*gwin
    cap=1-p['cap_amp']*wet_low
    if fam=='monsoon_break_release':
        # Recently wet/productive systems become burnable only after a rain hiatus and live-fuel drawdown.
        charge=sig(ctx.p_prev6,p['charge_k'],p['charge_c'])
        phase=monsoon*rainbreak*(p['phase_mix']*sen+(1-p['phase_mix'])*charge)
        release=release*(1+phase)
        cap=cap + p['cap_relief']*wet_low*phase
    elif fam=='mosaic_edge_release':
        # Wet productive cores remain capped; dry edges are inferred by high annual fuel + rain hiatus + senescence.
        annfuel=sig(ctx.gpp_ann,p['annfuel_k'],p['annfuel_c'])
        edge=supp(ctx.p_prev3,p['edge_k'],p['edge_c'])*sen*annfuel
        release=(1-p['edge_mix'])*release + p['edge_mix']*dry*pwin*edge
        cap=cap + p['cap_relief']*wet_low*edge
    elif fam=='protected_corridor':
        productive=sig(ctx.gpp_ann,p['guard_gpp_k'],p['guard_gpp_c'])
        guard=1-p['cold_guard_amp']*supp(ctx.t_ann,p['cold_k'],p['cold_c'])*supp(ctx.t_warm_frac,p['short_k'],p['short_c'])*productive
        phase=monsoon*rainbreak*sen
        release=release*(guard + p['phase_amp']*phase)
        cap=cap + p['cap_relief']*wet_low*phase
    else:
        raise ValueError(fam)
    fac=(1+p['boost']*release)*np.clip(cap,0.4,1.2)*(1-p['arid_amp']*arid)*cold_guard
    return np.power(np.clip(prod*fac,0,None),base_p['fire_exp']*p['exp_mult']).astype(np.float32)*ctx.land[None,:,:]

def summarize(ctx,pred):
    g=score(ctx,pred); regs={r:score(ctx,pred,ctx.region_masks[r]) for r in ctx.region_masks}
    weak=float(np.mean([regs[r]['overall'] for r in WEAK])); weakmin=float(min(regs[r]['overall'] for r in WEAK)); prot=float(min(regs[r]['overall'] for r in PROTECT))
    return g,regs,weak,weakmin,prot

def objective(ctx,pred):
    g,regs,weak,weakmin,prot=summarize(ctx,pred)
    # Score for the target frontier: retain Cand4-like global/spatial and Africa/BONA protection,
    # recover Cand3-like weak monsoon/temperate regions. Penalties are deliberately explicit so
    # successes/failures diagnose the next hypothesis rather than overfitting a single scalar.
    penalty=0.0
    penalty+=max(0,C4['overall']-g['overall'])*1.0
    penalty+=max(0,C3['spatial']-g['spatial'])*1.0
    penalty+=max(0,C3['bona']-regs['bona']['overall'])*0.7
    penalty+=max(0,C3['nhaf']-regs['nhaf']['overall'])*0.45
    penalty+=max(0,C3['shaf']-regs['shaf']['overall'])*0.45
    for r,w in [('nhsa',0.75),('shsa',0.75),('seas',0.45),('ceam',0.35),('tena',0.35)]:
        penalty+=max(0,C3[r]-regs[r]['overall'])*w
    return 0.66*g['overall']+0.13*g['spatial']+0.13*weak+0.04*weakmin+0.04*prot-penalty

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--family',choices=FAMILIES,required=True); ap.add_argument('--trials',type=int,default=500); ap.add_argument('--seed',type=int,default=20260524); ap.add_argument('--outdir',default='models/explore5'); ap.add_argument('--write-nc',action='store_true')
    args=ap.parse_args(); ctx=Ctx5(); base_p=json.load(open(REPO/'models/C/params.json'))['params']
    study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=args.seed,multivariate=True,group=True)); t0=time.time()
    def obj(trial): return objective(ctx,ed_transform(rate(ctx,args.family,sample(trial,args.family),base_p)))
    def cb(st,tr):
        if len(st.trials)%50==0: print(f"[cycle5] {args.family} {len(st.trials)}/{args.trials} best={st.best_value:.6f} elapsed={(time.time()-t0)/60:.1f}m", flush=True)
    study.optimize(obj,n_trials=args.trials,callbacks=[cb])
    p=study.best_params; raw=rate(ctx,args.family,p,base_p); pred=ed_transform(raw); g,regs,weak,weakmin,prot=summarize(ctx,pred)
    out={'family':args.family,'n_trials':len(study.trials),'seed':args.seed,'fast_objective':study.best_value,'fast_global':g,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'params':p,'diagnostics':{'raw_land_mean':float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),'raw_max':float(raw.max())},'mechanism_note':__doc__}
    outdir=REPO/args.outdir/args.family; outdir.mkdir(parents=True,exist_ok=True); (outdir/'result.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'family':args.family,'best':study.best_value,'global':g,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'out':str(outdir/'result.json')},indent=2))
    if args.write_nc:
        write_nc(ctx,pred,outdir/'burntArea.nc',f'cycle5 candidate {args.family}'); print(f"wrote {outdir/'burntArea.nc'}")
if __name__=='__main__': main()
