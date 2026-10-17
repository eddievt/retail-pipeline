import logging
import pandas as pd
from src.config import DATE_FORMAT, COUNTRY_ALIASES

logger = logging.getLogger(__name__)


def clean_text(series):
    return series.str.strip().str.replace(r'\s+', ' ', regex=True)


def clean_orders(df):
    df = df.copy()
    df['order_id'] = clean_text(df['order_id'])
    df['customer_id'] = clean_text(df['customer_id'])
    df['product_id'] = clean_text(df['product_id']).str.upper()
    df['order_date_raw'] = df['order_date']
    df['order_date'] = pd.to_datetime(clean_text(df['order_date']), format=DATE_FORMAT, errors='coerce')
    df['quantity'] = pd.to_numeric(clean_text(df['quantity']), errors='coerce')
    return df

def clean_customers(df):
    df = df.copy()
    df['customer_id'] = clean_text(df['customer_id'])
    df['customer_name'] = clean_text(df['customer_name']).str.title()
    df['email'] = clean_text(df['email']).str.lower()
    df['country'] = clean_text(df['country']).replace(COUNTRY_ALIASES).str.title()
    return df


def clean_products(df):
    df = df.copy()
    df['product_id'] = clean_text(df['product_id']).str.upper()
    df['product_name'] = clean_text(df['product_name']).str.upper()
    df['category'] = clean_text(df['category']).str.title()
    df['price'] = pd.to_numeric(clean_text(df['price']), errors='coerce')
    return df

def remove_duplicates(name, df):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    logger.info(f"{name}: removed {removed} exact duplicate rows, {len(df)} rows remain")
    return df, removed


def keep_one_per_key(name, df, key):
    repeated = df[key].duplicated(keep='first')
    if repeated.any():
        logger.warning(f"{name}: {repeated.sum()} rows share a {key} with different data, keeping the first")
    return df[~repeated]


def clean_all(raw):
    orders = clean_orders(raw['orders'])
    customers = clean_customers(raw['customers'])
    products = clean_products(raw['products'])

    orders, duplicates_removed = remove_duplicates('orders', orders)
    customers, _ = remove_duplicates('customers', customers)
    products, _ = remove_duplicates('products', products)

    customers = keep_one_per_key('customers', customers, 'customer_id')
    products = keep_one_per_key('products', products, 'product_id')

    return orders, customers, products, duplicates_removed