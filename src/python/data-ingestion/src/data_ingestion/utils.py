import os
from urllib.parse import urlparse

import polars as pl
import psycopg2.extras
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv(os.path.join(os.getcwd(), ".env"))


def write_to_db(df: pl.DataFrame, table_name: str):
    """Write a polars dataframe to a postgres table."""
    # first we convert polars date64 representation to python datetime objects
    for col in df:
        # only for date64
        if col.dtype == pl.Date:
            df = df.with_columns(col.dt.to_python_datetime())

    # create sql identifiers for the column names
    # we do this to safely insert this into a sql query
    columns = sql.SQL(",").join(sql.Identifier(name) for name in df.columns)

    # create placeholders for the values. These will be filled later
    values = sql.SQL(",").join([sql.Placeholder() for _ in df.columns])

    # prepare the insert query
    insert_stmt = sql.SQL("INSERT INTO {} ({}) VALUES({});").format(
        sql.Identifier(table_name), columns, values
    )

    # make a connection
    postgres_uri = urlparse(os.getenv("POSTGRES_WAREHOUSE_SILVER_URI"))
    username = postgres_uri.username
    password = postgres_uri.password
    database = postgres_uri.path[1:]
    hostname = postgres_uri.hostname
    port = postgres_uri.port
    conn = psycopg2.connect(
        database=database, user=username, password=password, host=hostname, port=port
    )
    cur = conn.cursor()

    # do the insert
    psycopg2.extras.execute_batch(cur, insert_stmt, df.rows())
    conn.commit()

    conn.close()
