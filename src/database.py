import sqlite3
import pandas as pd
from src.config import SQL_DIR


def create_database(tables):
    conn = sqlite3.connect(':memory:')
    for name, df in tables.items():
        df.to_sql(name, conn, index=False)
    return conn


def run_sql_file(conn, file_name):
    sql = (SQL_DIR / file_name).read_text()
    return pd.read_sql_query(sql, conn)