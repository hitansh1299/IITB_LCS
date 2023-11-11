import pandas as pd
import sqlite3
import os
from app import app

CONN = app.config['DATABASE']

def insert_df(df: pd.DataFrame, table:str):
    with sqlite3.connect(CONN) as conn:
        df.to_sql(table, conn, if_exists='append', index=False)

def delete_by_filename(filename):
    with sqlite3.connect(CONN) as conn:
        conn.execute(f'DELETE * WHERE filename = {filename}')

def get_all_data(table: str) -> pd.DataFrame:
    with sqlite3.connect(CONN) as conn:
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
    return df
    