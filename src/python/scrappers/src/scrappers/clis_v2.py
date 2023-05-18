"""CLI interface for scrappers (v2)."""
import asyncio
import importlib

import click


@click.group()
def stores_cli():
    pass


@stores_cli.command("stores")
@click.argument("brand", type=str)