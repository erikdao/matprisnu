"""Scrapeprs for Coop's products."""
import asyncio
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from data_models.scrappers import CoopAPICategory
from scrappers.common import make_url, random_user_agents
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode, json_encode
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest
from tornado.httputil import HTTPHeaders

concurrency = 50
AsyncHTTPClient.configure(None, max_clients=concurrency)

BASE_URL = "https://external.api.coop.se/personalization/search/entities/by-attribute"
QUERY_PARAMS = {
    "api-version": "v1",
    "store": 251300,
    "groups": "CUSTOMER_PRIVATE",
    "device": "desktop",
    "direct": "false",
}
FACETS = [
    {
        "attributeName": "manufacturerName",
        "type": "distinct",
        "operator": "OR",
        "name": "brand",
        "selected": [],
    },
    {
        "attributeName": "filterLabels",
        "type": "distinct",
        "operator": "AND",
        "name": "environmentalLabels",
        "selected": [],
    },
    {
        "attributeName": "allergyFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "allergyFilters",
        "selected": [],
    },
    {
        "attributeName": "nutritionFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "nutritionFilters",
        "selected": [],
    },
    {
        "attributeName": "lifestyleFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "lifestyleFilters",
        "selected": [],
    },
]
ITEMS_TAKE = 48


def _build_request_payload(
    category_id: Optional[str] = None, take: Optional[int] = 48, skip: Optional[int] = 0
) -> Dict[str, Any]:
    """Builds POST request payload for Coop's product API."""
    custom_data = {"consent": True}
    attribute = {"name": "categoryIds", "value": category_id}
    results_options = {"skip": skip, "take": take, "sortBy": [], "facets": FACETS}

    return {
        "attribute": attribute,
        "customData": custom_data,
        "resultsOptions": results_options,
    }


async def get_products_data(
    category_id: str, take: Optional[int] = ITEMS_TAKE, skip: Optional[int] = 0
) -> Optional[Tuple[int, Any]]:
    """Get products data from Coop by invoking a POST request to Coop's API."""
    # Build the request
    headers = {
        "User-Agent": random_user_agents(),
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Ocp-Apim-Subscription-Key": os.getenv("COOP_PRODUCTS_API_SUBSCRIPTION_KEY"),
    }
    url = BASE_URL
    payload = _build_request_payload(category_id=category_id, take=take, skip=skip)

    request = HTTPRequest(
        url=make_url(url, QUERY_PARAMS),
        method="POST",
        headers=HTTPHeaders(headers),
        user_agent=headers["User-Agent"],
        body=json_encode(payload),
    )

    try:
        response = await AsyncHTTPClient().fetch(request)
        results = json_decode(response.body).get("results")
        return results["count"], results["items"]
    except HTTPClientError as e:
        logger.error(e)
        raise e


async def scrape_products(category_id: str) -> List[Any]:
    """Scrapes all products for a given category."""
    items_take = ITEMS_TAKE
    items_skip = 0

    data = []
    items_count, page_items = await get_products_data(
        category_id=category_id, take=items_take, skip=items_skip
    )
    data.extend(page_items)

    total_pages = math.ceil(items_count / items_take)
    logger.debug(
        f"Category {category_id}; items_count = {items_count}; total_pages = {total_pages}"
    )

    if total_pages > 1:
        results = await asyncio.gather(
            *[
                get_products_data(
                    category_id=category_id, take=items_take, skip=page * items_take
                )
                for page in range(1, total_pages)
            ]
        )
        for idx, res in enumerate(results):
            data.extend(res[-1])
        logger.debug(f"Got {len(data)} products for category {category_id}")

    return data


async def scrapping_function(category: CoopAPICategory, storage_path: Path) -> None:
    """Main scrapping function for aggregating category's products and write
    them to JSON files."""
    products = await scrape_products(category_id=str(category.id))
    logger.info(f"Scrapped {len(products)} products for category: {category}")

    if not len(products):
        return

    # Write to json
    json_file = storage_path / f"{category.escapedName}.json"
    with open(json_file, "w") as f:
        json.dump(products, f, indent=2)

    logger.info("Saving scrapped products to delta lake")
    await AsyncDataLakeConnector().save_to_data_lake(
        data=products,
        collection_name="products",
        brand_name="coop",
        id_field="id",
        brand_category=category.escapedName,
    )
