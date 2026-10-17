import pandas as pd

sheets = pd.read_excel('raw_source/online_retail_II.xlsx', sheet_name =None)

df = pd.concat(sheets.values(), ignore_index=True)

print("Rows:", len(df))

df.to_csv('raw_source/online_retail_full.csv', index=False)

