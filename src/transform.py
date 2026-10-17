import logging
import pandas as pd
from src.database import run_sql_file

logger = logging.getLogger(__name__)


def join_tables(conn, expected_rows):
    joined = run_sql_file(conn, 'join_orders.sql')

    joined['order_date'] = pd.to_datetime(joined['order_date'])
    joined['customer_found'] = joined['customer_found'].astype(bool)
    joined['product_found'] = joined['product_found'].astype(bool)

    if len(joined) != expected_rows:
        raise ValueError(f"Join changed the row count from {expected_rows} to {len(joined)}")

    logger.info(f"Joined orders with customers and products: {len(joined)} rows")
    return joined