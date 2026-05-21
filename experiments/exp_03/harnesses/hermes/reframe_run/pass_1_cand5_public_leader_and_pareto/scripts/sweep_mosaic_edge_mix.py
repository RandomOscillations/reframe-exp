"""Deterministic edge-mix Pareto sweep for ED-Cand5 mosaic mechanism.

Ablation showed the optimized mosaic edge term buys broad regional repair but costs
some global/public score. This sweep varies only edge_mix between the pruned no-edge
state and the optimized full value, preserving all other parameters, to see whether a
middle Pareto point can preserve the new public/global lead while recovering more
NHSA/SHSA/SEAS/CEAM behavior.
"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_cycle5_mechanisms import Ctx5, rate, summarize
from explore_fire_candidates import ed_transform, write_nc
REPO=Path(__file__).resolve().parents[1]
FRACS=[0.0,0.25,0.5,0.75,1.0]

def main():
    ctx=Ctx5(); base_p=json.load(open(REPO/'models/C/params.json'))['params']; best=json.load(open(REPO/'models/explore5/mosaic_edge_release/result.json'))
    p0=best['params']; edge0=p0.get('edge_mix',0.0)
    outdir=REPO/'models/explore5/mosaic_edge_mix_sweep'; outdir.mkdir(parents=True,exist_ok=True)
    results={}
    for frac in FRACS:
        q=dict(p0); q['edge_mix']=edge0*frac; name=f'edgefrac_{frac:.2f}'.replace('.','p')
        raw=rate(ctx,'mosaic_edge_release',q,base_p); pred=ed_transform(raw); g,regs,weak,weakmin,prot=summarize(ctx,pred)
        sub=outdir/name; sub.mkdir(exist_ok=True); write_nc(ctx,pred,sub/'burntArea.nc',f'mosaic edge_mix sweep {frac}')
        results[name]={'frac':frac,'edge_mix':q['edge_mix'],'fast_global':g,'fast_regions':regs,'weak_mean':weak,'weak_min':weakmin,'protect_min':prot,'params':q}
        print(name,'edge_mix',q['edge_mix'],'overall',round(g['overall'],6),'spatial',round(g['spatial'],6),'weak',round(weak,6),'nhsa',round(regs['nhsa']['overall'],6),'shsa',round(regs['shsa']['overall'],6))
    (outdir/'result.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__': main()
