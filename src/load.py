import logging
import pandas as pd
from src.config import DATA_DIR, INPUT_FILES, REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


def load_csv(name, path):
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path, dtype=str)

    missing = [col for col in REQUIRED_COLUMNS[name] if col not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")

    logger.info(f"Loaded {path.name}: {len(df)} rows")
    return df


def load_raw_data():
    raw = {}
    for name, file_name in INPUT_FILES.items():
        raw[name] = load_csv(name, DATA_DIR / file_name)
    return raw