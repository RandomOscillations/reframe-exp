import pandas as pd
csv='ilamb/output_candidates_global/scalar_database.csv'
df=pd.read_csv(csv)
print(df.ScalarName.unique())
print(df[(df.Model=='ED-ModelC-final') & (df.Region=='global')][['ScalarName','Data']].to_string(index=False))
