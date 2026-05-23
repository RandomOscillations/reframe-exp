import json, copy, csv
from pathlib import Path
import sys
sys.path.insert(0,'scripts')
import run_modelC_mechanism_experiments as exp

indir=Path('experiments/modelC_mechanism_search')
rows=[]
ablations={
 'precip_shape': {'p_floor_exp':1.0,'p_damp_exp':1.0},
 'temp_window': {'heat_k':1e-9,'heat_c':1e9},
 'humid_suppression': {'humid_k':1e-9,'humid_c':1e9},
 'fuel_moisture_balance': {'relief_amp':0.0},
}
for fam, neutral in ablations.items():
    r=json.load(open(indir/f'{fam}.json'))
    formula=exp.FAMILIES[fam][0]
    for label, params in [('full',r['params']),('ablated', {**r['params'], **neutral})]:
        pred=exp.predict(formula, params)
        obj,g,regs=exp.score_candidate(pred)
        ros=[v['overall'] for v in regs.values()]
        rows.append({'family':fam,'case':label,'objective':obj,'global_overall_proxy':g['overall'],'global_bias_proxy':g['bias'],'global_rmse_proxy':g['rmse'],'global_seasonal_proxy':g['seasonal'],'global_spatial_proxy':g['spatial'],'regional_mean_proxy':sum(ros)/len(ros),'regional_min_proxy':min(ros)})
with open(indir/'proxy_ablation_scores.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
for row in rows:
    print(row)
