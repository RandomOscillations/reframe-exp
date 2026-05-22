from __future__ import annotations
import sys
import pandas as pd
metrics = ['Bias Score','RMSE Score','Seasonal Cycle Score','Spatial Distribution Score','Overall Score']
for p in sys.argv[1:]:
    df = pd.read_csv(p)
    print('\n' + p, df.shape, df.columns.tolist())
    sub = df[df.ScalarName.isin(metrics)]
    if 'Model' in df.columns and len(sys.argv) > 2:
        pass
    print(sub.pivot_table(index=['Model','Region'], columns='ScalarName', values='Data', aggfunc='first').round(4).to_string())
