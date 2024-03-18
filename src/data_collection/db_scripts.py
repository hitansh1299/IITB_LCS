import pandas as pd
import sqlite3
import os
from app import app

CONN = app.config['DATABASE']

#TODO: Make all queries SQL injection proof. https://realpython.com/prevent-python-sql-injection/
#TODO: Make queries Injection safe by adding checks to API layer.
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

def get_pm_data(table, columns: str | list, start: str, end:str) -> pd.DataFrame:
    if isinstance(columns, list):
        columns = ','.join([f'"{x}"' for x in columns])
    print(columns)
    with sqlite3.connect(CONN) as conn:
        query = f"SELECT timestamp,{columns} FROM {table} WHERE timestamp >= '{start}' AND timestamp <= '{end}'"
        print(query)
        df = pd.read_sql_query(query, conn)
    return df

def insert_live_data(table, timestamp, pm1, pm25, pm10, temp, rh, location):
    with sqlite3.connect(CONN) as conn:
        conn.cursor().execute(f'INSERT INTO {table} (timestamp, pm1, "pm2.5", pm10, temp, rh, location) VALUES (?,?,?,?,?,?,?)', (timestamp, pm1, pm25, pm10, temp, rh, location))

def get_latest_data(table):
    with sqlite3.connect(CONN) as conn:
        query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1"
        df = pd.read_sql_query(query, conn)
    return df