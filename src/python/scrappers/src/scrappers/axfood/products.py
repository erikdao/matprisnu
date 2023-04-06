"""Products for Axfood (Hemköp and Willys)."""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from data_models import AxfoodAPICategory
from scrappers.common import make_url
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient

BASE_URL = {
    "hemkop": "https://www.hemkop.se/c/",
    "willys": "https://www.willys.se/c/",
}


async def _scrape_product_func(url: str, payload: Dict[str, Any]) -> Tuple[int, Any]:
    response = await AsyncHTTPClient().fetch(make_url(url, payload))
    data = json_decode(response.body)

    results = data.get("results")
    number_of_pages = data.get("pagination", {}).get("numberOfPages")

    return number_of_pages, results


async def scrape_category(brand: str, category: str) -> List[Any]:
    """Scrape products for a category."""
    url = BASE_URL[brand] + category

    products = []

    # Scrape the first page to find the number of pages to be scrapped
    payload = {"size": 3000, "page": 0}
    number_of_pages, data = await _scrape_product_func(url, payload)
    products.extend(data)

    if number_of_pages > 1:
        tasks = []
        for p in range(1, number_of_pages):
            tasks.append(_scrape_product_func(url, payload={"size": 3000, "page": p}))

        # Scrape subsequent pages asynchronously
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for _, res in results:
            products.extend(res)

    return products


async def scrapping_function(
    brand: str, category: AxfoodAPICategory, storage_path: Path
):
    """Function to scrape products for a particular category."""
    category_id = category.url
    products = await scrape_category(brand, category_id)
    logger.info(f"Scrapped {len(products)} products for category. {category}")

    json_file = storage_path / f"{category_id}.json"
    with open(json_file, "w") as f:
        json.dump(products, f, indent=2)

    logger.info("Saving scrapped products to data lake")
    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="products",
        data=products,
        brand_name=brand,
        id_field="code",
        brand_category=category_id,
    )
