import logging
from src.config import OUTPUT_DIR, DATE_FORMAT

logger = logging.getLogger(__name__)


def split_orders(joined, results):
    passed = results.all(axis=1)
    return joined[passed], joined[~passed]


def write_csv(df, file_name):
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / file_name
    df.to_csv(path, index=False, date_format=DATE_FORMAT)
    logger.info(f"Wrote {file_name}: {len(df)} rows")