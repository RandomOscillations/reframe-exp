from __future__ import annotations
import json
from itertools import product
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire_explore as fe

d,obs=fe.load_drivers_obs(); base=fe.load_params(); land=(obs>0).any(axis=0)
lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32)
masks=fe.region_masks(land)
weak=['ceam','euro','mide','tena','eqas','seas','shsa']
# Mechanistic grid: low precipitation x low GPP fuel-discontinuity suppression.
vals=[]
for arid_alpha, arid_c, gppmin_c in product([0.25,0.5,0.75,1.0],[150,250,400,600],[0.1,0.25,0.5,0.8]):
    p=dict(base,_family='hyperarid_fuel',arid_alpha=arid_alpha,arid_k=0.02,arid_c=arid_c,gppmin_k=8.0,gppmin_c=gppmin_c)
    pred=fe.transform(fe.candidate_rate(d,p,'hyperarid_fuel'),land)
    s=fe.proxy_scores(pred,obs,w3,masks)
    obj=0.55*s['global']['overall']+0.45*np.mean([s[k]['overall'] for k in weak])
    vals.append((obj,p,s['global'],float(np.mean([s[k]['overall'] for k in weak]))))
vals.sort(key=lambda x:x[0], reverse=True)
out={'family':'hyperarid_fuel','grid_count':len(vals),'best_value':vals[0][0],'params':vals[0][1],'global_proxy':vals[0][2],'weak_mean_proxy':vals[0][3]}
Path('artifacts/search2').mkdir(parents=True,exist_ok=True)
Path('artifacts/search2/hyperarid_fuel_grid.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
