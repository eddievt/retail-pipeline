import logging
import sys

from src.load import load_raw_data
from src.profiling import write_profiling_summary
from src.clean import clean_all

from src.database import create_database
from src.transform import join_tables
from src.checks import run_checks, build_dq_report, reconcile
from src.outputs import split_orders, write_csv
from src.config import CLEAN_ORDER_COLUMNS
from src.analysis import run_analysis

logger = logging.getLogger('pipeline')


def main():
    logger.info("Pipeline started")

    raw = load_raw_data()
    write_profiling_summary(raw)

    orders, customers, products, duplicates_removed = clean_all(raw)

    conn = create_database({'orders': orders, 'customers': customers, 'products': products})
    joined = join_tables(conn, expected_rows=len(orders))

    results = run_checks(joined)

    clean, failed = split_orders(joined, results)
    reconcile(len(raw['orders']), len(clean), len(failed), duplicates_removed)

    write_csv(clean[CLEAN_ORDER_COLUMNS], 'clean_orders.csv')
    write_csv(build_dq_report(joined, results), 'dq_report.csv')

    write_csv(run_analysis(conn, clean[CLEAN_ORDER_COLUMNS], failed), 'analysis_results.csv')
    conn.close()
    


    logger.info("Pipeline completed successfully")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S',
    )
    try:
        main()
    except Exception as error:
        logger.error(f"Pipeline FAILED: {error}")
        sys.exit(1)