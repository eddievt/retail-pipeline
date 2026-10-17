import logging
import pandas as pd

logger = logging.getLogger(__name__)


def run_checks(joined):
    checks = {
        'order_id_present': joined['order_id'].notna(),
        'customer_id_present': joined['customer_id'].notna(),
        'product_id_present': joined['product_id'].notna(),
        'order_id_unique': ~joined['order_id'].duplicated(keep=False),
        'order_date_valid': joined['order_date'].notna() & (joined['order_date'] <= pd.Timestamp.now()),
        'customer_matched': joined['customer_found'] | joined['customer_id'].isna(),
        'product_matched': joined['product_found'] | joined['product_id'].isna(),
        'quantity_positive': joined['quantity'] > 0,
        'price_positive': (joined['price'] > 0) | ~joined['product_found'],
    }
    return pd.DataFrame(checks)

CHECK_COLUMNS = {
    'order_id_present': 'order_id',
    'customer_id_present': 'customer_id',
    'product_id_present': 'product_id',
    'order_id_unique': 'order_id',
    'order_date_valid': 'order_date_raw',
    'customer_matched': 'customer_id',
    'product_matched': 'product_id',
    'quantity_positive': 'quantity',
    'price_positive': 'price',
}


def build_dq_report(joined, results):
    rows = []

    for check in results.columns:
        failed_count = int((~results[check]).sum())
        rows.append({
            'section': 'summary',
            'check_name': check,
            'status': 'PASS' if failed_count == 0 else 'FAIL',
            'rows_checked': len(results),
            'rows_failed': failed_count,
        })

    for check in results.columns:
        column = CHECK_COLUMNS[check]
        for _, row in joined[~results[check]].iterrows():
            value = row[column]
            rows.append({
                'section': 'exception',
                'check_name': check,
                'status': 'FAIL',
                'order_id': row['order_id'],
                'column': column,
                'failed_value': '(missing)' if pd.isna(value) else value,
            })

    return pd.DataFrame(rows, columns=['section', 'check_name', 'status', 'rows_checked',
                                       'rows_failed', 'order_id', 'column', 'failed_value'])

def reconcile(input_rows, clean_rows, failed_rows, duplicates_removed):
    accounted = clean_rows + failed_rows + duplicates_removed
    logger.info(f"Reconciliation: {input_rows} input = {clean_rows} clean + "
                f"{failed_rows} failed + {duplicates_removed} duplicates removed")
    if accounted != input_rows:
        raise ValueError(f"Reconciliation failed: {input_rows} input rows but {accounted} accounted for")