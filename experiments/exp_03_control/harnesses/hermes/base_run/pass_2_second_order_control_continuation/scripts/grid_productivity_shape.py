from __future__ import annotations
import json
from itertools import product
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire_explore as fe

# Deterministic productivity-shape probe.
# Tests whether changing the global GPP hump alone can solve weak-region overprediction
# without precipitation/wetness gates. This is intentionally low-dimensional because Model C
# already came from a broad 12-param fit; we are probing a mechanism, not re-fitting all params.
d, obs = fe.load_drivers_obs(); base=fe.load_params(); land=(obs>0).any(axis=0)
lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32)
masks=fe.region_masks(land); weak=['ceam','euro','mide','tena','eqas','seas','shsa']
vals=[]
for gpp_af,gpp_d,fire_exp,pre_half in product([0.25,0.35,0.46,0.65,0.9], [40,80,128.62113841235993,200,350,600], [0.45,0.575,0.70], [3,5.714386941567207,10,20]):
    p=dict(base)
    p.update(gpp_af=gpp_af,gpp_d=gpp_d,fire_exp=fire_exp,pre_dampen_half=pre_half)
    pred=fe.transform(fe.candidate_rate(d,p,'none'),land)
    s=fe.proxy_scores(pred,obs,w3,masks)
    obj=0.70*s['global']['overall']+0.30*np.mean([s[k]['overall'] for k in weak])
    vals.append((obj,p,s['global'],float(np.mean([s[k]['overall'] for k in weak])),s))
vals.sort(key=lambda x:x[0], reverse=True)
best=vals[0]
out={'family':'productivity_shape_grid','grid_count':len(vals),'best_value':best[0],'params':best[1],'global_proxy':best[2],'weak_mean_proxy':best[3], 'top10':[{'value':v[0],'params':v[1],'global':v[2],'weak_mean':v[3]} for v in vals[:10]]}
Path('artifacts/search2/productivity_shape_grid.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
