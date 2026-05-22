from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire_explore as fe

# Deeper triage: characterize regions by allowed physical inputs and C0 error ratio.
d, obs = fe.load_drivers_obs(); p = fe.load_params(); land = (obs > 0).any(axis=0)
lat = np.arange(-89.5,90,1.0).astype(np.float32); w3 = np.broadcast_to(np.cos(np.deg2rad(lat))[None,:,None], obs.shape).astype(np.float32)
masks = fe.region_masks(land)
pred = fe.transform(np.power(np.clip(fe.base_rate(d,p),0,None),p['fire_exp']).astype(np.float32), land)
rows=[]
for key,mask in masks.items():
    ww = w3*mask[None,:,:]; sw=ww.sum()+1e-12
    def wm(a): return float((a*ww).sum()/sw)
    gpp=d['gpp_monthly']; dbar=d['dbar']; pann=d['p_ann']; pm=d['p_month']; tair=d['t_air']
    # dry-season current dryness proxy: fraction months p_month < p_ann/24 and dbar > threshold
    dryfrac=float((((pm < pann/24) & (dbar > 100))*ww).sum()/sw)
    hotdry=float((((pm < pann/24) & (tair > 20) & (dbar > 100))*ww).sum()/sw)
    rows.append({
      'region':key,'cells':int(mask.sum()),'pred_mean':wm(pred),'obs_mean':wm(obs),'ratio':wm(pred)/(wm(obs)+1e-12),
      'p_ann':wm(pann),'p_month':wm(pm),'dbar':wm(dbar),'t_air':wm(tair),'gpp':wm(gpp),
      'dryfrac':dryfrac,'hotdryfrac':hotdry,
      'gpp_p90':float(np.quantile(gpp[:,mask],0.9)) if mask.sum() else np.nan,
      'dbar_p90':float(np.quantile(dbar[:,mask],0.9)) if mask.sum() else np.nan,
      'pann_p90':float(np.quantile(pann[:,mask],0.9)) if mask.sum() else np.nan,
    })
df=pd.DataFrame(rows).sort_values('ratio', ascending=False)
Path('artifacts').mkdir(exist_ok=True)
df.to_csv('artifacts/region_allowed_input_diagnostics.csv',index=False)
print(df.round(4).to_string(index=False))
