"""Grid ablation for partial annual-precipitation wet-forest suppression on top of fixed Model C.

Mechanism: keep original C gates and multiply by a partial high-annual-precipitation
suppression term: floor + (1-floor)/(1+(P_ann/P_wet)^pow). A floor of 1 is the
exact baseline ablation; lower floors express stronger closed-canopy/wet-fuel
nonflammability. This tests whether regional improvements from annual_p_hump can
be retained without sacrificing global ILAMB.
"""
from pathlib import Path
import json, itertools
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_fire_candidates import Context, base_product, ed_transform, score, write_nc, WEAK_REGIONS

REPO=Path(__file__).resolve().parents[1]
ctx=Context()
p=json.load(open(REPO/'models/C/params.json'))['params']
prod=base_product(ctx,p)
rows=[]
P_wets=[1200,1600,2000,2600,3200,4000,6000,10000]
pows=[0.25,0.5,0.75,1.0,1.5,2.0,3.0]
floors=[0.70,0.80,0.85,0.90,0.93,0.95,0.97,0.99,1.0]
for P_wet,pow_,floor in itertools.product(P_wets,pows,floors):
    wet=1.0/(1.0+np.power(np.clip(ctx.d['p_ann']/(P_wet+1e-12),0,1e6),pow_))
    prod2=prod*(floor+(1-floor)*wet)
    rate=np.power(np.clip(prod2,0,None),p['fire_exp']).astype(np.float32)*ctx.land[None,:,:]
    pred=ed_transform(rate)
    g=score(ctx,pred)
    regs={r:score(ctx,pred,ctx.region_masks[r])['overall'] for r in WEAK_REGIONS}
    rows.append(dict(P_wet=P_wet,pow=pow_,floor=floor,global_overall=g['overall'],global_bias=g['bias'],global_rmse=g['rmse'],global_seasonal=g['seasonal'],global_spatial=g['spatial'],weak_mean=float(np.mean(list(regs.values()))),weak_min=float(np.min(list(regs.values()))),regs=regs))
# baseline row floor=1 appears many times; choose top constrained and top objective
for r in rows:
    r['objective']=0.85*r['global_overall']+0.10*r['weak_mean']+0.05*r['weak_min']
rows_sorted=sorted(rows,key=lambda r:r['objective'],reverse=True)
out=REPO/'models/explore/partial_wet_suppression'
out.mkdir(parents=True,exist_ok=True)
(out/'scan.json').write_text(json.dumps(rows_sorted,indent=2))
# choose best with global proxy within 0.001 of baseline proxy, and best objective overall
base=max([r for r in rows if r['floor']==1.0], key=lambda r:r['global_overall'])
constrained=[r for r in rows if r['global_overall']>=base['global_overall']-0.001]
best=max(constrained,key=lambda r:(r['weak_mean'],r['objective']))
for name,r in [('best_constrained',best),('best_objective',rows_sorted[0]),('baseline_proxy',base)]:
    (out/f'{name}.json').write_text(json.dumps(r,indent=2))
print('baseline',base)
print('best_constrained',best)
print('best_objective',rows_sorted[0])
# write constrained nc
r=best
wet=1.0/(1.0+np.power(np.clip(ctx.d['p_ann']/(r['P_wet']+1e-12),0,1e6),r['pow']))
prod2=prod*(r['floor']+(1-r['floor'])*wet)
rate=np.power(np.clip(prod2,0,None),p['fire_exp']).astype(np.float32)*ctx.land[None,:,:]
pred=ed_transform(rate)
write_nc(ctx,pred,out/'burntArea.nc','partial wet suppression candidate')
print(out/'burntArea.nc')
