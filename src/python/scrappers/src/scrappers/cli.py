"""CLI-interface for scrappers."""
import asyncio
import importlib
import json
from pathlib import Path
from typing import Union

import click
from scrappers.common import init_storage_dir


@click.group()
def stores_cli():
    pass


@stores_cli.command("stores")
@click.argument("brand", type=str)
@click.option(
    "--output-path",
    type=click.Path(exists=True),
    default="data",
    help="Path to output directory",
)
def stores_command(brand: str, output_path: str):
    output_path = Path(output_path).resolve()

    if brand in ["willys", "hemkop"]:
        brand_name = "axfood"
    else:
        brand_name = brand
    module = importlib.import_module(f"scrappers.{brand_name}.stores")
    scrapping_function = getattr(module, "scrapping_function")

    storage_path = init_storage_dir(
        parent_path=output_path, dirname=brand, sub_dir="stores"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrapping_function(storage_path, brand=brand))


@click.group()
def categories_cli():
    pass


@categories_cli.command("categories")
@click.argument("brand", type=str)
@click.option(
    "--output-path",
    type=click.Path(exists=True),
    default="data",
    help="Path to output directory",
)
@click.option(
    "--stores-file",
    type=click.Path(exists=True),
    help="Path to stores directory",
)
@click.option(
    "--store-id",
    type=str,
    help="Store ID",
)
def categories_command(brand: str, output_path: str, stores_file: str, store_id: str):
    def run_ica(
        stores_file: Union[str, Path], store_id: str, storage_path: Union[str, Path]
    ):
        """Run ICA categories scrapping."""
        from data_models import IcaAPIStore

        with open(stores_file, "r") as f:
            stores = json.load(f)
        store = next(store for store in stores if store["storeId"] == store_id)
        store = IcaAPIStore.parse_obj(store)

        module = importlib.import_module("scrappers.ica.categories")
        scrapping_function = getattr(module, "scrapping_function")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(store, storage_path))

    def run_other(brand: str, storage_path: Union[str, Path]):
        """Run other brands categories scrapping."""
        if brand in ["willys", "hemkop"]:
            brand_name = "axfood"
        else:
            brand_name = brand
        module = importlib.import_module(f"scrappers.{brand_name}.categories")
        scrapping_function = getattr(module, "scrapping_function")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path, brand=brand))

    output_path = Path(output_path).resolve()
    storage_path = init_storage_dir(
        parent_path=output_path, dirname=brand, sub_dir="categories"
    )

    if brand == "ica":
        run_ica(stores_file, store_id, storage_path)
    else:
        run_other(brand, storage_path)


def main():
    cli = click.CommandCollection(sources=[stores_cli, categories_cli])
    cli()


if __name__ == "__main__":
    main()
