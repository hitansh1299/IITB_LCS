import pandas as pd
import sqlite3
import os
from app import app

CONN = app.config['DATABASE']

#TODO: Make all queries SQL injection proof. https://realpython.com/prevent-python-sql-injection/

def insert_df(df: pd.DataFrame, table:str):
    with sqlite3.connect(CONN) as conn:
        df.to_sql(table, conn, if_exists='append', index=False)

def delete_by_filename(filename):
    with sqlite3.connect(CONN) as conn:
        conn.execute(f'DELETE FROM Grimm WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM Partector WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM N3 WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM Atmos WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM PurpleAir WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM clean_purpleair WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM clean_n3 WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM clean_grimm WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM clean_partector WHERE filename LIKE "%{filename}%"')
        conn.execute(f'DELETE FROM clean_atmos WHERE filename LIKE "%{filename}%"')

def get_table_data(table: str, start=None, end=None) -> pd.DataFrame:
    with sqlite3.connect(CONN) as conn:
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
    return df

def get_pm_data(table, column, start: str, end:str) -> pd.DataFrame:
    with sqlite3.connect(CONN) as conn:
        query = f"SELECT timestamp,{column} FROM {table} WHERE timestamp >= '{start}' AND timestamp <= '{end}'"
        # print(query)
        df = pd.read_sql_query(query, conn)
    return df
    