#!/usr/bin/env python3
"""Deterministic scan for lagged/antecedent GPP fuel availability extension.

Hypothesis: burned area responds to cured fuel accumulated before the burn month,
not solely same-month GPP. A global lagged-fuel blend may improve fire-season
phase and spatial fuel limitation without region routing.

Functional form: replace GPP_month in the existing GPP hump by
    GPP_eff = (1-alpha)*GPP_month + alpha*mean(GPP_{t-1}..GPP_{t-window})
with no calendar or regional branch. Existing inputs only.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import sig, supp, hump, load_drivers, load_gfed_1deg
from optimize_modelC_ilamb_aligned import score_BA_ilamb, ed_transform, land_mask, drivers, WARM_START

WINDOWS = [1,2,3,4,6,9,12]
ALPHAS = [0.25,0.5,0.75,1.0]

def lagged_mean(gpp, window):
    vals=[]
    for lag in range(1, window+1):
        x=np.empty_like(gpp)
        x[:lag]=gpp[:lag]  # avoid wrapping 2016 into 2001
        x[lag:]=gpp[:-lag]
        vals.append(x)
    return np.mean(vals, axis=0).astype(np.float32)

def fire_lag(p, gpp_eff):
    d=drivers
    onset=sig(d['dbar'],p['k1'],p['D_low'])
    suppress=supp(d['dbar'],p['k2'],p['D_high'])
    p_floor=d['p_ann']/(d['p_ann']+p['P_half']+1e-12)
    p_damp=1.0/(1.0+d['p_month']/(p['pre_dampen_half']+1e-12))
    gpp_mod=hump(p['gpp_af']*gpp_eff,p['gpp_b'],p['gpp_d'])
    ign_mod=sig(d['t_air'],p['ign_k'],p['ign_c'])
    product=onset*suppress*p_floor*p_damp*gpp_mod*ign_mod
    return np.power(np.clip(product,0,None),p['fire_exp']).astype(np.float32)

def main():
    t0=time.time(); rows=[]; best=None
    # base score via alpha=0 current GPP
    base_pred=ed_transform(fire_lag(WARM_START, drivers['gpp_monthly'])*land_mask[None,:,:])
    base_score,base_break=score_BA_ilamb(base_pred)
    print(f"BASE proxy overall={base_score:.6f} {base_break}")
    lag_cache={w:lagged_mean(drivers['gpp_monthly'],w) for w in WINDOWS}
    for w in WINDOWS:
      for a in ALPHAS:
        gpp_eff=((1-a)*drivers['gpp_monthly']+a*lag_cache[w]).astype(np.float32)
        pred=ed_transform(fire_lag(WARM_START,gpp_eff)*land_mask[None,:,:])
        overall,b=score_BA_ilamb(pred)
        row={'gpp_lag_window':w,'gpp_lag_alpha':a,**b}; rows.append(row)
        print(f"scan window={w:2d} alpha={a:.2f} overall={overall:.6f} bias={b['bias']:.4f} rmse={b['rmse']:.4f} seas={b['seas']:.4f} spatial={b['spatial']:.4f}")
        if best is None or overall>best[0]: best=(overall,w,a,b)
    p=WARM_START.copy(); p.update(gpp_lag_window=int(best[1]),gpp_lag_alpha=float(best[2]))
    out={'hypothesis':'fire responds to antecedent/cured productivity, not only same-month GPP','functional_form':'GPP_eff=(1-alpha)*GPP_month+alpha*mean(previous window months) inside existing GPP hump','scan_space':{'gpp_lag_window':WINDOWS,'gpp_lag_alpha':ALPHAS},'base_proxy':base_break,'best_proxy':best[3],'best_params':p,'rows':rows,'runtime_sec':time.time()-t0}
    Path('out_candidate_lagged_fuel.json').write_text(json.dumps(out,indent=2))
    print('BEST',best)
    print('wrote out_candidate_lagged_fuel.json')
if __name__=='__main__': main()
