"""Categories for Axfood stores (Hemköp and Willys)."""
import json
from pathlib import Path
from typing import Any, List

from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient

CATEGORY_URL = {
    "hemkop": "https://www.hemkop.se/leftMenu/categorytree",
    "willys": "https://www.willys.se/leftMenu/categorytree",
}


async def _scrape_func(url) -> List[Any]:
    res = await AsyncHTTPClient().fetch(url)
    data = json_decode(res.body)
    return data.get("children", {})


async def scrapping_function(storage_path: Path, **kwargs) -> None:
    """Scrapping function for Axfood categories."""
    brand = kwargs.get("brand")
    categories = await _scrape_func(CATEGORY_URL[brand])
    logger.info(f"Got {len(categories)} categories")

    with open(storage_path / "categories.json", "w") as f:
        json.dump(categories, f, indent=2)

    logger.info("Saving scrapped data to data lake")
    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="categories",
        data=categories,
        brand_name=brand,
        id_field="id",
    )
