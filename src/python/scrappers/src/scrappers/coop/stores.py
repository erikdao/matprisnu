"""Coop stores scrapper."""
import json
import os
from pathlib import Path
from typing import Any, List, Optional

from dotenv import load_dotenv
from loguru import logger
from scrappers.common import make_url, random_user_agents
from scrappers.data_lake import AsyncDataLakeConnector
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders

load_dotenv(os.path.join(os.getcwd(), ".env"))

BASE_URL = "https://proxy.api.coop.se/external/store/stores/map"


async def scrape_stores() -> Optional[List[Any]]:
    params = {"conceptIds": "12,6,95", "invertFilter": "true", "api-version": "v2"}
    headers = {
        "User-Agent": random_user_agents(),
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("COOP_STORES_API_SUBSCRIPTION_KEY"),
    }
    url = BASE_URL

    request = HTTPRequest(url=make_url(url, params), headers=HTTPHeaders(headers))
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)


async def scrapping_function(storage_path: Path, **kwargs) -> None:
    """Stores scrapper function.

    Args:
        storage_path (Path): Path to store the scrapped data
    """
    stores = await scrape_stores()

    logger.info(f"Got {len(stores)} stores")
    file_path = storage_path / "stores.json"
    logger.info(f"Write data to {file_path}")
    with open(file_path, "w") as f:
        json.dump(stores, f, indent=2)

    logger.info("Saving scrapped data to data lake")
    await AsyncDataLakeConnector().save_to_data_lake(
        collection_name="stores", data=stores, brand_name="coop", id_field="storeId"
    )
