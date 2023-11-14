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

def get_table_data(table: str, start=None, end=None) -> pd.DataFrame:
    with sqlite3.connect(CONN) as conn:
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
    return df

def get_pm_data(table, column, start: str, end:str) -> pd.DataFrame:
    with sqlite3.connect(CONN) as conn:
        query = f'SELECT {column} FROM {table} WHERE timestamp >= {start} AND timestamp <= {end}'
        print(query)
        df = pd.read_sql_query(query, conn)
    return df
    