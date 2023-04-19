import pandas as pd
import polars as pl


def generate_coop_stores_create_sql(json_file: str) -> str:
    df = pl.read_json(json_file)
    df = df.to_pandas()

    table_name = "coop_stores"
    sql = pd.io.sql.get_schema(df, table_name, con=None)

    return sql


def generate_axfood_stores_create_sql(json_file: str, table_name: str) -> str:
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

        df = df.join(geo_df, on="storeId", how="left")
        df = df.join(address_df, on="storeId", how="left")

        # Remove the original structured columns
        df = df.drop(["geoPoint", "address"])

        return df

    def generate_sql(df: pl.DataFrame, table_name: str = "hemkop_stores") -> str:
        df = df.to_pandas()
        sql = pd.io.sql.get_schema(df, table_name, con=None)

        return sql

    df = pl.read_json(json_file)
    df = flatten_df(df)
    return generate_sql(df, table_name)


def generate_ica_stores_create_sql(json_file: str) -> str:
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

    def generate_sql(df: pl.DataFrame, table_name: str = "ica_stores") -> str:
        df = df.to_pandas()
        sql = pd.io.sql.get_schema(df, table_name, con=None)

        return sql

    df = pl.read_json(json_file)
    # CAUTION: pl.read_json() does not include the `distanceInMeters` column since it is null
    # for all rows. For now, it seems to be okay. But we might need to take further actions in the future.

    # Drop the `openingHours` column as we don't know how to process it
    df = df.drop(["openingHours", "urls"])

    df = flatten_df(df)
    return generate_sql(df)
