from __future__ import annotations
import sys
import pandas as pd
metrics = ['Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score']
for p in sys.argv[1:]:
    df = pd.read_csv(p)
    print('\n' + p, df.shape, df.columns.tolist())
    mask = (df.Model == 'ED-ModelC-final') & (df.ScalarName.isin(metrics))
    sub = df[mask]
    print('sub rows', len(sub))
    print(sub.pivot(index='Region', columns='ScalarName', values='Data').round(4).to_string())
