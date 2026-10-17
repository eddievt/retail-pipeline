import pandas as pd
import os

def most_common(values):
    counts = values.value_counts()
    if counts.empty:
        return None
    return counts.index[0]




CATEGORY_KEYWORDS = {
    'Christmas': ['CHRISTMAS', 'XMAS'],
    'Fragrance': ['INCENSE', 'OIL BURNER', 'FRAGRANCE'],
    'Lighting': ['LIGHT', 'CANDLE', 'LANTERN'],
    'Kitchen': ['MUG', 'CUP', 'PLATE', 'BOWL', 'CAKE', 'TEA', 'JAR', 'SPOON',
                'COFFEE', 'WASHING UP', 'BOTTLE'],
    'Bags': ['BAG'],
    'Stationery': ['CARD', 'PAPER', 'NOTEBOOK', 'WRAP', 'STICKER', 'PENCIL',
                   'SHARPENER', 'ERASER', 'SKETCHBOOK', 'SCISSOR', 'PUNCH'],
    'Accessories': ['PARASOL', 'UMBRELLA', 'PURSE', 'PASSPORT', 'CASE',
                    'NECKLACE', 'BRACELET', 'EARRINGS', 'JEWELLERY'],
    'Home Decor': ['FRAME', 'CLOCK', 'CUSHION', 'SIGN', 'HEART', 'VASE', 'DOORMAT'],
    'Toys & Games': ['TOY', 'GAME', 'DOLL', 'PUZZLE'],
}


injected = []

def log_issue(table, issue, ids):
    injected.append({'table': table, 'issue': issue, 'count': len(ids), 'ids': ', '.join(ids)})

def get_category(name):
    if pd.isna(name):
        return None
    name = name.upper()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in name:
                return category
    return 'Other'



df = pd.read_csv('raw_source/online_retail_full.csv',
                 dtype={'Invoice': str, 'StockCode': str, 'Customer ID': str})
print("Loaded:", len(df))

df = df[df['StockCode'].str[0].str.isdigit()]
print("After keeping product codes:", len(df))

df = df[(df['InvoiceDate'] >= '2011-09-01') & (df['InvoiceDate'] < '2011-12-01')]
print("After keeping Sep-Nov 2011:", len(df))

customer_ids = df['Customer ID'].dropna().unique()
sampled_ids = pd.Series(customer_ids).sample(n=150, random_state=42)

with_customer = df[df['Customer ID'].isin(sampled_ids)]
no_customer = df[df['Customer ID'].isna()].sample(n=100, random_state=42)

df = pd.concat([with_customer, no_customer]).sort_index()
print("Rows with a sampled customer:", len(with_customer))
print("Rows with no customer:", len(no_customer))
print("Total sample:", len(df))

unique_rows = df.drop_duplicates().copy()
unique_rows['line_number'] = unique_rows.groupby('Invoice').cumcount() + 1
unique_rows['order_id'] = unique_rows['Invoice'] + '-' + unique_rows['line_number'].astype(str)

df = df.merge(unique_rows, on=list(df.columns), how='left')

print("Rows:", len(df))
print("Distinct order_ids:", df['order_id'].nunique())
print("Exact duplicate rows:", df.duplicated().sum())
print(df[['Invoice', 'StockCode', 'order_id']].head())


orders = df[['order_id', 'Customer ID', 'StockCode', 'InvoiceDate', 'Quantity']].rename(columns={
    'Customer ID': 'customer_id',
    'StockCode': 'product_id',
    'InvoiceDate': 'order_date',
    'Quantity': 'quantity'
})

orders['customer_id'] = orders['customer_id'].str.removesuffix('.0')

print("Orders:", len(orders))
print(orders.head())


products = df.groupby('StockCode').agg(
    product_name=('Description', most_common),
    price=('Price', most_common)
).reset_index().rename(columns={'StockCode': 'product_id'})

print("Products:", len(products))
print(products.head())


products['category'] = products['product_name'].apply(get_category)
print(products['category'].value_counts(dropna=False))



customers = df.dropna(subset=['Customer ID']).groupby('Customer ID').agg(
    country=('Country', most_common)
).reset_index().rename(columns={'Customer ID': 'customer_id'})

customers['customer_id'] = customers['customer_id'].str.removesuffix('.0')
customers['customer_name'] = 'Customer ' + customers['customer_id']
customers['email'] = 'customer' + customers['customer_id'] + '@example.com'

customers = customers[['customer_id', 'customer_name', 'email', 'country']]

print("Customers:", len(customers))
print(customers.head())
print(customers['country'].value_counts())

picked = orders.sample(n=21, random_state=1).index
bad_dates = picked[0:6]
bad_customers = picked[6:11]
bad_products = picked[11:16]
messy_ids = picked[16:21]

