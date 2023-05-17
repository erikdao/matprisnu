"""CLI interface for data ingestion."""
import importlib
import os

import click
from loguru import logger


@click.group()
def stores_cli():
    pass


@stores_cli.command("stores")
@click.option("--brand", type=str, required=True)
@click.option("--json-file", type=str, required=True)
@click.option("--date", type=str, required=True)
def stores(brand: str, json_file: str, date: str):
    """Ingest stores."""
    if brand in ["hemkop", "willys"]:
        brand_name = "axfood"
    else:
        brand_name = brand
    module = importlib.import_module("data_ingestion.stores")
    ingest_function = getattr(module, f"ingest_{brand_name}_stores")

    if brand == "ica" or brand == "coop":
        ingest_function(json_file, date)
    elif brand == "hemkop" or brand == "willys":
        ingest_function(brand, json_file, date)


@click.group()
def categories_cli():
    pass


@categories_cli.command("categories")
@click.option("--brand", type=str, required=True)
@click.option("--json-path", type=str, required=False)
@click.option("--date", type=str, required=True)
def categories(brand: str, json_path: str, date: str):
    """Ingest categories."""
    if brand in ["hemkop", "willys"]:
        brand_name = "axfood"
    else:
        brand_name = brand
    module = importlib.import_module("data_ingestion.categories")
    ingest_function = getattr(module, f"ingest_{brand_name}_categories")

    if brand == "ica":
        # Get all json files in the directory
        json_files = [
            os.path.join(json_path, f)
            for f in os.listdir(json_path)
            if f.endswith(".json")
        ]
        for json_file in json_files:
            ingest_function(json_file=json_file, date=date)
    elif brand == "coop":
        ingest_function(json_file=json_path, date=date)
    elif brand == "hemkop" or brand == "willys":
        ingest_function(brand=brand, json_file=json_path, date=date)


@click.group()
def infer_schema_cli():
    pass


@infer_schema_cli.command("infer-schema")
@click.option("--brand", type=str, required=True)
@click.option("--json-path", type=str, required=True)
@click.option("--output-path", type=str, required=True)
def infer_schema(brand: str, json_path: str, output_path: str):
    module = importlib.import_module("data_ingestion.products.schemas")
    if brand == "ica":
        infer_function = ()
    else:
        infer_function = getattr(module, "infer_category_products_schema")

    input_categories = [
        fn.replace(".json", "") for fn in os.listdir(json_path) if fn.endswith(".json")
    ]
    for category in input_categories:
        input_file = os.path.join(json_path, category + ".json")
        output_file = os.path.join(output_path, category + ".json")
        infer_function(input_file, output_file)
        logger.info(f"Inferred product schema for {category}")


def main():
    cli = click.CommandCollection(
        sources=[stores_cli, categories_cli, infer_schema_cli]
    )
    cli()


if __name__ == "__main__":
    main()
