from __future__ import annotations
import pandas as pd
runs={
 'C0':'ilamb/output_modelC_regions/scalar_database.csv',
 'H1_retuned':'ilamb/output_H1_regions/scalar_database.csv',
 'H1m_mild':'ilamb/output_H1m_regions/scalar_database.csv',
 'H2_wetmonth':'ilamb/output_H2_regions/scalar_database.csv',
 'H3_contrast':'ilamb/output_H3_regions/scalar_database.csv',
}
metrics=['Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score']
frames=[]
for rid,path in runs.items():
 df=pd.read_csv(path)
 sub=df[df.ScalarName.isin(metrics)].copy(); sub['Run']=rid
 frames.append(sub)
all=pd.concat(frames)
piv=all.pivot_table(index=['Run','Region'], columns='ScalarName', values='Data', aggfunc='first')
piv.to_csv('artifacts/official_candidate_regional_scores.csv')
print(piv.loc[(slice(None),'global'),:].round(4).to_string())
print('\nOverall by weak regions:')
ov=piv['Overall Score'].unstack(0)
print(ov.loc[['euro','ceam','tena','mide','seas','shsa','eqas','global']].round(4).to_string())
