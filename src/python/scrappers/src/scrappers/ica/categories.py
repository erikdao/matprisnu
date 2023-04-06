"""ICA categories scrapper."""
import json
from pathlib import Path

from data_models import IcaAPIStore
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient

CATEGORIES_BY_STORE_URL = "https://handlaprivatkund.ica.se/stores/{accountNumber}/api/v1/catalog/categories?depth=4"


async def _scrape_func(url: str):
    response = await AsyncHTTPClient().fetch(url)
    data = json_decode(response.body)
    return data.get("entities", {}).get("categories")


async def scrapping_function(store: IcaAPIStore, storage_path: Path, **kwargs):
    # ICA API only work with stores whose online platform is OSP
    if store.onlinePlatform != "OSP":
        return

    url = CATEGORIES_BY_STORE_URL.format(accountNumber=store.accountNumber)
    logger.debug(url)
    categories = await _scrape_func(url=url)

    json_path = storage_path / f"{store.storeId}_categories.json"
    logger.debug(f"Writing {len(categories.items())} category items to {json_path}")
    with open(json_path, "w") as f:
        json.dump(categories, f, indent=2)

    logger.debug(
        f"Saving scrapped categories to data lake for store '{store.storeId} - {store.storeName}'"
    )
    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="categories",
        data=categories,
        brand_name="ica",
        id_field="id",
        ica_store_id=store.storeId,
        ica_store_account_number=store.accountNumber,
    )
