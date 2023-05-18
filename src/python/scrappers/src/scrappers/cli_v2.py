"""CLI interface for scrappers (v2)."""
import asyncio
import importlib

import click


@click.group()
def stores_cli():
    pass


@stores_cli.command("stores")
@click.argument("brand", type=str)
def stores_cmd(brand: str):
    """Scrape stores data."""
    module = importlib.import_module(f"scrappers.{brand}.stores")
    scrapping_function = getattr(module, "scrape_stores_flow")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrapping_function())


@click.group()
def categories_cli():
    pass


@categories_cli.command("categories")
@click.argument("brand", type=str)
def categories_cmd(brand: str):
    """Scrape categories data."""
    module = importlib.import_module(f"scrappers.{brand}.categories")
    scrapping_function = getattr(module, "scrape_categories_flow")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrapping_function())


@click.group()
def products_cli():
    pass


@products_cli.command("products")
@click.argument("brand", type=str)
@click.option("--category-file", type=str, help="Path to category file")
def products_cmd(brand: str, category_file: str):
    """Scrape products data."""
    module = importlib.import_module(f"scrappers.{brand}.products")
    scrapping_function = getattr(module, "scrape_products_flow")
    loop = asyncio.get_event_loop()

    if brand == "coop":
        module = importlib.import_module(f"scrappers.{brand}.categories")
        categories = module.get_categories_from_file(category_file, level=1)
        for category in categories:
            loop.run_until_complete(scrapping_function(category))


if __name__ == "__main__":
    cli = click.CommandCollection(sources=[categories_cli, products_cli, stores_cli])
    cli()
