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


if __name__ == "__main__":
    cli = click.CommandCollection(sources=[stores_cli])
    cli()
