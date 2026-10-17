from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'

INPUT_FILES = {
    'orders': 'orders.csv',
    'customers': 'customers.csv',
    'products': 'products.csv',
}

REQUIRED_COLUMNS = {
    'orders': ['order_id', 'customer_id', 'product_id', 'order_date', 'quantity'],
    'customers': ['customer_id', 'customer_name', 'email', 'country'],
    'products': ['product_id', 'product_name', 'category', 'price'],
}

KEY_COLUMNS = {
    'orders': 'order_id',
    'customers': 'customer_id',
    'products': 'product_id',
}

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
COUNTRY_ALIASES = {'UK': 'United Kingdom'}

SQL_DIR = PROJECT_ROOT / 'sql'

CLEAN_ORDER_COLUMNS = [
    'order_id', 'customer_id', 'customer_name', 'country',
    'product_id', 'product_name', 'category',
    'order_date', 'quantity', 'price', 'revenue',
]

ANALYSIS_SQL_FILES = [
    'revenue_by_country.sql',
    'top_10_products.sql',
    'top_5_customers.sql',
    'failed_records.sql',
]