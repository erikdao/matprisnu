"""CLI-interface for scrappers."""
import asyncio
import importlib
from pathlib import Path

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

    storage_path = init_storage_dir(output_path, brand, "stores")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrapping_function(storage_path, brand=brand))


def main():
    cli = click.CommandCollection(sources=[stores_cli])
    cli()


if __name__ == "__main__":
    main()
