"""Ablations for ED-Cand2-curing_window.

The accepted-looking mechanism is a boost factor:
  1 + boost * drydown * dry_now * annual_precip_window * monthly_gpp_window
with a modest exponent multiplier. This script writes deterministic ablation NetCDFs
so official ILAMB can distinguish whether the gain comes from the curing pulse,
windowing, or mere exponent/rescale.
"""
from pathlib import Path
import json, shutil, sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_second_order_candidates import Context, rate_for, FAMILIES
from explore_second_order_candidates import sig, supp, ed_transform, write_nc, score
from explore_fire_candidates import base_product

REPO=Path(__file__).resolve().parents[1]
ctx=Context()
base_p=json.load(open(REPO/'models/C/params.json'))['params']
res=json.load(open(REPO/'models/explore2/curing_window/result.json'))
p=res['params']
d=ctx.d
prod=base_product(ctx,base_p)
drydown=sig(ctx.d_delta,p['dd_k'],p['dd_c'])
dry_now=sig(d['dbar'],p['dry_k'],p['dry_c'])
mid_p=sig(d['p_ann'],p['p_low_k'],p['p_low_c'])*supp(d['p_ann'],p['p_high_k'],p['p_high_c'])
gpp=d['gpp_monthly']
gpp_mid=sig(gpp,p['gpp_lo_k'],p['gpp_lo_c'])*supp(gpp,p['gpp_hi2_k'],p['gpp_hi2_c'])

def make(name, pulse, exp_mult=None, boost=None):
    if exp_mult is None: exp_mult=p['exp_mult']
    if boost is None: boost=p['boost']
    fac=1.0+boost*pulse
    rate=np.power(np.clip(prod*fac,0,None),base_p['fire_exp']*exp_mult).astype(np.float32)*ctx.land[None,:,:]
    pred=ed_transform(rate)
    out=REPO/'models/explore2/curing_window_ablations'/name
    out.mkdir(parents=True,exist_ok=True)
    write_nc(ctx,pred,out/'burntArea.nc',f'curing window ablation {name}')
    glob=score(ctx,pred)
    regs={r:score(ctx,pred,ctx.region_masks[r])['overall'] for r in ctx.region_masks}
    meta={'name':name,'fast_global':glob,'fast_regions':regs,'exp_mult':exp_mult,'boost':boost,
          'pulse_mean':float((pulse*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),
          'pulse_max':float(np.max(pulse))}
    (out/'meta.json').write_text(json.dumps(meta,indent=2))
    dst=REPO/'ilamb/MODELS'/f'ED-Cand2Abl-{name}'
    dst.mkdir(parents=True,exist_ok=True)
    shutil.copy2(out/'burntArea.nc',dst/'burntArea.nc')
    print(name, glob)

pulse_full=drydown*dry_now*mid_p*gpp_mid
make('full',pulse_full)
make('exp_only',pulse_full,boost=0.0)
make('pulse_no_exp',pulse_full,exp_mult=1.0)
make('no_gpp_window',drydown*dry_now*mid_p)
make('no_p_window',drydown*dry_now*gpp_mid)
make('no_drydown',dry_now*mid_p*gpp_mid)
make('no_dry_now',drydown*mid_p*gpp_mid)
make('dry_only',drydown*dry_now)
