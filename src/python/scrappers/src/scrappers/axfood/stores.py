"""Axfood Store scrapper (Hemköp and Willys)."""
import json
from pathlib import Path
from typing import Any, List

from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPError

STORES_URL = {
    "hemkop": "https://www.hemkop.se/axfood/rest/store?online=false",
    "willys": "https://www.willys.se/axfood/rest/store?online=false",
}


async def _scrape_func(url) -> List[Any]:
    try:
        res = await AsyncHTTPClient().fetch(url)
        return json_decode(res.body)
    except HTTPError as e:
        logger.error(e)
        raise Exception(f"Error while scrapping stores from {url}")


def write_data_to_file(data: Any, storage_path: Path, file_name: str) -> None:
    with open(storage_path / file_name, "w") as f:
        json.dump(data, f, indent=2)


async def scrapping_function(storage_path: Path, **kwargs) -> None:
    brand = kwargs.get("brand")
    stores = await _scrape_func(STORES_URL[brand])

    write_data_to_file(stores, storage_path, "stores.json")

    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="stores", data=stores, brand_name="hemkop", id_field="storeId"
    )
