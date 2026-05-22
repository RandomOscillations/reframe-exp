from __future__ import annotations
import itertools, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire_explore as fe

def run(family, grid):
 d,obs=fe.load_drivers_obs(); base=fe.load_params(); land=(obs>0).any(axis=0)
 lat=np.arange(-89.5,90,1.0).astype(np.float32); w3=np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32); masks=fe.region_masks(land)
 weak=['ceam','euro','mide','tena','eqas','seas','shsa']
 rows=[]
 for vals in grid:
  p=dict(base); p['_family']=family; p.update(vals)
  pred=fe.transform(fe.candidate_rate(d,p,family),land); s=fe.proxy_scores(pred,obs,w3,masks)
  rows.append((0.6*s['global']['overall']+0.4*np.mean([s[k]['overall'] for k in weak]),s['global']['overall'],np.mean([s[k]['overall'] for k in weak]),s['global']['ratio'],vals))
 print('\n',family)
 for r in sorted(rows, reverse=True)[:15]: print(r)

run('wetmonth_logistic',[{'wet_k':k,'wet_c':c} for k,c in itertools.product([0.005,0.01,0.02,0.05,0.1],[20,50,100,150,250])])
run('seasonal_contrast',[{'contrast_eps':e,'contrast_q':q} for e,q in itertools.product([0.5,2,5,10,20],[0.25,0.5,1,2,4])])
