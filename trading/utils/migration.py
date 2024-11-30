# -*- coding:utf-8 -*-
import os

import fire
import polars as pl
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

# 데이터베이스 연결 정보
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        print("Connected to TimescaleDB")
        return conn
    except Exception as e:
        print(f"Error connecting to TimescaleDB: {e}")
        exit()


# 2. 테이블 생성 (없으면 생성)
def create_table_if_not_exists(conn, table_name: str):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS \"{table_name}\" (
        date TIMESTAMP NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume REAL,
        PRIMARY KEY (date)
    );
    """
    create_hypertable_query = f"""
    SELECT create_hypertable('\"{table_name}\"', 'date', if_not_exists => TRUE, create_default_indexes => FALSE);
    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
        cursor.execute(create_hypertable_query)
        conn.commit()
        print(f"Table '{table_name}' is ready.")


# 3. Parquet 데이터 읽기
def read_parquet(file_path):
    try:
        df = pl.read_parquet(file_path).unique(subset=["Date"])
        print(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        print(f"Error reading Parquet file: {e}")
        exit()


# 4. 데이터 삽입
def insert_data(conn, dataframe, table_name: str):
    insert_query = f"""
    INSERT INTO \"{table_name}\" (date, open, high, low, close, volume)
    VALUES %s
    """
    values = [
        (row["Date"], row["open"], row["high"], row["low"], row["close"], row["volume"])
        for row in dataframe.iter_rows(named=True)
    ]
    try:
        with conn.cursor() as cursor:
            execute_values(cursor, insert_query, values)
            conn.commit()
            print(f"Inserted {len(values)} rows into {table_name}.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()


class Migration:
    def __init__(self):
        self.conn = connect_to_db()

    def run(self, file_path: str, table_name: str):
        try:
            create_table_if_not_exists(self.conn, table_name)
            df = read_parquet(file_path)
            insert_data(self.conn, df, table_name)
        finally:
            self.conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    fire.Fire(Migration)
