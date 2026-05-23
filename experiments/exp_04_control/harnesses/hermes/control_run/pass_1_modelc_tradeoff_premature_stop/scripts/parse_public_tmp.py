import pandas as pd
csv='public_benchmark_clean/ilamb/output_with_ED-ModelC-final-reproduced/scalar_database.csv'
df=pd.read_csv(csv)
rows=[]
for model, sub in df[df.Region=='global'].groupby('Model'):
    rec={'Model':model}
    for s in ['Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score']:
        vals=sub.loc[sub.ScalarName==s,'Data']
        if len(vals): rec[s]=float(vals.iloc[0])
    rows.append(rec)
out=pd.DataFrame(rows).sort_values('Overall Score', ascending=False)
out.to_csv('experiments/modelC_mechanism_search/public_benchmark_final_reproduced.csv',index=False)
print(out.to_string(index=False,float_format=lambda x:f'{x:.6f}'))
