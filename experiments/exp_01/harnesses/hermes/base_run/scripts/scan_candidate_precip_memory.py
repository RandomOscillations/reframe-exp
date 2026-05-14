#!/usr/bin/env python3
"""Deterministic scan for antecedent precipitation moisture damping.

Hypothesis: fuel moisture and accessibility respond to recent rainfall memory, not
only the burn-month precipitation total. Use existing monthly precipitation and a
global rolling-memory blend in the existing precip dampener.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_modelC import sig, supp, hump
from optimize_modelC_ilamb_aligned import score_BA_ilamb, ed_transform, land_mask, drivers

# use explicit clean baseline params, not current candidate file
WARM_START=json.loads(Path('models/C/params.BASELINE-formal.json').read_text())['params']
WINDOWS=[1,2,3,4,6]
ALPHAS=[0.25,0.5,0.75,1.0]

def lagged_mean(arr, window):
    vals=[]
    for lag in range(1,window+1):
        x=np.empty_like(arr); x[:lag]=arr[:lag]; x[lag:]=arr[:-lag]; vals.append(x)
    return np.mean(vals,axis=0).astype(np.float32)

def fire_precip_mem(p,p_month_eff):
    d=drivers
    onset=sig(d['dbar'],p['k1'],p['D_low'])
    suppress=supp(d['dbar'],p['k2'],p['D_high'])
    p_floor=d['p_ann']/(d['p_ann']+p['P_half']+1e-12)
    p_damp=1.0/(1.0+p_month_eff/(p['pre_dampen_half']+1e-12))
    gpp_mod=hump(p['gpp_af']*d['gpp_monthly'],p['gpp_b'],p['gpp_d'])
    ign_mod=sig(d['t_air'],p['ign_k'],p['ign_c'])
    return np.power(np.clip(onset*suppress*p_floor*p_damp*gpp_mod*ign_mod,0,None),p['fire_exp']).astype(np.float32)

def main():
    rows=[]; best=None; t0=time.time()
    base=ed_transform(fire_precip_mem(WARM_START,drivers['p_month'])*land_mask[None,:,:])
    base_score,base_break=score_BA_ilamb(base)
    print(f"BASE proxy overall={base_score:.6f} {base_break}")
    cache={w:lagged_mean(drivers['p_month'],w) for w in WINDOWS}
    for w in WINDOWS:
      for a in ALPHAS:
        p_eff=((1-a)*drivers['p_month']+a*cache[w]).astype(np.float32)
        pred=ed_transform(fire_precip_mem(WARM_START,p_eff)*land_mask[None,:,:])
        overall,b=score_BA_ilamb(pred); rows.append({'precip_memory_window':w,'precip_memory_alpha':a,**b})
        print(f"scan window={w:2d} alpha={a:.2f} overall={overall:.6f} bias={b['bias']:.4f} rmse={b['rmse']:.4f} seas={b['seas']:.4f} spatial={b['spatial']:.4f}")
        if best is None or overall>best[0]: best=(overall,w,a,b)
    p=WARM_START.copy(); p.update(precip_memory_window=int(best[1]),precip_memory_alpha=float(best[2]))
    out={'hypothesis':'fuel moisture responds to recent precipitation memory','functional_form':'P_month_eff=(1-alpha)*P_month+alpha*mean(previous window months) in existing p_damp','scan_space':{'precip_memory_window':WINDOWS,'precip_memory_alpha':ALPHAS},'base_proxy':base_break,'best_proxy':best[3],'best_params':p,'rows':rows,'runtime_sec':time.time()-t0}
    Path('out_candidate_precip_memory.json').write_text(json.dumps(out,indent=2))
    print('BEST',best); print('wrote out_candidate_precip_memory.json')
if __name__=='__main__': main()
