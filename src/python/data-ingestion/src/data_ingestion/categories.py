"""Ingest category data."""
from datetime import datetime

import polars as pl
from data_ingestion.utils import write_to_db


def ingest_coop_categories(json_file: str, date: str):
    """Ingest Coop categories from JSON file to PostgreSQL table."""
    df = pl.read_json(json_file)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name="coop_categories")