orders.loc[bad_dates, 'order_date'] = ['2011-02-30 10:00:00', 'not a date', '2011-13-05 09:00:00',
                                        None, None, '2030-01-01 12:00:00']
log_issue('orders', 'invalid or missing order_date', orders.loc[bad_dates, 'order_id'].tolist())

orders.loc[bad_customers, 'customer_id'] = '99999'
log_issue('orders', 'customer_id not in customers table', orders.loc[bad_customers, 'order_id'].tolist())

orders.loc[bad_products, 'product_id'] = '99999X'
log_issue('orders', 'product_id not in products table', orders.loc[bad_products, 'order_id'].tolist())

orders.loc[messy_ids, 'product_id'] = ' ' + orders.loc[messy_ids, 'product_id'].str.lower() + ' '
log_issue('orders', 'product_id with spaces/lowercase (fixable)', orders.loc[messy_ids, 'order_id'].tolist())


picked = products.sample(n=10, random_state=2).index
zero_price = picked[0:2]
negative_price = picked[2:3]
missing_price = picked[3:4]
messy_names = picked[4:7]
messy_categories = picked[7:10]

products.loc[zero_price, 'price'] = 0
log_issue('products', 'price is zero', products.loc[zero_price, 'product_id'].tolist())

products.loc[negative_price, 'price'] = -1.25
log_issue('products', 'price is negative', products.loc[negative_price, 'product_id'].tolist())

products.loc[missing_price, 'price'] = None
log_issue('products', 'price is missing', products.loc[missing_price, 'product_id'].tolist())

products.loc[messy_names, 'product_name'] = products.loc[messy_names, 'product_name'].str.lower()
log_issue('products', 'product_name in lowercase', products.loc[messy_names, 'product_id'].tolist())

products.loc[messy_categories, 'category'] = ' ' + products.loc[messy_categories, 'category'].str.lower() + ' '
log_issue('products', 'category with spaces/lowercase', products.loc[messy_categories, 'product_id'].tolist())

dup_products = products.sample(n=2, random_state=3)
products = pd.concat([products, dup_products], ignore_index=True)
log_issue('products', 'exact duplicate row', dup_products['product_id'].tolist())


uk_customers = customers[customers['country'] == 'United Kingdom']
picked = uk_customers.sample(n=10, random_state=4).index
messy_countries = picked[0:3]
missing_country = picked[3:4]
upper_names = picked[4:6]
missing_email = picked[6:8]
bad_email = picked[8:9]
format_dup = picked[9:10]

customers.loc[messy_countries, 'country'] = ['united kingdom', 'UK', ' United Kingdom ']
log_issue('customers', 'country spelled inconsistently', customers.loc[messy_countries, 'customer_id'].tolist())

customers.loc[missing_country, 'country'] = None
log_issue('customers', 'country is missing', customers.loc[missing_country, 'customer_id'].tolist())

customers.loc[upper_names, 'customer_name'] = customers.loc[upper_names, 'customer_name'].str.upper()
log_issue('customers', 'customer_name in uppercase', customers.loc[upper_names, 'customer_id'].tolist())

customers.loc[missing_email, 'email'] = None
log_issue('customers', 'email is missing', customers.loc[missing_email, 'customer_id'].tolist())

customers.loc[bad_email, 'email'] = customers.loc[bad_email, 'email'].str.replace('@', '')
log_issue('customers', 'email has no @', customers.loc[bad_email, 'customer_id'].tolist())

copy_row = customers.loc[format_dup].copy()
copy_row['customer_name'] = copy_row['customer_name'].str.upper()
dup_customers = customers.sample(n=2, random_state=5)
customers = pd.concat([customers, copy_row, dup_customers], ignore_index=True)
log_issue('customers', 'duplicate that differs only in formatting', copy_row['customer_id'].tolist())
log_issue('customers', 'exact duplicate row', dup_customers['customer_id'].tolist())



os.makedirs('data', exist_ok=True)
os.makedirs('docs', exist_ok=True)

orders.to_csv('data/orders.csv', index=False)
customers.to_csv('data/customers.csv', index=False)
products.to_csv('data/products.csv', index=False)
pd.DataFrame(injected).to_csv('docs/injected_issues.csv', index=False)

print("\n=== Final counts ===")
print("orders.csv:   ", len(orders), "rows (EY minimum: 500)")
print("customers.csv:", len(customers), "rows (EY minimum: 100)")
print("products.csv: ", len(products), "rows (EY minimum: 50)")

print("\n=== Injected issues ===")
print(pd.DataFrame(injected)[['table', 'issue', 'count']])