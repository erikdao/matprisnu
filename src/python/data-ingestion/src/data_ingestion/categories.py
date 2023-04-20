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


def _get_flattend_axfood_categories(json_file: str) -> List[Dict[str, Any]]:
    """Get flattend categories from Axfood JSON file."""
    with open(json_file, "r") as f:
        data = json.load(f)

    # Top level categories
    categories = []
    for item in data:
        if len(item["children"]) == 0:
            del item["children"]
            item["parent"] = None  # Top level categories have no parent
            item["level"] = 1
            categories.append(item)
            continue

        # Second level categories
        for child in item["children"]:
            child["parent"] = item["id"]
            if len(child["children"]) == 0:
                del child["children"]
                child["level"] = 2
                categories.append(child)
                continue

            # Third level categories
            for grandchild in child["children"]:
                grandchild["parent"] = child["id"]
                del grandchild["children"]  # No grandchildren
                grandchild["level"] = 3
                categories.append(grandchild)

            del child["children"]  # Remove children from second level
            child["level"] = 2
            categories.append(child)

        del item["children"]  # Remove children from top level
        item["parent"] = None  # Top level categories have no parent
        item["level"] = 1
        categories.append(item)

    return categories


def ingest_axfood_categories(brand: str, json_file: str, date: str):
    """Ingest Axfood categories from JSON file to PostgreSQL table."""
    # TODO: Fix this, the `children_id` column is not correct
    categories = _get_flattend_axfood_categories(json_file)
    df = pl.DataFrame(categories)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name=f"{brand}_categories")
