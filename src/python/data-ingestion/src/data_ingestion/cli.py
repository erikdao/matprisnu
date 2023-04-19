"""CLI interface for data ingestion."""
import importlib

import click


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


def main():
    cli = click.CommandCollection(sources=[stores_cli])
    cli()


if __name__ == "__main__":
    main()
