"""Ingest store data."""
import os
from datetime import datetime

import polars as pl
from data_ingestion.utils import write_to_db
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))


def ingest_coop_stores(json_file: str, date: str):
    df = pl.read_json(json_file)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    conn = os.getenv("POSTGRES_WAREHOUSE_SILVER_URI")
    df.write_database("coop_stores", conn, if_exists="append")


def ingest_axfood_stores(brand: str, json_file: str, date: str):
    def flatten_df(df: pl.DataFrame) -> pl.DataFrame:
        # Flatten the geoPoint column by first createing a new dataframe with the unnested column
        geo_df = df.select(["storeId", "geoPoint"])
        geo_df = geo_df.unnest("geoPoint")
        geo_df = geo_df.rename(
            {"latitude": "geoPoint_latitude", "longitude": "geoPoint_longitude"}
        )

        # Flatten the address column by first createing a new dataframe with the unnested column
        address_df = df.select(["storeId", "address"])
        address_df = address_df.unnest("address")
        cols = [col for col in address_df.columns if col != "storeId"]
        address_df = address_df.rename({col: f"address_{col}" for col in cols})
        address_df = address_df.unnest("address_country")
        address_df = address_df.rename(
            {"isocode": "address_country_isocode", "name": "address_country_name"}
        )

        df = df.join(geo_df, on="storeId", how="left")
        df = df.join(address_df, on="storeId", how="left")

        # Remove the original structured columns
        df = df.drop(["geoPoint", "address"])

        return df

    df = pl.read_json(json_file)
    df = flatten_df(df)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name=f"{brand}_stores")


def ingest_ica_stores(json_file: str, date: str):
    def flatten_df(df: pl.DataFrame) -> pl.DataFrame:
        # Flatten the address column by first createing a new dataframe with the unnested column
        address_df = df.select(["storeId", "address"])
        address_df = address_df.unnest("address").unnest("coordinates")
        cols = [col for col in address_df.columns if col != "storeId"]
        address_df = address_df.rename({col: f"address_{col}" for col in cols})

        # Flatten the mdsaFilters
        mdsa_df = df.select(["storeId", "mdsaFilters"])
        mdsa_df = mdsa_df.unnest("mdsaFilters")
        cols = [col for col in mdsa_df.columns if col != "storeId"]
        mdsa_df = mdsa_df.rename({col: f"mdsaFilters_{col}" for col in cols})

        df = df.join(address_df, on="storeId", how="left")
        df = df.join(mdsa_df, on="storeId", how="left")

        # Remove the original structured columns
        df = df.drop(["address", "mdsaFilters"])

        return df

    df = pl.read_json(json_file)
    df = df.drop(["openingHours", "urls"])
    df = flatten_df(df)

    scrapped_date = datetime.strptime(date, "%Y-%m-%d")
    df = df.with_columns((pl.lit(scrapped_date, dtype=pl.Date).alias("scrapped_date")))

    write_to_db(df, table_name="ica_stores")
