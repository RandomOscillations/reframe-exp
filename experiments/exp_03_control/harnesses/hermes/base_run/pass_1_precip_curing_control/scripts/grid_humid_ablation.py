from __future__ import annotations
import itertools, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire_explore as fe

d,obs=fe.load_drivers_obs(); base=fe.load_params(); land=(obs>0).any(axis=0)
lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32); masks=fe.region_masks(land)
weak=['ceam','euro','mide','tena','eqas','seas','shsa']
rows=[]
for ph,q in itertools.product([1500,2000,2500,3000,4000,6000,10000],[0.5,1,2,3,4]):
    p=dict(base); p.update({'P_humid':ph,'P_humid_q':q,'_family':'annual_humid_supp'})
    pred=fe.transform(fe.candidate_rate(d,p,'annual_humid_supp'),land)
    s=fe.proxy_scores(pred,obs,w3,masks)
    rows.append((0.6*s['global']['overall']+0.4*np.mean([s[k]['overall'] for k in weak]), s['global']['overall'], np.mean([s[k]['overall'] for k in weak]), ph,q, s['global']['ratio']))
for r in sorted(rows, reverse=True)[:20]: print(r)
