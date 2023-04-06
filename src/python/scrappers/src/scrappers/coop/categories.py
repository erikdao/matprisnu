"""Module to scrape product's Categories on Coop website.

It doesn't guarantee to be able to get all categories of products
provided by Coop as the website might be well-personalised to user's
session
"""
import json
from pathlib import Path
from typing import Any, List, Optional, Union

from data_models.scrappers import CoopAPICategory
from pydantic import parse_obj_as
from scrappers.common import random_user_agents
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders

BASE_URL = "https://www.coop.se/api/ecommerce/section/list"


def parse_obj_list(obj_list: List[Any]) -> List[CoopAPICategory]:
    """Parse categories from Coop API format into Category format."""
    categories = parse_obj_as(List[CoopAPICategory], obj_list)
    return categories


def get_categories_from_file(
    file: Union[Path, str], level: int = 3
) -> List[CoopAPICategory]:
    """Read categories from JSON file, parse them into Category format.

    By default, only return lowest (deepest) level category
    """
    with open(file, "r") as f:
        categories = json.load(f)

    if level:
        categories = [cat for cat in categories if cat["level"] == level]

    return parse_obj_list(categories)


async def scrape_categories() -> Optional[List[Any]]:
    headers = {
        "User-Agent": random_user_agents(),
        "Accept": "application/json",
    }

    url = BASE_URL

    request = HTTPRequest(url=url, headers=HTTPHeaders(headers))
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)


async def scrapping_function(storage_path: Path, **kwargs) -> None:
    categories = await scrape_categories()
    logger.info(f"Got {len(categories)} categories")

    file_path = storage_path / "categories.json"
    logger.info(f"Write data to {file_path}")
    with open(file_path, "w") as f:
        json.dump(categories, f, indent=2)

    logger.info("Saving scrapped data to data lake")
    await AsyncDataLakeConnector().save_to_data_lake(
        collection_name="categories", data=categories, brand_name="coop", id_field="id"
    )
