"""Ablate ED-Cand4-pareto_guarded_corridor mechanism terms.

Variants neutralize one mechanistic term at a time while preserving the optimized
shared release-window parameters. This tests whether the apparent public/global gain
comes from interpretable pieces or gratuitous complexity.
"""
from pathlib import Path
import json, sys, argparse
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_pareto_release_candidates import Ctx4, rate, summarize
from explore_fire_candidates import ed_transform, write_nc
REPO=Path(__file__).resolve().parents[1]
VARIANTS=['full','no_guard','no_arid','no_hotboost','no_wetcap','no_corridor']

def params_for_variant(p, variant):
    q=dict(p)
    if variant=='no_guard':
        q['guard_amp']=0.0
    elif variant=='no_arid':
        q['arid_amp']=0.0
    elif variant=='no_hotboost':
        q['hotboost']=0.0
    elif variant=='no_wetcap':
        q['cap_amp']=0.0
    elif variant=='no_corridor':
        q['arid_amp']=0.0; q['hotboost']=0.0
    elif variant=='full':
        pass
    else:
        raise ValueError(variant)
    return q

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--write-nc',action='store_true'); args=ap.parse_args()
    ctx=Ctx4(); base_p=json.load(open(REPO/'models/C/params.json'))['params']
    best=json.load(open(REPO/'models/explore4/pareto_guarded_corridor/result.json'))
    p=best['params']; outdir=REPO/'models/explore4/pareto_guarded_corridor_ablation'; outdir.mkdir(parents=True,exist_ok=True)
    results={}
    for v in VARIANTS:
        q=params_for_variant(p,v)
        raw=rate(ctx,'pareto_guarded_corridor',q,base_p)
        pred=ed_transform(raw)
        g,regs,weak,weakmin,prot=summarize(ctx,pred)
        results[v]={'fast_global':g,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'params':q,'diagnostics':{'raw_land_mean':float((raw*ctx.w3*ctx.land[None,:,:]).sum()/((ctx.w3*ctx.land[None,:,:]).sum()+1e-12)),'raw_max':float(raw.max())}}
        if args.write_nc:
            sub=outdir/v; sub.mkdir(exist_ok=True)
            write_nc(ctx,pred,sub/'burntArea.nc',f'pareto_guarded_corridor ablation {v}')
    (outdir/'result.json').write_text(json.dumps(results,indent=2))
    for v,r in results.items():
        print(v, 'overall', round(r['fast_global']['overall'],6), 'spatial', round(r['fast_global']['spatial'],6), 'weak', round(r['weak_mean'],6), 'protect_min', round(r['protect_min'],6), 'bona', round(r['fast_regions']['bona']['overall'],6), 'nhsa', round(r['fast_regions']['nhsa']['overall'],6))
    print('wrote', outdir/'result.json')
if __name__=='__main__': main()
