import logging
import pandas as pd
from src.config import ANALYSIS_SQL_FILES
from src.database import run_sql_file

logger = logging.getLogger(__name__)


def run_analysis(conn, clean, failed):
    clean.to_sql('clean_orders', conn, index=False)
    failed.to_sql('failed_orders', conn, index=False)

    answers = []
    for file_name in ANALYSIS_SQL_FILES:
        result = run_sql_file(conn, file_name)
        result['value'] = result['value'].astype(object)
        result.insert(1, 'rank', range(1, len(result) + 1))
        answers.append(result)
        logger.info(f"Ran {file_name}: {len(result)} rows")

    return pd.concat(answers, ignore_index=True)