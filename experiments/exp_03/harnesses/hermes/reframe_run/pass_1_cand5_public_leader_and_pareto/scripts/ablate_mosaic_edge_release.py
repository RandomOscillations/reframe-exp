"""Ablate ED-Cand5-mosaic_edge_release.

The cycle-5 mosaic-edge candidate improved broad regional behavior while retaining
competitive global/public score. These variants neutralize one mechanism at a time:
edge replacement, wet-cap relief, hyperarid corridor, and cold/short-season guard.
"""
from pathlib import Path
import argparse, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_cycle5_mechanisms import Ctx5, rate, summarize
from explore_fire_candidates import ed_transform, write_nc
REPO=Path(__file__).resolve().parents[1]
VARIANTS=['full','no_edge_mix','no_cap_relief','no_arid','no_cold_guard','no_edge_and_relief']

def params_for_variant(p,v):
    q=dict(p)
    if v=='full': pass
    elif v=='no_edge_mix': q['edge_mix']=0.0
    elif v=='no_cap_relief': q['cap_relief']=0.0
    elif v=='no_arid': q['arid_amp']=0.0
    elif v=='no_cold_guard': q['cold_guard_amp']=0.0
    elif v=='no_edge_and_relief': q['edge_mix']=0.0; q['cap_relief']=0.0
    else: raise ValueError(v)
    return q

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--write-nc',action='store_true'); args=ap.parse_args()
    ctx=Ctx5(); base_p=json.load(open(REPO/'models/C/params.json'))['params']; best=json.load(open(REPO/'models/explore5/mosaic_edge_release/result.json'))
    outdir=REPO/'models/explore5/mosaic_edge_release_ablation'; outdir.mkdir(parents=True,exist_ok=True)
    results={}
    for v in VARIANTS:
        q=params_for_variant(best['params'],v); raw=rate(ctx,'mosaic_edge_release',q,base_p); pred=ed_transform(raw); g,regs,weak,weakmin,prot=summarize(ctx,pred)
        results[v]={'fast_global':g,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'params':q}
        if args.write_nc:
            sub=outdir/v; sub.mkdir(exist_ok=True); write_nc(ctx,pred,sub/'burntArea.nc',f'mosaic edge ablation {v}')
    (outdir/'result.json').write_text(json.dumps(results,indent=2))
    for v,r in results.items():
        print(v, 'overall', round(r['fast_global']['overall'],6), 'spatial', round(r['fast_global']['spatial'],6), 'weak', round(r['weak_mean'],6), 'bona', round(r['fast_regions']['bona']['overall'],6), 'nhsa', round(r['fast_regions']['nhsa']['overall'],6), 'shsa', round(r['fast_regions']['shsa']['overall'],6))
if __name__=='__main__': main()
