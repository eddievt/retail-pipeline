import pandas as pd

df = pd.read_csv('raw_source/online_retail_full.csv', dtype={'Invoice': str, 'StockCode': str})
print(df.head())
print(df.columns)

missing_customers = df['Customer ID'].isna().sum()
print("Missing Customer ID:", missing_customers)
print("Missing %:", round(missing_customers / len(df) * 100, 1))

is_cancel = df['Invoice'].str.startswith('C')
print("Cancellation rows:", is_cancel.sum())
print(df[is_cancel]['Quantity'].describe())

dupes = df.duplicated().sum()
print("Exact duplicate rows:", dupes)

print(df['StockCode'].value_counts().head(5))
one_product = df[df['StockCode'] == '85123A']
print(one_product['Price'].value_counts().head(10))

countries_per_customer = df.groupby('Customer ID')['Country'].nunique()
print("Customers with more than 1 country:", (countries_per_customer > 1).sum())

starts_with_digit = df['StockCode'].str[0].str.isdigit()
not_products = df[~starts_with_digit]
print(not_products[['StockCode', 'Description']].drop_duplicates('StockCode'))