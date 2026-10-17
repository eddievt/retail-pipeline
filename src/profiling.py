import logging
from src.config import OUTPUT_DIR, KEY_COLUMNS
import pandas as pd

logger = logging.getLogger(__name__)


def profile_table(name, df):
    key = KEY_COLUMNS[name]
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'exact_duplicate_rows': int(df.duplicated().sum()),
        'distinct_keys': int(df[key].nunique()),
        'duplicate_key_values': int(df[key].dropna().duplicated().sum()),
    }


def find_quality_issues(raw):
    orders, customers, products = raw['orders'], raw['customers'], raw['products']
    issues = []

    def add(table, issue, mask):
        issues.append((table, issue, int(mask.sum())))

    dates = pd.to_datetime(orders['order_date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    add('orders', 'order_date missing or not a valid date', dates.isna())
    add('orders', 'order_date in the future', dates > pd.Timestamp.now())

    qty = pd.to_numeric(orders['quantity'], errors='coerce')
    add('orders', 'quantity zero or negative', qty <= 0)

    add('orders', 'customer_id not found in customers',
        orders['customer_id'].notna() & ~orders['customer_id'].isin(customers['customer_id']))
    add('orders', 'product_id not found in products',
        ~orders['product_id'].isin(products['product_id']))

    price = pd.to_numeric(products['price'], errors='coerce')
    add('products', 'price missing, zero or negative', price.isna() | (price <= 0))

    for name, df in raw.items():
        for column in df.columns:
            text = df[column].dropna()
            messy = (text != text.str.strip()) | text.str.contains('  ', regex=False)
            if messy.sum() > 0:
                add(name, f'{column} has extra spaces', messy)

    add('products', 'product_name not in uppercase',
        products['product_name'].dropna() != products['product_name'].dropna().str.upper())
    for name, column in [('customers', 'customer_name'), ('customers', 'country'), ('products', 'category')]:
        text = raw[name][column].dropna()
        add(name, f'{column} has inconsistent casing or spelling', text != text.str.strip().str.title())

    add('customers', 'email missing @', ~customers['email'].dropna().str.contains('@'))

    return issues


def write_profiling_summary(raw):
    lines = ['# Profiling Summary', '',
             'Statistics on the raw source files, before any cleaning.', '',
             '## Overview', '',
             '| Table | Rows | Columns | Exact duplicate rows | Distinct keys | Duplicate key values |',
             '|---|---|---|---|---|---|']

    for name, df in raw.items():
        p = profile_table(name, df)
        lines.append(f"| {name} | {p['rows']} | {p['columns']} | {p['exact_duplicate_rows']} "
                     f"| {p['distinct_keys']} | {p['duplicate_key_values']} |")

    lines += ['', '## Missing values by column', '']
    for name, df in raw.items():
        lines += [f'### {name}', '', '| Column | Missing | % of rows |', '|---|---|---|']
        for column, count in df.isna().sum().items():
            lines.append(f'| {column} | {count} | {count / len(df) * 100:.2f}% |')
        lines.append('')
    lines += ['## Identified quality issues', '',
            'Counted on the raw data. Each one is handled later by cleaning or by a DQ check.', '',
            '| Table | Issue | Rows affected |', '|---|---|---|']
    for table, issue, count in find_quality_issues(raw):
        lines.append(f'| {table} | {issue} | {count} |')

    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / 'profiling_summary.md'
    path.write_text('\n'.join(lines))
    logger.info(f"Wrote {path.name}")