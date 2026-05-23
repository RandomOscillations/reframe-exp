import pandas as pd

def extract(csv, derive_missing=False):
    df=pd.read_csv(csv)
    rows=[]
    for (model, region), sub in df.groupby(['Model','Region']):
        rec={'Model':model,'Region':region}
        for s in ['Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score']:
            vals=sub.loc[sub.ScalarName==s,'Data']
            if len(vals): rec[s]=float(vals.iloc[0])
        if derive_missing and 'Overall Score' not in rec:
            rec['Overall Score']=(2*rec.get('Bias Score',float('nan'))+2*rec.get('RMSE Score',float('nan'))+rec.get('Seasonal Cycle Score',float('nan'))+rec.get('Spatial Distribution Score',float('nan')))/6
            rec['Overall Note']='derived'
        else:
            rec['Overall Note']='official' if 'Overall Score' in rec else 'missing'
        rows.append(rec)
    return pd.DataFrame(rows)

g=extract('ilamb/output_candidates_global_full/scalar_database.csv')
r=extract('ilamb/output_candidates_regions/scalar_database.csv', derive_missing=True)
cols=['Model','Region','Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score','Overall Note']
g[cols].sort_values('Overall Score', ascending=False).to_csv('experiments/modelC_mechanism_search/official_global_scores.csv', index=False)
r[cols].sort_values(['Region','Overall Score'], ascending=[True,False]).to_csv('experiments/modelC_mechanism_search/official_regional_scores.csv', index=False)
print('GLOBAL')
print(g[cols].sort_values('Overall Score', ascending=False).to_string(index=False, float_format=lambda x:f'{x:.6f}'))
print('\nREGIONAL derived summary')
summary=r.groupby('Model')['Overall Score'].agg(['mean','min','max']).sort_values('mean', ascending=False)
print(summary.to_string(float_format=lambda x:f'{x:.6f}'))
print('\nBest by region')
idx=r.groupby('Region')['Overall Score'].idxmax()
print(r.loc[idx, cols].sort_values('Region').to_string(index=False, float_format=lambda x:f'{x:.6f}'))
