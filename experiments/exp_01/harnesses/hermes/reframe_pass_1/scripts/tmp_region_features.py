from ILAMB.Regions import Regions
from types import SimpleNamespace
import numpy as np, json
from scripts.reproduce_modelC import load_drivers, load_gfed_1deg, fire_C
p=json.load(open('models/C/params.json'))['params']
d=load_drivers(); obs=load_gfed_1deg(); rate=fire_C(d,p)
lat=np.arange(-89.5,90,1.0); lon=np.arange(-179.5,180,1.0)
var=SimpleNamespace(lat=lat, lon=lon, lat_bnds=None, lon_bnds=None, spatial=True, ndata=None)
r=Regions(); land=(obs>0).any(axis=0)
for reg in ['tena','ceam','nhsa','shsa','euro','mide','nhaf','shaf','seas','eqas','aust','bona']:
    mask=r.getMask(reg,var)
    inside=np.logical_and(np.logical_not(mask), land)
    print(reg,'cells',inside.sum(),'pann',float(np.nanmean(d['p_ann'][:,inside])),'dbar',float(np.nanmean(d['dbar'][:,inside])),'tair',float(np.nanmean(d['t_air'][:,inside])),'gpp',float(np.nanmean(d['gpp_monthly'][:,inside])),'rate',float(np.nanmean(rate[:,inside])),'obs',float(np.nanmean(obs[:,inside])))
