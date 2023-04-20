"""Ingest category data."""
import json
import os
from datetime import datetime

import polars as pl
from data_ingestion.utils import write_to_db


def ingest_coop_categories(json_file: str, date: str):
    """Ingest Coop categories from JSON file to PostgreSQL table."""
    df = pl.read_json(json_file)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name="coop_categories")


def ingest_ica_categories(json_file: str, date: str):
    """Ingest ICA categories from JSON file to PostgreSQL table."""
    with open(json_file, "r") as f:
        data = json.load(f)
    categories = list(data.values())

    df = pl.DataFrame(categories)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    # The convention of json_file is `storeId_cartegories.json`
    store_id = os.path.basename(json_file).split("_")[0]
    df = df.with_columns((pl.lit(store_id).alias("storeId")))

    write_to_db(df, table_name="ica_categories")
