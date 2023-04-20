"""Ingest category data."""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

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


def _parse_axfood_categories(data: Any) -> List[Dict[str, Any]]:
    if len(data["children"]) == 0:
        return data

    items = []
    data["children_id"] = [child["id"] for child in data["children"]]

    for child in data["children"]:
        items.append(_parse_axfood_categories(child))

    return items


def _flatten(lst: List[Any]) -> List[Any]:
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(_flatten(item))
        else:
            flattened.append(item)
    return flattened


def _get_flattend_axfood_categories(json_file: str) -> List[Dict[str, Any]]:
    with open(json_file, "r") as f:
        data = json.load(f)
    categories = []
    for item in data:
        categories.extend(_flatten(_parse_axfood_categories(item)))
    return categories


def ingest_axfood_categories(brand: str, json_file: str, date: str):
    """Ingest Axfood categories from JSON file to PostgreSQL table."""
    # TODO: Fix this, the `children_id` column is not correct
    categories = _get_flattend_axfood_categories(json_file)
    df = pl.DataFrame(categories)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name=f"{brand}_categories")
